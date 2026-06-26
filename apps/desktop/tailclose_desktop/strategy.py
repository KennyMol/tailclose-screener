from __future__ import annotations

from collections.abc import Iterable

from .models import NumericCondition, ScreenResult, StockQuote, Strategy


def default_tailclose_strategy() -> Strategy:
    return Strategy(
        id="tail-close-default",
        name="默认尾盘买入法",
        numeric_conditions=[
            NumericCondition("change_percent", "涨幅在 0% 到 6%", 0, 6),
            NumericCondition("volume_ratio", "量比大于 1.2", 1.2, None),
            NumericCondition("turnover_rate", "换手率适中", 1, 12),
        ],
        exclude_flags=("is_st", "is_suspended", "is_delisting_risk"),
    )


def _passes_numeric(quote: StockQuote, condition: NumericCondition) -> bool:
    value = getattr(quote, condition.field)
    if value is None:
        return True
    if condition.minimum is not None and value < condition.minimum:
        return False
    if condition.maximum is not None and value > condition.maximum:
        return False
    return True


def _above_any_moving_average(quote: StockQuote) -> bool:
    if quote.latest_price is None or not quote.moving_averages:
        return True
    return any(quote.latest_price >= value for value in quote.moving_averages.values())


def screen_quotes(quotes: Iterable[StockQuote], strategy: Strategy) -> list[ScreenResult]:
    results: list[ScreenResult] = []
    for quote in quotes:
        if any(getattr(quote, flag) for flag in strategy.exclude_flags):
            continue

        reasons: list[str] = []
        rejected = False
        for condition in strategy.numeric_conditions:
            if not _passes_numeric(quote, condition):
                rejected = True
                break
            if getattr(quote, condition.field) is not None:
                reasons.append(condition.label)
        if rejected:
            continue

        if strategy.require_moving_average and not _above_any_moving_average(quote):
            continue
        if quote.latest_price is not None and quote.moving_averages:
            reasons.append("价格在均线上方")

        if strategy.require_late_session_active and not quote.late_session_active:
            continue
        if quote.late_session_active:
            reasons.append("尾盘成交活跃")

        if not reasons:
            continue

        results.append(
            ScreenResult(
                code=quote.code,
                name=quote.name,
                latest_price=quote.latest_price,
                change_percent=quote.change_percent,
                volume_ratio=quote.volume_ratio,
                reasons=reasons,
                score=len(reasons) * 10 + (quote.volume_ratio or 0),
            )
        )
    return sorted(results, key=lambda item: item.score, reverse=True)
