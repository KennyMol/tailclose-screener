from tailclose_desktop.models import HistoricalBar, StockQuote
from tailclose_desktop.strategy import (
    default_tailclose_strategy,
    screen_custom_tailclose_candidates,
    screen_quotes,
)


def base_quote(**overrides):
    data = {
        "code": "600000",
        "name": "浦发银行",
        "latest_price": 10.2,
        "change_percent": 2.1,
        "volume_ratio": 1.8,
        "turnover_rate": 3.2,
        "is_st": False,
        "is_suspended": False,
        "is_delisting_risk": False,
        "moving_averages": {"ma5": 10.0, "ma10": 9.9, "ma20": 9.7},
        "late_session_active": True,
    }
    data.update(overrides)
    return StockQuote(**data)


def test_default_strategy_includes_matching_quote():
    results = screen_quotes([base_quote()], default_tailclose_strategy())
    assert len(results) == 1
    assert results[0].code == "600000"
    assert "涨幅在 0% 到 6%" in results[0].reasons
    assert "量比大于 1.2" in results[0].reasons


def test_default_strategy_excludes_out_of_range_change_percent():
    results = screen_quotes([base_quote(change_percent=8.1)], default_tailclose_strategy())
    assert results == []


def test_default_strategy_excludes_risk_flags():
    quotes = [
        base_quote(code="600001", is_st=True),
        base_quote(code="600002", is_suspended=True),
        base_quote(code="600003", is_delisting_risk=True),
    ]
    assert screen_quotes(quotes, default_tailclose_strategy()) == []


def test_quotes_without_positive_reason_are_excluded():
    quote = StockQuote(code="600004", name="空数据")
    assert screen_quotes([quote], default_tailclose_strategy()) == []


def test_results_are_sorted_by_score_descending():
    low = base_quote(code="600010", volume_ratio=1.3, late_session_active=False)
    high = base_quote(code="600011", volume_ratio=2.6, late_session_active=True)
    results = screen_quotes([low, high], default_tailclose_strategy())
    assert [item.code for item in results] == ["600011", "600010"]


def history_bars():
    return [
        HistoricalBar(date="2026-06-19", code="sh.600000", open=10.0, close=10.0, volume=1000),
        HistoricalBar(date="2026-06-22", code="sh.600000", open=10.0, close=10.5, volume=1200),
        HistoricalBar(date="2026-06-23", code="sh.600000", open=10.5, close=10.8, volume=1300),
        HistoricalBar(date="2026-06-24", code="sh.600000", open=10.8, close=11.86, volume=1500),
        HistoricalBar(date="2026-06-25", code="sh.600000", open=11.7, close=12.0, volume=1800),
        HistoricalBar(date="2026-06-26", code="sh.600000", open=12.0, close=12.6, volume=2200),
    ]


def custom_quote(**overrides):
    data = {
        "code": "600000",
        "name": "浦发银行",
        "latest_price": 12.6,
        "change_percent": 5.0,
        "volume_ratio": 1.5,
        "turnover_rate": 10.0,
        "is_st": False,
        "is_suspended": False,
        "is_delisting_risk": False,
    }
    data.update(overrides)
    return StockQuote(**data)


def test_custom_tailclose_strategy_includes_quote_matching_all_rules():
    results = screen_custom_tailclose_candidates([(custom_quote(), history_bars())])

    assert len(results) == 1
    assert results[0].code == "600000"
    assert "主板" in results[0].reasons
    assert "换手率 8% 到 16%" in results[0].reasons
    assert "最近三个交易日有涨停" in results[0].reasons
    assert "量价齐升" in results[0].reasons


def test_custom_tailclose_strategy_rejects_non_main_board_codes():
    assert screen_custom_tailclose_candidates([(custom_quote(code="300001"), history_bars())]) == []
    assert screen_custom_tailclose_candidates([(custom_quote(code="688001"), history_bars())]) == []
    assert screen_custom_tailclose_candidates([(custom_quote(code="bj920000"), history_bars())]) == []


def test_custom_tailclose_strategy_rejects_realtime_threshold_misses():
    quotes = [
        custom_quote(code="600001", turnover_rate=8.0),
        custom_quote(code="600002", turnover_rate=16.0),
        custom_quote(code="600003", change_percent=3.5),
        custom_quote(code="600004", change_percent=6.5),
        custom_quote(code="600005", volume_ratio=1.0),
        custom_quote(code="600006", volume_ratio=2.0),
        custom_quote(code="600007", is_st=True),
    ]

    assert screen_custom_tailclose_candidates([(quote, history_bars()) for quote in quotes]) == []


def test_custom_tailclose_strategy_rejects_history_rule_misses():
    below_ma5 = [
        *history_bars()[:-1],
        HistoricalBar(date="2026-06-26", code="sh.600000", open=9.7, close=9.8, volume=2200),
    ]
    negative_candle = [
        *history_bars()[:-1],
        HistoricalBar(date="2026-06-26", code="sh.600000", open=12.8, close=12.6, volume=2200),
    ]
    no_limit_up = [
        HistoricalBar(date="2026-06-19", code="sh.600000", open=10.0, close=10.0, volume=1000),
        HistoricalBar(date="2026-06-22", code="sh.600000", open=10.0, close=10.5, volume=1200),
        HistoricalBar(date="2026-06-23", code="sh.600000", open=10.5, close=10.8, volume=1300),
        HistoricalBar(date="2026-06-24", code="sh.600000", open=10.8, close=11.0, volume=1500),
        HistoricalBar(date="2026-06-25", code="sh.600000", open=11.0, close=11.2, volume=1800),
        HistoricalBar(date="2026-06-26", code="sh.600000", open=11.2, close=11.4, volume=2200),
    ]
    falling_volume = [
        *history_bars()[:-1],
        HistoricalBar(date="2026-06-26", code="sh.600000", open=12.0, close=12.6, volume=1700),
    ]

    assert screen_custom_tailclose_candidates([(custom_quote(), below_ma5)]) == []
    assert screen_custom_tailclose_candidates([(custom_quote(), negative_candle)]) == []
    assert screen_custom_tailclose_candidates([(custom_quote(), no_limit_up)]) == []
    assert screen_custom_tailclose_candidates([(custom_quote(), falling_volume)]) == []
