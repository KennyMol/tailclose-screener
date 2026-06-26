import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from tailclose_desktop.providers.base import ProviderError
from tailclose_desktop.providers.sample import SampleProvider
from tailclose_desktop.ui.main_window import MainWindow


def test_main_window_refresh_populates_results():
    app = QApplication.instance() or QApplication([])
    window = MainWindow(provider=SampleProvider())

    assert window.windowTitle() == "尾盘买入法"

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
