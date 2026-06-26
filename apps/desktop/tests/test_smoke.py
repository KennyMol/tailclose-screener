from tailclose_desktop.main import main


def test_main_prints_app_name_and_returns_zero(capsys):
    result = main()

    captured = capsys.readouterr()
    assert result == 0
    assert "Tailclose Desktop" in captured.out
