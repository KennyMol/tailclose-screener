# Tailclose Desktop EXE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows 64-bit Python desktop app that screens A-share stocks with AkShare/baostock-ready data providers and can be packaged as an exe.

**Architecture:** Add a new Python app under `apps/desktop` without removing the existing PWA. Keep domain logic, providers, notification formatting, UI, and packaging separate so each piece can be tested independently. Use sample data as the deterministic baseline while AkShare and baostock adapters are isolated behind provider interfaces.

**Tech Stack:** Python 3.11+, PySide6, pytest, pandas, akshare, baostock, requests, PyInstaller, SQLite.

---

## File Structure

- `apps/desktop/pyproject.toml`: Python package metadata and dependencies.
- `apps/desktop/README.md`: desktop-specific run and package instructions.
- `apps/desktop/tailclose_desktop/main.py`: app entry point.
- `apps/desktop/tailclose_desktop/models.py`: dataclasses for quotes, strategies, results, and backtest summaries.
- `apps/desktop/tailclose_desktop/strategy.py`: tail-close screening engine.
- `apps/desktop/tailclose_desktop/providers/base.py`: provider protocol and provider errors.
- `apps/desktop/tailclose_desktop/providers/sample.py`: deterministic offline provider.
- `apps/desktop/tailclose_desktop/providers/akshare_provider.py`: AkShare quote adapter.
- `apps/desktop/tailclose_desktop/providers/baostock_provider.py`: baostock history adapter.
- `apps/desktop/tailclose_desktop/backtest.py`: compact backtest summary shell.
- `apps/desktop/tailclose_desktop/notify/feishu.py`: Feishu message formatting and webhook send.
- `apps/desktop/tailclose_desktop/storage.py`: app data paths and SQLite settings store.
- `apps/desktop/tailclose_desktop/ui/main_window.py`: PySide6 main window.
- `apps/desktop/tailclose_desktop/ui/settings_dialog.py`: Feishu/settings dialog.
- `apps/desktop/tests/`: pytest tests.
- `apps/desktop/packaging/tailclose-screener.spec`: PyInstaller spec.

## Task 1: Python Project Scaffold

**Files:**
- Create: `apps/desktop/pyproject.toml`
- Create: `apps/desktop/README.md`
- Create: `apps/desktop/tailclose_desktop/__init__.py`
- Create: `apps/desktop/tailclose_desktop/main.py`
- Create: `apps/desktop/tests/test_smoke.py`

- [ ] **Step 1: Create scaffold files**

Create `apps/desktop/pyproject.toml`:

```toml
[project]
name = "tailclose-desktop"
version = "0.1.0"
description = "Windows desktop tail-close stock screener"
requires-python = ">=3.11"
dependencies = [
  "PySide6>=6.7",
  "pandas>=2.2",
  "akshare>=1.14",
  "baostock>=0.8.9",
  "requests>=2.32"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2",
  "pyinstaller>=6.8"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

Create `apps/desktop/README.md`:

```md
# Tailclose Desktop

Windows desktop version of tailclose-screener.

## Setup

```powershell
cd apps/desktop
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Test

```powershell
pytest
```

## Run

```powershell
python -m tailclose_desktop.main
```
```

Create `apps/desktop/tailclose_desktop/__init__.py`:

```python
__all__ = ["__version__"]

__version__ = "0.1.0"
```

Create `apps/desktop/tailclose_desktop/main.py`:

```python
def main() -> int:
    print("Tailclose Desktop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Write smoke test**

Create `apps/desktop/tests/test_smoke.py`:

```python
from tailclose_desktop.main import main


def test_main_returns_success(capsys):
    assert main() == 0
    assert "Tailclose Desktop" in capsys.readouterr().out
