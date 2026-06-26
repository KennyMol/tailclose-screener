from collections.abc import Iterable, Mapping
from typing import Any

from tailclose_desktop.models import StockQuote
from tailclose_desktop.providers.base import ProviderError


def normalize_akshare_row(row: Mapping[str, Any]) -> StockQuote:
    name = str(row["名称"])
    return StockQuote(
        code=str(row["代码"]),
        name=name,
        price=float(row["最新价"]),
        change_pct=float(row["涨跌幅"]),
        volume_ratio=float(row["量比"]),
        turnover_rate=float(row["换手率"]),
        is_st="ST" in name.upper(),
    )


class AkShareProvider:
    def __init__(self, ak: Any | None = None) -> None:
        self._ak = ak

    def current_quotes(self) -> list[StockQuote]:
        try:
            ak = self._ak
            if ak is None:
                import akshare as ak

            rows = self._rows_from_spot(ak.stock_zh_a_spot_em())
            return [normalize_akshare_row(row) for row in rows]
        except Exception as exc:
            raise ProviderError("AkShare current quotes failed") from exc

    @staticmethod
    def _rows_from_spot(spot: Any) -> Iterable[Mapping[str, Any]]:
        if hasattr(spot, "to_dict"):
            return spot.to_dict("records")
        return spot
