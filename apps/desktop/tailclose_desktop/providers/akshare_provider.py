from collections.abc import Iterable, Mapping
from typing import Any

from tailclose_desktop.models import StockQuote
from tailclose_desktop.providers.base import ProviderError


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_akshare_row(row: Mapping[str, Any]) -> StockQuote:
    name = str(row.get("名称", ""))
    return StockQuote(
        code=str(row.get("代码", "")),
        name=name,
        latest_price=_float_or_none(row.get("最新价")),
        change_percent=_float_or_none(row.get("涨跌幅")),
        volume_ratio=_float_or_none(row.get("量比")),
        turnover_rate=_float_or_none(row.get("换手率")),
        is_st="ST" in name.upper(),
    )


class AkShareProvider:
    def __init__(self, ak: Any | None = None) -> None:
        self._ak = ak

    def current_quotes(self) -> list[StockQuote]:
        errors: list[Exception] = []
        try:
            ak = self._ak
            if ak is None:
                import akshare as ak

            for source_name in ("stock_zh_a_spot_em", "stock_zh_a_spot"):
                source = getattr(ak, source_name, None)
                if source is None:
                    continue
                try:
                    rows = self._rows_from_spot(source())
                    return [normalize_akshare_row(row) for row in rows]
                except Exception as exc:
                    errors.append(exc)
        except Exception as exc:
            errors.append(exc)

        detail = "; ".join(str(error) for error in errors) or "no available quote source"
        raise ProviderError(f"AkShare current quotes failed: {detail}")

    @staticmethod
    def _rows_from_spot(spot: Any) -> Iterable[Mapping[str, Any]]:
        if hasattr(spot, "to_dict"):
            return spot.to_dict("records")
        return spot
