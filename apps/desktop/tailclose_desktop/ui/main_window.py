from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from datetime import date, timedelta
from typing import Protocol

from tailclose_desktop.models import HistoricalBar, ScreenResult, Strategy, StockQuote
from tailclose_desktop.providers.akshare_provider import AkShareProvider
from tailclose_desktop.providers.base import ProviderError
from tailclose_desktop.providers.base import QuoteProvider
from tailclose_desktop.providers.baostock_provider import BaoStockProvider
from tailclose_desktop.providers.sample import SampleProvider
from tailclose_desktop.strategy import (
    default_tailclose_strategy,
    passes_custom_realtime_rules,
    screen_custom_tailclose_candidates,
    screen_quotes,
)


class HistoryProvider(Protocol):
    def historical_daily(
        self,
        code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[HistoricalBar]:
        ...


class MainWindow(QMainWindow):
    headers = ("代码", "名称", "现价", "涨幅", "量比", "原因")

    def __init__(
        self,
        provider: QuoteProvider | None = None,
        history_provider: HistoryProvider | None = None,
        strategy: Strategy | None = None,
    ) -> None:
        super().__init__()
        self.provider = provider
        self.history_provider = history_provider or BaoStockProvider()
        self.strategy = strategy or default_tailclose_strategy()

        self.setWindowTitle("尾盘买入法")
        self.resize(900, 560)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItem(self.strategy.name, self.strategy.id)
        self.strategy_combo.addItem("我的策略", "custom-tailclose")

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("实时行情 AkShare", "akshare")
        self.provider_combo.addItem("示例数据", "sample")

        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh)

        self.results_table = QTableWidget(0, len(self.headers))
        self.results_table.setHorizontalHeaderLabels(self.headers)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.status_label = QLabel("准备就绪")

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(QLabel("策略"))
        toolbar_layout.addWidget(self.strategy_combo, 1)
        toolbar_layout.addWidget(QLabel("数据源"))
        toolbar_layout.addWidget(self.provider_combo)
        toolbar_layout.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.results_table, 1)
        layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def refresh(self) -> None:
        try:
            quotes = self._active_provider().current_quotes()
            if self.strategy_combo.currentData() == "custom-tailclose":
                results = self._screen_custom_strategy(quotes)
            else:
                results = screen_quotes(quotes, self.strategy)
        except ProviderError as exc:
            self.results_table.setRowCount(0)
            self.status_label.setText(f"刷新失败：{exc}")
            return

        self._set_results(results)
        self.status_label.setText(f"刷新完成：{len(results)} 条结果（{self.strategy_combo.currentText()}）")

    def _active_provider(self) -> QuoteProvider:
        if self.provider is not None:
            return self.provider
        if self.provider_combo.currentData() == "sample":
            return SampleProvider()
        return AkShareProvider()

    def _screen_custom_strategy(self, quotes: list[StockQuote]) -> list[ScreenResult]:
        candidates: list[tuple[StockQuote, list[HistoricalBar]]] = []
        realtime_matches = [quote for quote in quotes if passes_custom_realtime_rules(quote)]
        end_date = date.today()
        start_date = end_date - timedelta(days=20)
        for quote in realtime_matches:
            try:
                history = self.history_provider.historical_daily(
                    quote.code,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                )
            except ProviderError:
                continue
            candidates.append((quote, history))
        return screen_custom_tailclose_candidates(candidates)

    def _set_results(self, results: list[ScreenResult]) -> None:
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            values = (
                result.code,
                result.name,
                self._format_number(result.latest_price),
                self._format_percent(result.change_percent),
                self._format_number(result.volume_ratio),
                "；".join(result.reasons),
            )
            for column, value in enumerate(values):
                self.results_table.setItem(row, column, QTableWidgetItem(value))

    @staticmethod
    def _format_number(value: float | None) -> str:
        if value is None:
            return "-"
        return f"{value:.2f}"

    @staticmethod
    def _format_percent(value: float | None) -> str:
        if value is None:
            return "-"
        return f"{value:.2f}%"
