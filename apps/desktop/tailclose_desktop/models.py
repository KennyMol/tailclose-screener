from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StockQuote:
    code: str
    name: str
    change_pct: float
    volume_ratio: float
    turnover_rate: float
    price: float | None = None
    is_st: bool = False
    is_suspended: bool = False
    has_delisting_risk: bool = False
    close_price: float | None = None
    ma5: float | None = None
    ma10: float | None = None
    ma20: float | None = None


@dataclass(frozen=True)
class HistoricalBar:
    date: str
    code: str
    close: float


@dataclass(frozen=True)
class NumericCondition:
    min_value: float | None = None
    max_value: float | None = None

    def matches(self, value: float) -> bool:
        if self.min_value is not None:
            if self.max_value is None:
                if value <= self.min_value:
                    return False
            elif value < self.min_value:
                return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True


@dataclass(frozen=True)
class Strategy:
    change_pct: NumericCondition
    volume_ratio: NumericCondition
    turnover_rate: NumericCondition
    exclude_st: bool = True
    exclude_suspended: bool = True
    exclude_delisting_risk: bool = True
    require_ma_alignment: bool = True


@dataclass(frozen=True)
class ScreenResult:
    quote: StockQuote
    score: float
    positive_reasons: list[str] = field(default_factory=list)
