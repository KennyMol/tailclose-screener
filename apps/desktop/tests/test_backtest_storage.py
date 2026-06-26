from tailclose_desktop.backtest import summarize_backtest
from tailclose_desktop.storage import SettingsStore


def test_summarize_backtest_reports_unavailable_history():
    signals = [{"code": "600000", "score": 2.5}, {"code": "000001", "score": 1.8}]

    summary = summarize_backtest(signals)

    assert summary["signal_count"] == 2
    assert summary["available"] is False
    assert "历史行情不足" in summary["message"]
    assert summary["signals"] == signals


def test_settings_store_persists_values_and_uses_default(tmp_path):
    db_path = tmp_path / "nested" / "settings.sqlite3"

    store = SettingsStore(db_path)
    assert store.get_value("missing", default="fallback") == "fallback"

    store.set_value("provider", "akshare")
    store.set_value("window", "tailclose")

    reopened = SettingsStore(db_path)
    assert reopened.get_value("provider") == "akshare"
    assert reopened.get_value("window") == "tailclose"
    assert db_path.exists()
