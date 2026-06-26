from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StockQuote:
    code: str
    name: str
    latest_price: float | None = None
    change_percent: float | None = None
    volume_ratio: float | None = None
    turnover_rate: float | None = None
    is_st: bool = False
    is_suspended: bool = False
    is_delisting_risk: bool = False
    moving_averages: dict[str, float] = field(default_factory=dict)
    late_session_active: bool = False


@dataclass(frozen=True)
class NumericCondition:
    field: str
    label: str
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class Strategy:
    id: str
    name: str
    numeric_conditions: list[NumericCondition]
    exclude_flags: tuple[str, ...]
    require_moving_average: bool = True
    require_late_session_active: bool = False


@dataclass(frozen=True)
class ScreenResult:
    code: str
    name: str
    latest_price: float | None
    change_percent: float | None
    volume_ratio: float | None
    reasons: list[str]
    score: float


@dataclass(frozen=True)
class HistoricalBar:
    date: str
    code: str
    close: float
