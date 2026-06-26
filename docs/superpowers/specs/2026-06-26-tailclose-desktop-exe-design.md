# Tailclose Desktop EXE Design

## Goal

Build a Windows 64-bit desktop screening tool for tail-close stock selection. The user runs a local `.exe`, selects a strategy, clicks refresh, and sees matching A-share stocks in the window.

The desktop version replaces the previous mobile-first deployment direction for the main product path. The existing PWA code can remain in the repository, but new work should live under `apps/desktop`.

This is a screening and observation tool only. It must not present results as investment advice.

## Platform

- Windows 64-bit.
- Python application packaged with PyInstaller.
- Desktop UI built with PySide6.
- Local data/cache stored under the user's app data directory.

## Main User Flow

1. User runs `tailclose-screener.exe`.
2. App opens a compact desktop window.
3. User selects a strategy.
4. User clicks refresh.
5. App loads market data through the local data providers.
6. App evaluates the selected strategy.
7. App displays matching stocks in the result table.

## Main Interface

The main window stays minimal:

- Strategy selector.
- Refresh button.
- Result table.
- Last data update status.

Result table columns:

- Code.
- Name.
- Price.
- Change percent.
- Volume ratio when available.
- Reason.

Secondary features live in menus or dialogs:

- Strategy parameters.
- Backtest.
- Data update.
- Feishu notification settings.

No Excel export is included in the first desktop version.

## Data Providers

Use Python data providers with a common interface.

Provider responsibilities:

- Normalize raw quote fields into internal data models.
- Handle provider failures with clear error messages.
- Allow fallback from one provider to another when possible.

First implementation providers:

- AkShare provider for current A-share quote data and market fields when available.
- baostock provider for historical K-line data, moving averages, and backtest support.
- Sample provider for tests and offline fallback.

## Strategy Engine

The desktop app should reuse the same conceptual strategy rules as the PWA:

- Exclude ST, suspended, delisting-risk, and invalid quote stocks when data allows.
- Percentage change between 0% and 6%.
- Volume ratio greater than 1.2 when available.
- Turnover in a moderate range when available.
- Price above or near 5-day, 10-day, or 20-day moving averages when historical data is available.
- Prefer active late-session trading when data allows.

The engine returns match reasons so the UI can explain each stock result.

Missing data policy:

- A missing optional field should not automatically exclude a stock.
- A stock must have at least one positive trigger reason before it can appear in results.

## Backtesting

Backtesting uses baostock historical data when available.

First version scope:

- Select strategy.
- Select date range.
- Show signal count.
- Show compact historical signal list.
- If exit-price data is insufficient, clearly state that return metrics are unavailable.

Full performance analytics can come later.

## Local Storage

Use SQLite for local state:

- Strategy parameter presets.
- Provider update metadata.
- Cached stock universe.
- Optional cached daily K-line data.
- Feishu notification settings.

Sensitive settings such as webhook URLs should not be logged.

## Feishu Notification Support

First desktop version includes Feishu support as a local settings module:

- Webhook URL input.
- Test send button.
- Optional "send after refresh" toggle.
- Optional top-N limit for pushed results.

Default behavior:

- Auto-send is off.
- Manual test send is available.

Message content:

- Strategy name.
- Refresh time.
- Matching stock list.
- Risk notice that results are only for screening and observation.

## Packaging

Package with PyInstaller.

Expected deliverables:

- `dist/tailclose-screener/tailclose-screener.exe`, or a single-file exe if startup time is acceptable.
- Clear local run instructions.
- Clear package command.

AkShare, baostock, pandas, PySide6, requests, and PyInstaller dependencies must be captured in the packaging configuration.

## Error Handling

The UI should show plain Chinese messages:

- 数据源不可用。
- 刷新失败。
- 当前没有符合策略的股票。
- baostock 登录失败。
- 飞书测试发送失败。
- 部分字段缺失，结果仅基于可用字段筛选。

Errors should not crash the app.

## Testing

Required automated tests:

- Strategy includes matching sample stock.
- Strategy excludes out-of-range change percent.
- Strategy excludes ST/suspended/delisting-risk stocks.
- Strategy excludes quotes with no positive reason.
- Provider normalization maps raw provider rows into internal models.
- Feishu message formatting does not include secrets.
- Backtest summary reports unavailable metrics when historical exits are incomplete.

Manual verification:

- App starts locally.
- Refresh with sample provider.
- Refresh with AkShare when network is available.
- baostock historical query works when login succeeds.
- Feishu test send handles success and failure.
- PyInstaller package starts on Windows.

## Out of Scope

- Broker order placement.
- Real-time exchange-grade quote guarantees.
- Mobile/PWA deployment changes.
- Excel export.
- Arbitrary Python strategy code execution.
- Full quantitative analytics dashboard.