```

- [ ] **Step 3: Run red/green scaffold verification**

Run:

```powershell
cd apps/desktop
python -m pip install -e ".[dev]"
pytest
```

Expected: pytest passes with 1 test.

- [ ] **Step 4: Commit scaffold**

Run:

```bash
git add apps/desktop
git commit -m "chore: scaffold desktop app"
```

## Task 2: Domain Models And Strategy Engine

**Files:**
- Create: `apps/desktop/tailclose_desktop/models.py`
- Create: `apps/desktop/tailclose_desktop/strategy.py`
- Create: `apps/desktop/tests/test_strategy.py`

- [ ] **Step 1: Write failing strategy tests**

Create `apps/desktop/tests/test_strategy.py`:

```python
from tailclose_desktop.models import StockQuote
from tailclose_desktop.strategy import default_tailclose_strategy, screen_quotes


def base_quote(**overrides):
    data = {
        "code": "600000",
        "name": "浦发银行",
        "latest_price": 10.2,
        "change_percent": 2.1,
        "volume_ratio": 1.8,
        "turnover_rate": 3.2,
        "is_st": False,
        "is_suspended": False,
        "is_delisting_risk": False,
        "moving_averages": {"ma5": 10.0, "ma10": 9.9, "ma20": 9.7},
        "late_session_active": True,
    }
    data.update(overrides)
    return StockQuote(**data)


def test_default_strategy_includes_matching_quote():
    results = screen_quotes([base_quote()], default_tailclose_strategy())
    assert len(results) == 1
    assert results[0].code == "600000"
    assert "涨幅在 0% 到 6%" in results[0].reasons
    assert "量比大于 1.2" in results[0].reasons


def test_default_strategy_excludes_out_of_range_change_percent():
    results = screen_quotes([base_quote(change_percent=8.1)], default_tailclose_strategy())
    assert results == []


def test_default_strategy_excludes_risk_flags():
    quotes = [
        base_quote(code="600001", is_st=True),
        base_quote(code="600002", is_suspended=True),
        base_quote(code="600003", is_delisting_risk=True),
    ]
    assert screen_quotes(quotes, default_tailclose_strategy()) == []


def test_quotes_without_positive_reason_are_excluded():
    quote = StockQuote(code="600004", name="空数据")
    assert screen_quotes([quote], default_tailclose_strategy()) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
cd apps/desktop
pytest tests/test_strategy.py
```

Expected: FAIL because `models.py` and `strategy.py` do not exist.

- [ ] **Step 3: Implement models**

Create `apps/desktop/tailclose_desktop/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StockQuote:
    code: str
    name: str
    latest_price: float | None = None
    change_percent: float | None = None
    volume_ratio: float | None = None
    turnover_rate: float | None = None
    is_st: bool = False
    is_suspended: bool = False
    is_delisting_risk: bool = False
    moving_averages: dict[str, float] = field(default_factory=dict)
    late_session_active: bool = False


@dataclass(frozen=True)
class NumericCondition:
    field: str
    label: str
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class Strategy:
    id: str
    name: str
    numeric_conditions: list[NumericCondition]
    exclude_flags: tuple[str, ...]
    require_moving_average: bool = True
    require_late_session_active: bool = False


@dataclass(frozen=True)
class ScreenResult:
    code: str
    name: str
    latest_price: float | None
    change_percent: float | None
    volume_ratio: float | None
    reasons: list[str]
    score: float
```

- [ ] **Step 4: Implement strategy engine**

Create `apps/desktop/tailclose_desktop/strategy.py`:

```python
from __future__ import annotations

from typing import Iterable

from .models import NumericCondition, ScreenResult, StockQuote, Strategy


def default_tailclose_strategy() -> Strategy:
    return Strategy(
        id="tail-close-default",
        name="默认尾盘买入法",
        numeric_conditions=[
            NumericCondition("change_percent", "涨幅在 0% 到 6%", 0, 6),
            NumericCondition("volume_ratio", "量比大于 1.2", 1.2, None),
            NumericCondition("turnover_rate", "换手率适中", 1, 12),
        ],
        exclude_flags=("is_st", "is_suspended", "is_delisting_risk"),
    )


