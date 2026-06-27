from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import requests

from tailclose_desktop.models import HistoricalBar, StockQuote
from tailclose_desktop.providers.base import ProviderError


TUSHARE_API_URL = "https://api.tushare.pro"


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _compact_date(value: str | None) -> str | None:
    if value is None:
        return None
    return value.replace("-", "")


def _plain_code(ts_code: str) -> str:
    return ts_code.split(".", maxsplit=1)[0]


class TushareProvider:
    def __init__(
        self,
        token: str | None = None,
        session: Any | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.token = token or os.environ.get("TUSHARE_TOKEN")
        self.session = session or requests.Session()
        self.timeout = timeout

    def current_quotes(self) -> list[StockQuote]:
        names = self._stock_names()
        trade_date, daily_rows = self._latest_daily_rows()
        basic_rows = self._request_rows(
            "daily_basic",
            {"trade_date": trade_date},
            fields="ts_code,trade_date,turnover_rate,volume_ratio",
        )

        daily_by_code = {str(row.get("ts_code", "")): row for row in daily_rows}
        basic_by_code = {str(row.get("ts_code", "")): row for row in basic_rows}

        quotes: list[StockQuote] = []
        for ts_code, daily in daily_by_code.items():
            name = names.get(ts_code, "")
            basic = basic_by_code.get(ts_code, {})
            quotes.append(
                StockQuote(
                    code=_plain_code(ts_code),
                    name=name,
                    latest_price=_float_or_none(daily.get("close")),
                    change_percent=_float_or_none(daily.get("pct_chg")),
                    volume_ratio=_float_or_none(basic.get("volume_ratio")),
                    turnover_rate=_float_or_none(basic.get("turnover_rate")),
                    is_st="ST" in name.upper(),
                )
            )
        return quotes

    def historical_daily(
        self,
        code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[HistoricalBar]:
        ts_code = self._to_ts_code(code)
        rows = self._request_rows(
            "daily",
            {
                "ts_code": ts_code,
                "start_date": _compact_date(start_date),
                "end_date": _compact_date(end_date),
            },
            fields="ts_code,trade_date,open,close,pct_chg,vol",
        )
        bars = [
            HistoricalBar(
                date=self._display_date(str(row.get("trade_date", ""))),
                code=_plain_code(ts_code),
                close=float(row["close"]),
                open=_float_or_none(row.get("open")),
                volume=_float_or_none(row.get("vol")),
            )
            for row in rows
            if row.get("close") not in (None, "")
        ]
        return sorted(bars, key=lambda bar: bar.date)

    def _stock_names(self) -> dict[str, str]:
        rows = self._request_rows(
            "stock_basic",
            {"exchange": "", "list_status": "L"},
            fields="ts_code,name,market,list_status",
        )
        return {str(row.get("ts_code", "")): str(row.get("name", "")) for row in rows}

    def _latest_daily_rows(self) -> tuple[str, list[dict[str, Any]]]:
        today = date.today()
        for day_offset in range(10):
            trade_date = (today - timedelta(days=day_offset)).strftime("%Y%m%d")
            rows = self._request_rows(
                "daily",
                {"trade_date": trade_date},
                fields="ts_code,trade_date,open,close,pct_chg,vol",
            )
            if rows:
                return trade_date, rows
        raise ProviderError("Tushare daily 最近 10 天没有返回行情。")

    def _request_rows(
        self,
        api_name: str,
        params: dict[str, Any],
        fields: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.token:
            raise ProviderError("Tushare token 未设置，请先设置 TUSHARE_TOKEN。")

        payload = {
            "api_name": api_name,
            "token": self.token,
            "params": {key: value for key, value in params.items() if value not in (None, "")},
        }
        if fields:
            payload["fields"] = fields
        response = self.session.post(TUSHARE_API_URL, json=payload, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        if body.get("code") != 0:
            raise ProviderError(f"Tushare {api_name} failed: {body.get('msg', '')}")

        data = body.get("data") or {}
        fields = data.get("fields") or []
        items = data.get("items") or []
        return [dict(zip(fields, item, strict=False)) for item in items]

    @staticmethod
    def _to_ts_code(code: str) -> str:
        normalized = code.upper()
        if normalized.endswith((".SH", ".SZ", ".BJ")):
            return normalized
        if normalized.startswith(("600", "601", "603", "605", "688")):
            return f"{normalized}.SH"
        if normalized.startswith(("8", "9", "4")):
            return f"{normalized}.BJ"
        return f"{normalized}.SZ"

    @staticmethod
    def _display_date(compact_date: str) -> str:
        if len(compact_date) == 8:
            return f"{compact_date[:4]}-{compact_date[4:6]}-{compact_date[6:]}"
        return compact_date
