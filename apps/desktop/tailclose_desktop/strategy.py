from __future__ import annotations

from collections.abc import Iterable

from .models import HistoricalBar, NumericCondition, ScreenResult, StockQuote, Strategy


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


def screen_custom_tailclose_candidates(
    candidates: Iterable[tuple[StockQuote, list[HistoricalBar]]],
) -> list[ScreenResult]:
    results: list[ScreenResult] = []
    for quote, bars in candidates:
        reasons = _custom_realtime_reasons(quote)
        if not reasons:
            continue

        history_reasons = _custom_history_reasons(bars)
        if not history_reasons:
            continue

        results.append(
            ScreenResult(
                code=quote.code,
                name=quote.name,
                latest_price=quote.latest_price,
                change_percent=quote.change_percent,
                volume_ratio=quote.volume_ratio,
                reasons=[*reasons, *history_reasons],
                score=len(reasons) * 10 + len(history_reasons) * 20 + (quote.volume_ratio or 0),
            )
        )
    return sorted(results, key=lambda item: item.score, reverse=True)


def passes_custom_realtime_rules(quote: StockQuote) -> bool:
    return bool(_custom_realtime_reasons(quote))


def _custom_realtime_reasons(quote: StockQuote) -> list[str]:
    if not _is_main_board_code(quote.code):
        return []
    if quote.is_st or quote.is_suspended or quote.is_delisting_risk:
        return []
    if quote.turnover_rate is None or not (8 < quote.turnover_rate < 16):
        return []
    if quote.change_percent is None or not (3.5 < quote.change_percent < 6.5):
        return []
    if quote.volume_ratio is None or not (1 < quote.volume_ratio < 2):
        return []
    return [
        "主板",
        "非 ST",
        "换手率 8% 到 16%",
        "涨幅 3.5% 到 6.5%",
        "量比 1 到 2",
    ]


def _is_main_board_code(code: str) -> bool:
    normalized = code.lower()
    if normalized.startswith(("sh.", "sz.")):
        normalized = normalized[3:]
    return normalized.startswith(("600", "601", "603", "605", "000", "001", "002"))


def _custom_history_reasons(bars: list[HistoricalBar]) -> list[str]:
    ordered = sorted(bars, key=lambda bar: bar.date)
    if len(ordered) < 6:
        return []

    today = ordered[-1]
    previous = ordered[-2]
    last_five = ordered[-5:]
    closes = [bar.close for bar in last_five]
    ma5 = sum(closes) / len(closes)

    if today.close <= ma5:
        return []
    if today.open is None or today.close <= today.open:
        return []
    if not _has_recent_limit_up(ordered):
        return []
    if today.volume is None or previous.volume is None or today.volume <= previous.volume:
        return []
    if today.close <= previous.close:
        return []

    return ["5日均线之上", "阳线", "最近三个交易日有涨停", "量价齐升"]


def _has_recent_limit_up(bars: list[HistoricalBar]) -> bool:
    for previous, current in zip(bars[-4:-1], bars[-3:], strict=False):
        if previous.close <= 0:
            continue
        if (current.close - previous.close) / previous.close * 100 >= 9.8:
            return True
    return False
