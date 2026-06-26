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


def test_akshare_provider_wraps_errors():
    def fail():
        raise RuntimeError("network down")

    provider = AkShareProvider(ak=types.SimpleNamespace(stock_zh_a_spot_em=fail))

    with pytest.raises(ProviderError, match="AkShare"):
        provider.current_quotes()


def test_baostock_provider_returns_historical_daily_bars():
    fake_baostock = types.SimpleNamespace(
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


def test_baostock_provider_wraps_errors():
    def fail(*args, **kwargs):
        raise RuntimeError("baostock failed")

    provider = BaoStockProvider(bs=types.SimpleNamespace(query_history_k_data_plus=fail))

    with pytest.raises(ProviderError, match="BaoStock"):
        provider.historical_daily("sh.600000")
