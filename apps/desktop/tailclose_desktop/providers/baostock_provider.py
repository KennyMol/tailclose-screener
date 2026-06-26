from collections.abc import Iterable, Mapping
from typing import Any

from tailclose_desktop.models import HistoricalBar
from tailclose_desktop.providers.base import ProviderError


def to_baostock_code(code: str) -> str:
    normalized = code.lower()
    if normalized.startswith(("sh.", "sz.")):
        return normalized
    if normalized.startswith(("600", "601", "603", "605", "688")):
        return f"sh.{normalized}"
    return f"sz.{normalized}"


class BaoStockProvider:
    def __init__(self, bs: Any | None = None) -> None:
        self._bs = bs

    def historical_daily(
        self,
        code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[HistoricalBar]:
        bs = self._baostock_module()
        logged_in = False
        try:
            login = bs.login()
            if getattr(login, "error_code", "") != "0":
                message = getattr(login, "error_msg", "")
                raise ProviderError(f"BaoStock 登录失败: {message}")
            logged_in = True

            result = bs.query_history_k_data_plus(
                to_baostock_code(code),
                "date,code,open,close,volume",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3",
            )
            return [self._bar_from_row(row) for row in self._rows_from_result(result)]
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("BaoStock historical daily failed") from exc
        finally:
            if logged_in and hasattr(bs, "logout"):
                bs.logout()

    def _baostock_module(self) -> Any:
        if self._bs is not None:
            return self._bs
        import baostock as bs

        return bs

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
            open=float(row["open"]) if row.get("open") not in (None, "") else None,
            close=float(row["close"]),
            volume=float(row["volume"]) if row.get("volume") not in (None, "") else None,
        )
