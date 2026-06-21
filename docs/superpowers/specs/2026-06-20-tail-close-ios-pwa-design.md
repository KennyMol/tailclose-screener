# Tail Close iOS PWA Design

## Goal

Build a mobile-first stock screening web app for iPhone. The user opens a public URL in Safari, optionally adds it to the iOS home screen, selects a strategy, taps refresh, and sees stocks that currently match the selected strategy.

This app is a screening and observation tool only. It must not present results as investment advice.

## Target User Flow

1. User opens the public app URL on iPhone.
2. Home screen shows a strategy selector and a refresh button.
3. User taps refresh.
4. App fetches current market data through the backend.
5. Backend evaluates the selected strategy.
6. App displays matching stocks in a compact list.
7. User can open secondary screens for strategy parameters, custom conditions, and backtesting.

## Main Interface

The main screen is intentionally minimal:

- Strategy selector.
- Refresh button.
- Last refresh time.
- Result list.

Each result item shows:

- Stock code.
- Stock name.
- Latest price when available.
- Percentage change.
- Volume ratio when available.
- Trigger reason.

Secondary features are not shown on the main screen. They live behind menu or tab actions:

- Strategy settings.
- Custom condition strategy.
- Backtest.

No Excel export is included.

## Default Strategy

The default "tail close buy" strategy uses configurable conditions:

- Exclude ST, suspended, delisting-risk, and invalid quote stocks when data allows.
- Percentage change between 0% and 6%.
- Volume ratio greater than 1.2 when available.
- Turnover in a moderate range when available.
- Price above or near 5-day, 10-day, or 20-day moving averages when historical data is available.
- Prefer active late-session trading when intraday data is available.

The strategy engine returns a match result with reasons instead of only true or false, so the UI can explain why each stock appeared.

## Custom Strategy

The first version should use a condition editor instead of arbitrary code execution.

Supported condition types:

- Numeric comparison: greater than, less than, between.
- Boolean filters: exclude ST, exclude suspended.
- Moving average relation: price above or near selected moving average.
- Logical all-match grouping for version one.

This keeps the mobile UI understandable and avoids executing user-supplied code.

## Backtesting

Backtesting uses the currently selected strategy and a selected date range.

Backtest output should be compact:

- Number of trade signals.
- Win rate when exit logic is available.
- Average return.
- Maximum drawdown if enough data exists.
- List of historical signal dates and matching stocks.

For the first implementation, backtesting can be limited by the chosen free data source. If historical data is incomplete, the UI should state which metrics are unavailable.

## Data Architecture

Use a backend layer between the mobile app and market data sources.

Reasons:

- Avoid browser CORS problems.
- Hide API keys if a paid data source is added later.
- Normalize quote fields from different providers.
- Keep strategy calculations consistent.

Core backend endpoints:

- `GET /api/strategies`
- `GET /api/screen?strategyId=...`
- `POST /api/strategies/custom`
- `POST /api/backtest`

The first version may use a free or public data source for validation. The data provider must be abstracted behind a provider interface so it can be replaced later.

## Deployment

Preferred deployment:

- Cloudflare Pages or Vercel for the mobile web app.
- Serverless functions or Workers for API endpoints.

The first version should stay within free-tier-friendly limits. A custom domain is optional and not required for launch.

## Error Handling

The app should show short, plain messages:

- Data source unavailable.
- Refresh failed.
- No stocks matched the current strategy.
- Some fields are unavailable from the current data source.
- Backtest range is too large or unavailable.

The app must degrade gracefully when volume ratio, turnover, or moving average data is missing.

## Testing

Test the strategy engine separately from the UI.

Required coverage:

- Default strategy includes matching stock.
- Default strategy excludes stocks with out-of-range percentage change.
- Default strategy excludes ST/suspended stocks when flags exist.
- Condition editor evaluates numeric comparisons.
- Screen endpoint returns reasons for matches.
- UI renders empty, loading, error, and result states.

Manual verification:

- iPhone-sized viewport.
- Safari/PWA layout.
- Refresh flow.
- Strategy switch flow.
- Backtest flow.

## Out of Scope

- Windows `.exe`.
- Excel export.
- Brokerage trading or order placement.
- Investment recommendation language.
- Arbitrary user code execution.
- Guaranteed real-time exchange-grade market feed in the free first version.
