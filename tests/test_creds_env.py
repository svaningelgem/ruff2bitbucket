import sys

import pytest

from ruff2bitbucket.credentials import AutoCredentials, UserPass, get_credentials


@pytest.fixture(autouse=True)
def _setup_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "CREDUSR", "--passvar", "CREDPWD"])
    monkeypatch.setenv("CREDUSR", "USER")
    monkeypatch.setenv("CREDPWD", "PASS")


def test_envcred() -> None:
    sut = get_credentials()
    assert len(sut) == 1
    assert next(iter(sut)) == UserPass("USER", "PASS")


def test_envcred_invalid_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CREDUSR")

    with pytest.raises(ValueError, match="No username found"):
        len(get_credentials())


def test_envcred_invalid_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CREDPWD")

    with pytest.raises(ValueError, match="No password found"):
        len(get_credentials())
