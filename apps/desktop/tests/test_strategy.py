from tailclose_desktop.models import StockQuote
from tailclose_desktop.strategy import default_tailclose_strategy, screen_quotes


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
