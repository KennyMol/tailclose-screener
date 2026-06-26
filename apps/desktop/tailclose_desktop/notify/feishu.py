from __future__ import annotations

from collections.abc import Sequence

import requests

from tailclose_desktop.models import ScreenResult

DISCLAIMER = "仅供策略筛选和观察，不构成投资建议。"


def _format_optional_number(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "-"
    return f"{value:g}{suffix}"


def format_feishu_message(
    strategy_name: str,
    results: Sequence[ScreenResult],
    webhook_url: str | None = None,
) -> str:
    lines = [
        f"策略：{strategy_name}",
        "筛选结果：",
    ]

    if not results:
        lines.append("当前没有符合条件的股票。")
    else:
        for index, result in enumerate(results, start=1):
            reasons = "；".join(result.reasons) if result.reasons else "-"
            lines.append(
                f"{index}. {result.code} {result.name} | "
                f"最新价：{_format_optional_number(result.latest_price)} | "
                f"涨跌幅：{_format_optional_number(result.change_percent, '%')} | "
                f"量比：{_format_optional_number(result.volume_ratio)} | "
                f"评分：{_format_optional_number(result.score)} | "
                f"原因：{reasons}"
            )

    lines.append(DISCLAIMER)
    return "\n".join(lines)


def send_feishu_text(webhook_url: str, text: str, timeout: float = 5.0):
    response = requests.post(
        webhook_url,
        json={"msg_type": "text", "content": {"text": text}},
        timeout=timeout,
    )
    response.raise_for_status()
    return response
