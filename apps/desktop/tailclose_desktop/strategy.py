from __future__ import annotations

from collections.abc import Iterable

from tailclose_desktop.models import NumericCondition, ScreenResult, StockQuote, Strategy


def default_strategy() -> Strategy:
    return Strategy(
        change_pct=NumericCondition(min_value=0, max_value=6),
        volume_ratio=NumericCondition(min_value=1.2),
        turnover_rate=NumericCondition(min_value=1, max_value=12),
        exclude_st=True,
        exclude_suspended=True,
        exclude_delisting_risk=True,
        require_ma_alignment=True,
    )


def screen_quotes(
    quotes: Iterable[StockQuote], strategy: Strategy | None = None
) -> list[ScreenResult]:
    active_strategy = strategy or default_strategy()
    results = []

    for quote in quotes:
        positive_reasons = _positive_reasons(quote, active_strategy)
        if not positive_reasons:
            continue

        score = float(len(positive_reasons))
        results.append(
            ScreenResult(
                quote=quote,
                score=score,
                positive_reasons=positive_reasons,
            )
        )

    return sorted(results, key=lambda result: result.score, reverse=True)


def _positive_reasons(quote: StockQuote, strategy: Strategy) -> list[str]:
    if strategy.exclude_st and quote.is_st:
        return []
    if strategy.exclude_suspended and quote.is_suspended:
        return []
    if strategy.exclude_delisting_risk and quote.has_delisting_risk:
        return []

    if not strategy.change_pct.matches(quote.change_pct):
        return []
    if not strategy.volume_ratio.matches(quote.volume_ratio):
        return []
    if not strategy.turnover_rate.matches(quote.turnover_rate):
        return []

    reasons = []
    if strategy.require_ma_alignment:
        reasons.extend(_moving_average_reasons(quote))
    else:
        reasons.extend(
            [
                "change pct in range",
                "volume ratio above threshold",
                "turnover rate in range",
            ]
        )

    return reasons


def _moving_average_reasons(quote: StockQuote) -> list[str]:
    reasons = []
    price = quote.close_price if quote.close_price is not None else quote.price
    if price is None:
        return reasons

    moving_averages = [
        ("ma5", quote.ma5),
        ("ma10", quote.ma10),
        ("ma20", quote.ma20),
    ]

    for label, value in moving_averages:
        if value is not None and price > value:
            reasons.append(f"price above {label}")

    return reasons
