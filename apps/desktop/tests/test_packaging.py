from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pyinstaller_spec_configures_desktop_executable():
    spec_path = ROOT / "packaging" / "tailclose-screener.spec"

    assert spec_path.exists()
    assert "tailclose-screener" in spec_path.name

    spec_text = spec_path.read_text(encoding="utf-8").replace("\\", "/")
    assert "tailclose_desktop/main.py" in spec_text
    assert "collect_submodules('akshare')" in spec_text
    assert "collect_submodules('baostock')" in spec_text
    assert "name='tailclose-screener'" in spec_text


def test_readme_documents_packaging_command_and_output_path():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Package" in readme
    assert "pyinstaller packaging/tailclose-screener.spec" in readme
    assert "apps/desktop/dist/tailclose-screener/" in readme
