from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def summarize_backtest(signals: Sequence[Any]) -> dict[str, Any]:
    return {
        "signal_count": len(signals),
        "available": False,
        "message": "历史行情不足，暂无法生成回测结果。",
        "signals": signals,
    }
