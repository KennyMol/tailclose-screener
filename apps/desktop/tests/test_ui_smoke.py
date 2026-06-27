import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from tailclose_desktop.models import HistoricalBar, StockQuote
from tailclose_desktop.providers.base import ProviderError
from tailclose_desktop.providers.sample import SampleProvider
from tailclose_desktop.ui.main_window import MainWindow


def test_main_window_refresh_populates_results():
    app = QApplication.instance() or QApplication([])
    window = MainWindow(provider=SampleProvider())

    assert window.windowTitle() == "尾盘买入法"
    assert window.provider_combo.currentText() == "实时行情 AkShare"

    window.refresh()

    assert window.results_table.rowCount() >= 1
    assert window.status_label.text().find("刷新完成") != -1
    assert [window.results_table.horizontalHeaderItem(index).text() for index in range(6)] == [
        "代码",
        "名称",
        "现价",
        "涨幅",
        "量比",
        "原因",
    ]

    window.close()
    app.processEvents()


def test_main_window_refresh_reports_provider_errors():
    class FailingProvider:
        def current_quotes(self):
            raise ProviderError("network down")

    app = QApplication.instance() or QApplication([])
    window = MainWindow(provider=FailingProvider())

    window.refresh()

    assert window.results_table.rowCount() == 0
    assert "刷新失败" in window.status_label.text()

    window.close()
    app.processEvents()


def test_main_window_status_message_can_be_selected_for_copying():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    assert window.status_label.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse

    window.close()
    app.processEvents()


def test_main_window_can_switch_to_sample_provider():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.provider_combo.setCurrentText("示例数据")

    window.refresh()

    assert window.results_table.rowCount() >= 1
    assert "刷新完成" in window.status_label.text()

    window.close()
    app.processEvents()


def test_main_window_can_select_tushare_provider(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.provider_combo.setCurrentText("Tushare")

    window.refresh()

    assert "TUSHARE_TOKEN" in window.status_label.text()

    window.close()
    app.processEvents()


def test_main_window_runs_custom_strategy_with_history_provider():
    class QuoteFixtureProvider:
        def current_quotes(self):
            return [
                StockQuote(
                    code="600000",
                    name="浦发银行",
                    latest_price=12.6,
                    change_percent=5.0,
                    volume_ratio=1.5,
                    turnover_rate=10.0,
                )
            ]

    class HistoryFixtureProvider:
        def historical_daily(self, code, start_date=None, end_date=None):
            return [
                HistoricalBar(date="2026-06-19", code=code, open=10.0, close=10.0, volume=1000),
                HistoricalBar(date="2026-06-22", code=code, open=10.0, close=10.5, volume=1200),
                HistoricalBar(date="2026-06-23", code=code, open=10.5, close=10.8, volume=1300),
                HistoricalBar(date="2026-06-24", code=code, open=10.8, close=11.86, volume=1500),
                HistoricalBar(date="2026-06-25", code=code, open=11.7, close=12.0, volume=1800),
                HistoricalBar(date="2026-06-26", code=code, open=12.0, close=12.6, volume=2200),
            ]

    app = QApplication.instance() or QApplication([])
    window = MainWindow(provider=QuoteFixtureProvider(), history_provider=HistoryFixtureProvider())
    window.strategy_combo.setCurrentText("我的策略")

    window.refresh()

    assert window.results_table.rowCount() == 1
    assert "我的策略" in window.status_label.text()
    assert "量价齐升" in window.results_table.item(0, 5).text()

    window.close()
    app.processEvents()


def test_custom_strategy_skips_history_for_realtime_misses():
    class QuoteFixtureProvider:
        def current_quotes(self):
            return [
                StockQuote(
                    code="600000",
                    name="浦发银行",
                    latest_price=12.6,
                    change_percent=2.0,
                    volume_ratio=1.5,
                    turnover_rate=10.0,
                )
            ]

    class HistoryFixtureProvider:
        def historical_daily(self, code, start_date=None, end_date=None):
            raise AssertionError("history should not be queried")

    app = QApplication.instance() or QApplication([])
    window = MainWindow(provider=QuoteFixtureProvider(), history_provider=HistoryFixtureProvider())
    window.strategy_combo.setCurrentText("我的策略")

    window.refresh()

    assert window.results_table.rowCount() == 0

    window.close()
    app.processEvents()
