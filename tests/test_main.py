import pytest
from pytest_mock import MockerFixture
from ruff2bitbucket import main


@pytest.fixture(autouse=True)
def _setting_default_credential(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRED_USER", "USER")
    monkeypatch.setenv("CRED_PASSWORD", "PASS")


def test_main_no_credentials(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    mocker.patch("os.environ", new={})

    with pytest.raises(SystemExit) as ex:
        main()

    assert ex.value.code == 1
    assert any(rec.levelname == "ERROR" and "No valid credentials found." in rec.message for rec in caplog.records)