def _passes_numeric(quote: StockQuote, condition: NumericCondition) -> bool:
    value = getattr(quote, condition.field)
    if value is None:
        return True
    if condition.minimum is not None and value < condition.minimum:
        return False
    if condition.maximum is not None and value > condition.maximum:
        return False
    return True


def _above_any_moving_average(quote: StockQuote) -> bool:
    if quote.latest_price is None or not quote.moving_averages:
        return True
    return any(quote.latest_price >= value for value in quote.moving_averages.values())


def screen_quotes(quotes: Iterable[StockQuote], strategy: Strategy) -> list[ScreenResult]:
    results: list[ScreenResult] = []
    for quote in quotes:
        if any(getattr(quote, flag) for flag in strategy.exclude_flags):
            continue

        reasons: list[str] = []
        rejected = False
        for condition in strategy.numeric_conditions:
            if not _passes_numeric(quote, condition):
                rejected = True
                break
            if getattr(quote, condition.field) is not None:
                reasons.append(condition.label)
        if rejected:
            continue

        if strategy.require_moving_average and not _above_any_moving_average(quote):
            continue
        if quote.latest_price is not None and quote.moving_averages:
            reasons.append("价格在均线上方")

        if strategy.require_late_session_active and not quote.late_session_active:
            continue
        if quote.late_session_active:
            reasons.append("尾盘成交活跃")

        if not reasons:
            continue

        results.append(
            ScreenResult(
                code=quote.code,
                name=quote.name,
                latest_price=quote.latest_price,
                change_percent=quote.change_percent,
                volume_ratio=quote.volume_ratio,
                reasons=reasons,
                score=len(reasons) * 10 + (quote.volume_ratio or 0),
            )
        )
    return sorted(results, key=lambda item: item.score, reverse=True)
```

- [ ] **Step 5: Verify strategy tests pass**

Run:

```powershell
cd apps/desktop
pytest tests/test_strategy.py
```

Expected: PASS.

- [ ] **Step 6: Commit strategy engine**

Run:

```bash
git add apps/desktop/tailclose_desktop/models.py apps/desktop/tailclose_desktop/strategy.py apps/desktop/tests/test_strategy.py
git commit -m "feat: add desktop strategy engine"
```

## Task 3: Providers And Normalization

**Files:**
- Create: `apps/desktop/tailclose_desktop/providers/__init__.py`
- Create: `apps/desktop/tailclose_desktop/providers/base.py`
- Create: `apps/desktop/tailclose_desktop/providers/sample.py`
- Create: `apps/desktop/tailclose_desktop/providers/akshare_provider.py`
- Create: `apps/desktop/tailclose_desktop/providers/baostock_provider.py`
- Create: `apps/desktop/tests/test_providers.py`

- [ ] **Step 1: Write failing provider tests**

Create `apps/desktop/tests/test_providers.py`:

```python
from tailclose_desktop.providers.akshare_provider import normalize_akshare_row
from tailclose_desktop.providers.sample import SampleProvider


def test_sample_provider_returns_matching_quotes():
    quotes = SampleProvider().current_quotes()
    assert quotes
    assert quotes[0].code == "600000"


def test_akshare_row_normalization_maps_known_fields():
    row = {
        "代码": "600000",
        "名称": "浦发银行",
        "最新价": 10.21,
        "涨跌幅": 2.1,
        "量比": 1.8,
        "换手率": 3.2,
    }
    quote = normalize_akshare_row(row)
    assert quote.code == "600000"
    assert quote.name == "浦发银行"
    assert quote.latest_price == 10.21
    assert quote.change_percent == 2.1
    assert quote.volume_ratio == 1.8
    assert quote.turnover_rate == 3.2
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
cd apps/desktop
pytest tests/test_providers.py
```

Expected: FAIL because provider modules do not exist.

- [ ] **Step 3: Implement provider base and sample provider**

Create `apps/desktop/tailclose_desktop/providers/__init__.py`:

```python
from .sample import SampleProvider

