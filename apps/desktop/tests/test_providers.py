import types

import pytest

from tailclose_desktop.models import HistoricalBar, StockQuote
from tailclose_desktop.providers.akshare_provider import (
    AkShareProvider,
    normalize_akshare_row,
)
from tailclose_desktop.providers.baostock_provider import BaoStockProvider
from tailclose_desktop.providers.base import ProviderError, QuoteProvider
from tailclose_desktop.providers.sample import SampleProvider
from tailclose_desktop.providers.tushare_provider import TushareProvider


def test_sample_provider_returns_deterministic_matching_a_share_quotes():
    provider: QuoteProvider = SampleProvider()

    quotes = provider.current_quotes()

    assert [quote.code for quote in quotes[:2]] == ["600000", "000001"]
    assert all(isinstance(quote, StockQuote) for quote in quotes)
    first = quotes[0]
    assert first.name == "浦发银行"
    assert first.latest_price == pytest.approx(8.8)
    assert first.change_percent == pytest.approx(2.1)
    assert first.volume_ratio == pytest.approx(1.8)
    assert first.turnover_rate == pytest.approx(3.2)
    assert first.is_st is False


def test_normalize_akshare_row_maps_eastmoney_fields_and_detects_st():
    row = {
        "代码": "600000",
        "名称": "ST浦发",
        "最新价": 8.72,
        "涨跌幅": -1.23,
        "量比": 2.4,
        "换手率": 4.5,
    }

    quote = normalize_akshare_row(row)

    assert quote == StockQuote(
        code="600000",
        name="ST浦发",
        latest_price=8.72,
        change_percent=-1.23,
        volume_ratio=2.4,
        turnover_rate=4.5,
        is_st=True,
    )


def test_normalize_akshare_row_tolerates_dirty_optional_numbers():
    quote = normalize_akshare_row({"代码": "600001", "名称": "空值", "最新价": "-", "涨跌幅": ""})

    assert quote.code == "600001"
    assert quote.name == "空值"
    assert quote.latest_price is None
    assert quote.change_percent is None
    assert quote.volume_ratio is None
    assert quote.turnover_rate is None


def test_akshare_provider_converts_spot_rows():
    fake_akshare = types.SimpleNamespace(
        stock_zh_a_spot_em=lambda: [
            {
                "代码": "600000",
                "名称": "浦发银行",
                "最新价": 8.72,
                "涨跌幅": 1.23,
                "量比": 2.4,
                "换手率": 4.5,
            }
        ]
    )

    quotes = AkShareProvider(ak=fake_akshare).current_quotes()

    assert quotes == [
        StockQuote(
            code="600000",
            name="浦发银行",
            latest_price=8.72,
            change_percent=1.23,
            volume_ratio=2.4,
            turnover_rate=4.5,
            is_st=False,
        )
    ]


def test_akshare_provider_falls_back_to_legacy_spot_when_em_fails():
    fake_akshare = types.SimpleNamespace(
        stock_zh_a_spot_em=lambda: (_ for _ in ()).throw(RuntimeError("em failed")),
        stock_zh_a_spot=lambda: [
            {
                "代码": "600000",
                "名称": "浦发银行",
                "最新价": 8.72,
                "涨跌幅": 1.23,
            }
        ],
    )

    quotes = AkShareProvider(ak=fake_akshare).current_quotes()

    assert quotes[0].code == "600000"
    assert quotes[0].latest_price == pytest.approx(8.72)


def test_akshare_provider_wraps_errors():
    def fail():
        raise RuntimeError("network down")

    provider = AkShareProvider(ak=types.SimpleNamespace(stock_zh_a_spot_em=fail))

    with pytest.raises(ProviderError, match="network down"):
        provider.current_quotes()


def test_baostock_provider_returns_historical_daily_bars():
    calls = []

    def login():
        calls.append("login")
        return types.SimpleNamespace(error_code="0", error_msg="")

    def logout():
        calls.append("logout")

    fake_baostock = types.SimpleNamespace(
        login=login,
        logout=logout,
        query_history_k_data_plus=lambda *args, **kwargs: [
            {"date": "2026-06-25", "code": "sh.600000", "close": "8.70"},
            {"date": "2026-06-26", "code": "sh.600000", "close": "8.80"},
        ]
    )

    bars = BaoStockProvider(bs=fake_baostock).historical_daily(
        "sh.600000",
        start_date="2026-06-25",
        end_date="2026-06-26",
    )

    assert bars == [
        HistoricalBar(date="2026-06-25", code="sh.600000", close=8.7),
        HistoricalBar(date="2026-06-26", code="sh.600000", close=8.8),
    ]
    assert calls == ["login", "logout"]


def test_baostock_provider_raises_when_login_fails():
    fake_baostock = types.SimpleNamespace(
        login=lambda: types.SimpleNamespace(error_code="1", error_msg="bad token"),
        logout=lambda: None,
    )

    with pytest.raises(ProviderError, match="登录失败"):
        BaoStockProvider(bs=fake_baostock).historical_daily("sh.600000")


