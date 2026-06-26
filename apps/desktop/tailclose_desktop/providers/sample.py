from tailclose_desktop.models import StockQuote


class SampleProvider:
    def current_quotes(self) -> list[StockQuote]:
        return [
            StockQuote(
                code="600000",
                name="浦发银行",
                latest_price=8.80,
                change_percent=2.10,
                volume_ratio=1.80,
                turnover_rate=3.20,
                moving_averages={"ma5": 8.6, "ma10": 8.4, "ma20": 8.1},
                late_session_active=True,
            ),
            StockQuote(
                code="000001",
                name="平安银行",
                latest_price=12.30,
                change_percent=1.50,
                volume_ratio=1.60,
                turnover_rate=2.70,
                moving_averages={"ma5": 12.0, "ma10": 11.8, "ma20": 11.5},
            ),
            StockQuote(
                code="600519",
                name="贵州茅台",
                latest_price=1520.00,
                change_percent=0.80,
                volume_ratio=1.20,
                turnover_rate=0.90,
            ),
        ]
