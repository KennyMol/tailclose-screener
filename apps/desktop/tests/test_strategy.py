from tailclose_desktop.models import NumericCondition, StockQuote, Strategy
from tailclose_desktop.strategy import default_strategy, screen_quotes


def quote(**overrides):
    base = {
        "code": "600000",
        "name": "Sample Bank",
        "change_pct": 3.0,
        "volume_ratio": 1.8,
        "turnover_rate": 5.0,
        "is_st": False,
        "is_suspended": False,
        "has_delisting_risk": False,
        "close_price": 10.0,
        "ma5": 9.8,
        "ma10": 9.5,
        "ma20": 9.0,
    }
    base.update(overrides)
    return StockQuote(**base)


def test_numeric_condition_supports_open_ended_and_closed_ranges():
    assert NumericCondition(min_value=0, max_value=6).matches(0)
    assert NumericCondition(min_value=0, max_value=6).matches(6)
    assert not NumericCondition(min_value=0, max_value=6).matches(-0.01)
    assert not NumericCondition(min_value=0, max_value=6).matches(6.01)

    assert NumericCondition(min_value=1.2).matches(1.21)
    assert not NumericCondition(min_value=1.2).matches(1.2)


def test_default_strategy_screens_quotes_and_explains_positive_reasons():
    results = screen_quotes(
        [
            quote(code="600001", name="GoodCo"),
            quote(code="600002", name="NoMomentum", close_price=8.0),
            quote(code="600003", name="ST Bad", is_st=True),
            quote(code="600004", name="Suspended", is_suspended=True),
            quote(code="600005", name="Risky", has_delisting_risk=True),
            quote(code="600006", name="TooHot", change_pct=6.1),
            quote(code="600007", name="QuietVolume", volume_ratio=1.2),
            quote(code="600008", name="NoTurnover", turnover_rate=0.9),
        ]
    )

    assert [result.quote.code for result in results] == ["600001"]
    assert results[0].score > 0
    assert "price above ma5" in results[0].positive_reasons
    assert "price above ma10" in results[0].positive_reasons
    assert "price above ma20" in results[0].positive_reasons


def test_screen_quotes_returns_results_sorted_by_score_descending():
    results = screen_quotes(
        [
            quote(code="LOW", close_price=10.1, ma5=10.0, ma10=11.0, ma20=12.0),
            quote(code="HIGH", close_price=12.0, ma5=11.0, ma10=10.0, ma20=9.0),
        ]
    )

    assert [result.quote.code for result in results] == ["HIGH", "LOW"]
    assert results[0].score > results[1].score


def test_screen_quotes_accepts_custom_strategy():
    strategy = Strategy(
        change_pct=NumericCondition(min_value=-2, max_value=2),
        volume_ratio=NumericCondition(min_value=1.0),
        turnover_rate=NumericCondition(min_value=0.5, max_value=20),
        require_ma_alignment=False,
    )

    results = screen_quotes(
        [
            quote(code="CUSTOM", change_pct=-1.0, volume_ratio=1.1, turnover_rate=0.6),
            quote(code="DEFAULT_ONLY", change_pct=3.0),
        ],
        strategy=strategy,
    )

    assert [result.quote.code for result in results] == ["CUSTOM"]
    assert "change pct in range" in results[0].positive_reasons


def test_default_strategy_documents_planned_thresholds():
    strategy = default_strategy()

    assert strategy.change_pct == NumericCondition(min_value=0, max_value=6)
    assert strategy.volume_ratio == NumericCondition(min_value=1.2)
    assert strategy.turnover_rate == NumericCondition(min_value=1, max_value=12)
    assert strategy.exclude_st is True
    assert strategy.exclude_suspended is True
    assert strategy.exclude_delisting_risk is True
    assert strategy.require_ma_alignment is True