__all__ = ["SampleProvider"]
```

Create `apps/desktop/tailclose_desktop/providers/base.py`:

```python
from __future__ import annotations

from typing import Protocol

from tailclose_desktop.models import StockQuote


class ProviderError(RuntimeError):
    pass


class QuoteProvider(Protocol):
    def current_quotes(self) -> list[StockQuote]:
        ...
```

Create `apps/desktop/tailclose_desktop/providers/sample.py`:

```python
from __future__ import annotations

from tailclose_desktop.models import StockQuote


class SampleProvider:
    def current_quotes(self) -> list[StockQuote]:
        return [
            StockQuote(
                code="600000",
                name="浦发银行",
                latest_price=10.21,
                change_percent=2.1,
                volume_ratio=1.8,
                turnover_rate=3.2,
                moving_averages={"ma5": 10.0, "ma10": 9.9, "ma20": 9.7},
                late_session_active=True,
            ),
            StockQuote(
                code="000001",
                name="平安银行",
                latest_price=12.44,
                change_percent=1.4,
                volume_ratio=1.5,
                turnover_rate=2.6,
                moving_averages={"ma5": 12.2, "ma10": 12.1, "ma20": 11.8},
            ),
            StockQuote(
                code="300000",
                name="示例股票",
                latest_price=18.7,
                change_percent=8.2,
                volume_ratio=2.2,
                turnover_rate=7.1,
            ),
        ]
```

- [ ] **Step 4: Implement AkShare and baostock adapters**

Create `apps/desktop/tailclose_desktop/providers/akshare_provider.py`:

```python
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tailclose_desktop.models import StockQuote

from .base import ProviderError


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
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
    def current_quotes(self) -> list[StockQuote]:
        try:
            import akshare as ak

            frame = ak.stock_zh_a_spot_em()
            return [normalize_akshare_row(row) for row in frame.to_dict("records")]
        except Exception as exc:
            raise ProviderError(f"AkShare 数据源不可用: {exc}") from exc
```

Create `apps/desktop/tailclose_desktop/providers/baostock_provider.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from .base import ProviderError


@dataclass(frozen=True)
class HistoricalBar:
    date: str
    code: str
    close: float


class BaoStockProvider:
    def historical_daily(self, code: str, start_date: str, end_date: str) -> list[HistoricalBar]:
        try:
            import baostock as bs

            login = bs.login()
            if login.error_code != "0":
                raise ProviderError(f"baostock 登录失败: {login.error_msg}")
            result = bs.query_history_k_data_plus(
                code,
                "date,code,close",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3",
            )
            bars: list[HistoricalBar] = []
            while result.error_code == "0" and result.next():
                row = result.get_row_data()
                bars.append(HistoricalBar(date=row[0], code=row[1], close=float(row[2])))
            bs.logout()
            return bars
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"baostock 数据源不可用: {exc}") from exc
```

- [ ] **Step 5: Verify provider tests pass**

Run:

```powershell
cd apps/desktop
pytest tests/test_providers.py
```

Expected: PASS.

- [ ] **Step 6: Commit providers**

Run:

```bash
git add apps/desktop/tailclose_desktop/providers apps/desktop/tests/test_providers.py
git commit -m "feat: add desktop market data providers"
```

## Task 4: Feishu Notification Module

**Files:**
- Create: `apps/desktop/tailclose_desktop/notify/__init__.py`
- Create: `apps/desktop/tailclose_desktop/notify/feishu.py`
- Create: `apps/desktop/tests/test_feishu.py`

- [ ] **Step 1: Write failing Feishu tests**

Create `apps/desktop/tests/test_feishu.py`:

```python
from tailclose_desktop.models import ScreenResult
from tailclose_desktop.notify.feishu import format_feishu_message


