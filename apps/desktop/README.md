# Tailclose Desktop

Python desktop application scaffold for Tailclose.

## Development

Install the package with development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
pytest
```

## Tushare

To use the Tushare data source, set your token as an environment variable before launching the app:

```powershell
$env:TUSHARE_TOKEN="your-token"
python -m tailclose_desktop.main
```

The token needs access to the `stock_basic`, `daily`, and `daily_basic` Tushare Pro APIs.

## Package

Build the desktop executable with PyInstaller:

```powershell
pyinstaller packaging/tailclose-screener.spec
```

The packaged application is written to `apps/desktop/dist/tailclose-screener/`.
