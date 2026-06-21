# tailclose-screener

Mobile-first stock screening app for iPhone.

The planned app lets the user open a public URL in Safari, select a strategy, tap refresh, and see stocks that currently match the selected tail-close screening strategy.

## Current Scope

- iPhone-friendly web app / PWA.
- Minimal main screen: strategy selector, refresh, update time, stock results.
- Strategy settings, custom conditions, and backtesting behind secondary screens.
- No Windows EXE.
- No Excel export.
- Screening and observation only, not investment advice.

## Design

See [docs/superpowers/specs/2026-06-20-tail-close-ios-pwa-design.md](docs/superpowers/specs/2026-06-20-tail-close-ios-pwa-design.md).

## Local Development

```sh
npm install
npm run dev
```

## Build

```sh
npm test
npm run build
```

## Cloudflare Pages

- Framework preset: Vite
- Build command: npm run build
- Build output directory: dist
- Root directory: /

The current app uses sample market data. After choosing a stable market data API, replace the provider implementation in `functions/_shared/provider.ts`.

## iPhone Usage

Open the deployed `pages.dev` URL in Safari. From the share sheet, choose Add to Home Screen to install it like a PWA.
