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

## Package

Build the desktop executable with PyInstaller:

```powershell
pyinstaller packaging/tailclose-screener.spec
```

The packaged application is written to `apps/desktop/dist/tailclose-screener/`.
