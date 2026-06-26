from collections.abc import Iterable, Mapping
from typing import Any

from tailclose_desktop.models import HistoricalBar
from tailclose_desktop.providers.base import ProviderError


class BaoStockProvider:
    def __init__(self, bs: Any | None = None) -> None:
        self._bs = bs

    def historical_daily(
        self,
        code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[HistoricalBar]:
        try:
            bs = self._bs
            if bs is None:
                import baostock as bs

            result = bs.query_history_k_data_plus(
                code,
                "date,code,close",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3",
            )
            return [self._bar_from_row(row) for row in self._rows_from_result(result)]
        except Exception as exc:
            raise ProviderError("BaoStock historical daily failed") from exc

    @staticmethod
    def _rows_from_result(result: Any) -> Iterable[Mapping[str, Any]]:
        if isinstance(result, list):
            return result
        if hasattr(result, "to_dict"):
            return result.to_dict("records")
        if hasattr(result, "next") and hasattr(result, "get_row_data"):
            rows = []
            fields = list(getattr(result, "fields", ["date", "code", "close"]))
            while result.next():
                rows.append(dict(zip(fields, result.get_row_data(), strict=False)))
            return rows
        return result

    @staticmethod
    def _bar_from_row(row: Mapping[str, Any]) -> HistoricalBar:
        return HistoricalBar(
            date=str(row["date"]),
            code=str(row["code"]),
            close=float(row["close"]),
        )
