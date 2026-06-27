# tailclose-screener

Tail-close stock screening tools for A-share observation.

## Apps

- `apps/desktop`: Windows desktop EXE direction with AkShare/Tushare current quotes, baostock/Tushare history providers, manual strategy support foundations, local settings, backtest shell, and Feishu notification module.
- root PWA: earlier Cloudflare Pages prototype retained for reference.

## Desktop App

```powershell
cd apps/desktop
python -m pip install -e ".[dev]"
pytest
python -m tailclose_desktop.main
```

Package as a Windows desktop app:

```powershell
cd apps/desktop
pyinstaller packaging/tailclose-screener.spec
```

The packaged app is created under `apps/desktop/dist/tailclose-screener/`.

## PWA Prototype

```sh
npm install
npm test
npm run build
```

Cloudflare Pages settings for the retained prototype:

- Framework preset: Vite
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `/`

Screening results are for strategy observation only and do not constitute investment advice.