def test_feishu_message_formats_results_without_webhook_secret():
    result = ScreenResult(
        code="600000",
        name="浦发银行",
        latest_price=10.21,
        change_percent=2.1,
        volume_ratio=1.8,
        reasons=["尾盘成交活跃"],
        score=88,
    )
    text = format_feishu_message("默认尾盘买入法", [result], "https://open.feishu.cn/webhook/secret")
    assert "默认尾盘买入法" in text
    assert "600000 浦发银行" in text
    assert "secret" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
cd apps/desktop
pytest tests/test_feishu.py
```

Expected: FAIL because notify module does not exist.

- [ ] **Step 3: Implement Feishu formatter and sender**

Create `apps/desktop/tailclose_desktop/notify/__init__.py`:

```python
from .feishu import format_feishu_message, send_feishu_text

__all__ = ["format_feishu_message", "send_feishu_text"]
```

Create `apps/desktop/tailclose_desktop/notify/feishu.py`:

```python
from __future__ import annotations

from collections.abc import Sequence

import requests

from tailclose_desktop.models import ScreenResult


def format_feishu_message(strategy_name: str, results: Sequence[ScreenResult], webhook_url: str | None = None) -> str:
    lines = [
        f"尾盘筛选结果：{strategy_name}",
        "仅供策略筛选和观察，不构成投资建议。",
    ]
    if not results:
        lines.append("当前没有符合条件的股票。")
    for item in results:
        reasons = "、".join(item.reasons)
        change = "--" if item.change_percent is None else f"{item.change_percent:+.1f}%"
        lines.append(f"{item.code} {item.name} {change} 量比 {item.volume_ratio or '--'} {reasons}")
    return "\n".join(lines)


def send_feishu_text(webhook_url: str, text: str, timeout: float = 5.0) -> None:
    response = requests.post(webhook_url, json={"msg_type": "text", "content": {"text": text}}, timeout=timeout)
    response.raise_for_status()
```

- [ ] **Step 4: Verify Feishu tests pass**

Run:

```powershell
cd apps/desktop
pytest tests/test_feishu.py
```

Expected: PASS.

- [ ] **Step 5: Commit Feishu module**

Run:

```bash
git add apps/desktop/tailclose_desktop/notify apps/desktop/tests/test_feishu.py
git commit -m "feat: add feishu notification formatter"
```

## Task 5: Backtest And Storage Shell

**Files:**
- Create: `apps/desktop/tailclose_desktop/backtest.py`
- Create: `apps/desktop/tailclose_desktop/storage.py`
- Create: `apps/desktop/tests/test_backtest_storage.py`

- [ ] **Step 1: Write failing tests**

Create `apps/desktop/tests/test_backtest_storage.py`:

```python
from tailclose_desktop.backtest import summarize_backtest
from tailclose_desktop.storage import SettingsStore


def test_backtest_summary_reports_unavailable_metrics():
    summary = summarize_backtest([{"date": "2026-06-20", "code": "600000"}])
    assert summary["signal_count"] == 1
    assert summary["available"] is False
    assert "历史行情不足" in summary["message"]


def test_settings_store_round_trips_values(tmp_path):
    store = SettingsStore(tmp_path / "settings.db")
    store.set_value("feishu_webhook", "hidden")
    assert store.get_value("feishu_webhook") == "hidden"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