def test_baostock_provider_wraps_errors():
    def fail(*args, **kwargs):
        raise RuntimeError("baostock failed")

    provider = BaoStockProvider(bs=types.SimpleNamespace(query_history_k_data_plus=fail))

    with pytest.raises(ProviderError, match="BaoStock"):
        provider.historical_daily("sh.600000")


class FakeTushareResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeTushareSession:
    def __init__(self):
        self.requests = []

    def post(self, url, json, timeout):
        self.requests.append(json)
        api_name = json["api_name"]
        if api_name == "stock_basic":
            return FakeTushareResponse(
                {
                    "code": 0,
                    "msg": "",
                    "data": {
                        "fields": ["ts_code", "name", "market", "list_status"],
                        "items": [["600000.SH", "浦发银行", "主板", "L"]],
                    },
                }
            )
        if api_name == "daily":
            if json["params"].get("trade_date") == "20260627":
                return FakeTushareResponse(
                    {
                        "code": 0,
                        "msg": "",
                        "data": {
                            "fields": ["ts_code", "trade_date", "open", "close", "pct_chg", "vol"],
                            "items": [],
                        },
                    }
                )
            return FakeTushareResponse(
                {
                    "code": 0,
                    "msg": "",
                    "data": {
                        "fields": ["ts_code", "trade_date", "open", "close", "pct_chg", "vol"],
                        "items": [["600000.SH", "20260626", 12.0, 12.6, 5.0, 2200.0]],
                    },
                }
            )
        if api_name == "daily_basic":
            return FakeTushareResponse(
                {
                    "code": 0,
                    "msg": "",
                    "data": {
                        "fields": ["ts_code", "trade_date", "turnover_rate", "volume_ratio"],
                        "items": [["600000.SH", "20260626", 10.0, 1.5]],
                    },
                }
            )
        raise AssertionError(f"unexpected api {api_name}")


def test_tushare_provider_builds_quotes_from_daily_basic_and_daily():
    session = FakeTushareSession()
    provider = TushareProvider(token="token", session=session)

    quotes = provider.current_quotes()

    assert quotes == [
        StockQuote(
            code="600000",
            name="浦发银行",
            latest_price=12.6,
            change_percent=5.0,
            volume_ratio=1.5,
            turnover_rate=10.0,
            is_st=False,
        )
    ]
    assert {request["api_name"] for request in session.requests} == {
        "stock_basic",
        "daily",
        "daily_basic",
    }
    daily_request = next(request for request in session.requests if request["api_name"] == "daily")
    assert daily_request["params"]["trade_date"] == "20260627"


def test_tushare_provider_tries_previous_day_when_latest_day_has_no_daily_rows(monkeypatch):
    class WeekendSession(FakeTushareSession):
        def post(self, url, json, timeout):
            if json["api_name"] == "daily" and json["params"].get("trade_date") == "20260627":
                self.requests.append(json)
                return FakeTushareResponse(
                    {"code": 0, "msg": "", "data": {"fields": ["ts_code"], "items": []}}
                )
            return super().post(url, json, timeout)

    class FixedDate:
        @classmethod
        def today(cls):
            from datetime import date

            return date(2026, 6, 27)

    import tailclose_desktop.providers.tushare_provider as provider_module

    monkeypatch.setattr(provider_module, "date", FixedDate)
    session = WeekendSession()

    quotes = TushareProvider(token="token", session=session).current_quotes()

    assert quotes[0].code == "600000"
    daily_dates = [
        request["params"]["trade_date"]
        for request in session.requests
        if request["api_name"] == "daily" and "trade_date" in request["params"]
    ]
    assert daily_dates[:2] == ["20260627", "20260626"]


def test_tushare_provider_reports_permission_errors():
    class PermissionDeniedSession:
        def post(self, url, json, timeout):
            return FakeTushareResponse(
                {
                    "code": -2001,
                    "msg": "抱歉，您没有接口(daily)访问权限",
                    "data": {"fields": [], "items": []},
                }
            )

    with pytest.raises(ProviderError, match="没有接口"):
        TushareProvider(token="token", session=PermissionDeniedSession()).current_quotes()


def test_tushare_provider_requires_token(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)

    with pytest.raises(ProviderError, match="TUSHARE_TOKEN"):
        TushareProvider(session=FakeTushareSession()).current_quotes()


def test_tushare_provider_returns_historical_daily_bars():
    provider = TushareProvider(token="token", session=FakeTushareSession())

    bars = provider.historical_daily("600000", start_date="2026-06-20", end_date="2026-06-26")

    assert bars == [
        HistoricalBar(date="2026-06-26", code="600000", close=12.6, open=12.0, volume=2200.0)
    ]
