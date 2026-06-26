from tailclose_desktop.models import StockQuote


class SampleProvider:
    def current_quotes(self) -> list[StockQuote]:
        return [
            StockQuote(
                code="600000",
                name="浦发银行",
                price=8.80,
                change_pct=2.10,
                volume_ratio=1.80,
                turnover_rate=3.20,
                is_st=False,
            ),
            StockQuote(
                code="000001",
                name="平安银行",
                price=12.30,
                change_pct=1.50,
                volume_ratio=1.60,
                turnover_rate=2.70,
                is_st=False,
            ),
            StockQuote(
                code="600519",
                name="贵州茅台",
                price=1520.00,
                change_pct=0.80,
                volume_ratio=1.20,
                turnover_rate=0.90,
                is_st=False,
            ),
        ]