cd apps/desktop
pytest tests/test_backtest_storage.py
```

Expected: FAIL because modules do not exist.

- [ ] **Step 3: Implement backtest and storage**

Create `apps/desktop/tailclose_desktop/backtest.py`:

```python
from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def summarize_backtest(signals: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return {
        "signal_count": len(signals),
        "available": False,
        "message": "历史行情不足，暂不能计算胜率、平均收益和最大回撤。",
        "signals": list(signals),
    }
```

Create `apps/desktop/tailclose_desktop/storage.py`:

```python
from __future__ import annotations

import sqlite3
from pathlib import Path


class SettingsStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def set_value(self, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_value(self, key: str, default: str | None = None) -> str | None:
        with self._connect() as connection:
            row = connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return default if row is None else str(row[0])
```

- [ ] **Step 4: Verify tests pass**

Run:

```powershell
cd apps/desktop
pytest tests/test_backtest_storage.py
```

Expected: PASS.

- [ ] **Step 5: Commit backtest/storage shell**

Run:

```bash
git add apps/desktop/tailclose_desktop/backtest.py apps/desktop/tailclose_desktop/storage.py apps/desktop/tests/test_backtest_storage.py
git commit -m "feat: add desktop backtest and storage shell"
```

## Task 6: PySide6 UI

**Files:**
- Create: `apps/desktop/tailclose_desktop/ui/__init__.py`
- Create: `apps/desktop/tailclose_desktop/ui/main_window.py`
- Create: `apps/desktop/tailclose_desktop/ui/settings_dialog.py`
- Modify: `apps/desktop/tailclose_desktop/main.py`
- Create: `apps/desktop/tests/test_ui_smoke.py`

- [ ] **Step 1: Write failing UI smoke test**

Create `apps/desktop/tests/test_ui_smoke.py`:

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from tailclose_desktop.ui.main_window import MainWindow


def test_main_window_can_refresh_sample_results():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.refresh()
    assert window.table.rowCount() >= 1
    assert "刷新完成" in window.status_label.text()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
cd apps/desktop
pytest tests/test_ui_smoke.py
```

Expected: FAIL because UI modules do not exist.

- [ ] **Step 3: Implement main window and settings dialog**

Create `apps/desktop/tailclose_desktop/ui/__init__.py`:

```python
from .main_window import MainWindow

__all__ = ["MainWindow"]
```

Create `apps/desktop/tailclose_desktop/ui/settings_dialog.py`:

```python
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.webhook_input = QLineEdit(self)
        self.test_button = QPushButton("测试发送", self)
        form = QFormLayout()
        form.addRow("飞书 Webhook", self.webhook_input)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.test_button)
```

Create `apps/desktop/tailclose_desktop/ui/main_window.py`:

```python
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

from tailclose_desktop.providers.sample import SampleProvider
from tailclose_desktop.strategy import default_tailclose_strategy, screen_quotes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("尾盘买入法")
        self.resize(820, 520)
        self.provider = SampleProvider()
        self.strategy = default_tailclose_strategy()

        self.strategy_select = QComboBox(self)
        self.strategy_select.addItem(self.strategy.name, self.strategy.id)
        self.refresh_button = QPushButton("刷新", self)
        self.refresh_button.clicked.connect(self.refresh)

        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(["代码", "名称", "现价", "涨幅", "量比", "原因"])
        self.status_label = QLabel("未刷新", self)

        top = QHBoxLayout()
        top.addWidget(self.strategy_select)
        top.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.table)
        layout.addWidget(self.status_label)

        root = QWidget(self)
        root.setLayout(layout)
        self.setCentralWidget(root)

    def refresh(self) -> None:
        quotes = self.provider.current_quotes()
        results = screen_quotes(quotes, self.strategy)
        self.table.setRowCount(len(results))
        for row_index, result in enumerate(results):
            values = [
                result.code,
                result.name,
                "" if result.latest_price is None else f"{result.latest_price:.2f}",
                "" if result.change_percent is None else f"{result.change_percent:+.1f}%",
                "" if result.volume_ratio is None else f"{result.volume_ratio:.1f}",
                "、".join(result.reasons),
            ]
            for column_index, value in enumerate(values):
                self.table.setItem(row_index, column_index, QTableWidgetItem(value))
        self.status_label.setText(f"刷新完成：{len(results)} 只股票")
```

Replace `apps/desktop/tailclose_desktop/main.py`:

```python
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from tailclose_desktop.ui.main_window import MainWindow


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Update smoke test from Task 1**

Replace `apps/desktop/tests/test_smoke.py`:

```python
from tailclose_desktop import __version__


def test_package_version_exists():
    assert __version__ == "0.1.0"
```

- [ ] **Step 5: Verify UI tests pass**

Run:

```powershell
cd apps/desktop
pytest tests/test_ui_smoke.py tests/test_smoke.py
```

Expected: PASS.

- [ ] **Step 6: Commit UI**

Run:

```bash
git add apps/desktop/tailclose_desktop/ui apps/desktop/tailclose_desktop/main.py apps/desktop/tests/test_ui_smoke.py apps/desktop/tests/test_smoke.py
git commit -m "feat: add desktop ui shell"
```

## Task 7: Packaging

**Files:**
- Create: `apps/desktop/packaging/tailclose-screener.spec`
- Modify: `apps/desktop/README.md`
- Create: `apps/desktop/tests/test_packaging.py`

- [ ] **Step 1: Write packaging test**

Create `apps/desktop/tests/test_packaging.py`:

```python
from pathlib import Path


def test_pyinstaller_spec_exists_and_names_app():
    spec = Path("packaging/tailclose-screener.spec")
    text = spec.read_text(encoding="utf-8")
    assert "tailclose-screener" in text
    assert "tailclose_desktop/main.py" in text.replace("\\\\", "/")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
cd apps/desktop
pytest tests/test_packaging.py
```

Expected: FAIL because spec file does not exist.

- [ ] **Step 3: Add PyInstaller spec**

Create `apps/desktop/packaging/tailclose-screener.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("akshare") + collect_submodules("baostock")

a = Analysis(
    ["../tailclose_desktop/main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="tailclose-screener",
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="tailclose-screener",
)
```

- [ ] **Step 4: Update README packaging instructions**

Append to `apps/desktop/README.md`:

```md
## Package

```powershell
cd apps/desktop
pyinstaller packaging/tailclose-screener.spec
```

The packaged app will be created under `apps/desktop/dist/tailclose-screener/`.
```

- [ ] **Step 5: Verify packaging test passes**

Run:

```powershell
cd apps/desktop
pytest tests/test_packaging.py
```

Expected: PASS.

- [ ] **Step 6: Commit packaging**

Run:

```bash
git add apps/desktop/packaging apps/desktop/README.md apps/desktop/tests/test_packaging.py
git commit -m "chore: add desktop packaging config"
```

## Task 8: Final Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update root README direction**

Modify `README.md` so it says the repository contains both:

```md
## Apps

- `apps/desktop`: Windows desktop EXE direction with AkShare/baostock data providers.
- root PWA: earlier Cloudflare Pages prototype retained for reference.
```

- [ ] **Step 2: Run full desktop tests**

Run:

```powershell
cd apps/desktop
pytest
```

Expected: all desktop tests pass.

- [ ] **Step 3: Run existing PWA tests and build**

Run:

```powershell
npm test
npm run build
```

Expected: existing PWA tests and build still pass.

- [ ] **Step 4: Optional package smoke**

Run when dependencies and time allow:

```powershell
cd apps/desktop
pyinstaller packaging/tailclose-screener.spec
```

Expected: `dist/tailclose-screener/tailclose-screener.exe` exists.

- [ ] **Step 5: Commit README update**

Run:

```bash
git add README.md
git commit -m "docs: document desktop app direction"
```

- [ ] **Step 6: Push**

Run:

```bash
git push origin main
```

Expected: push succeeds.

## Self-Review Notes

- Spec coverage: Windows desktop app, AkShare provider adapter, baostock provider adapter, sample fallback, strategy engine, Feishu formatting, storage shell, UI shell, and packaging config are represented.
- First version keeps live provider usage behind adapters; tests rely on sample data and normalization to avoid network flakiness.
- Full baostock backtest analytics remain out of scope for the first desktop implementation.
