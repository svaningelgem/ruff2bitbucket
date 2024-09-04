import pytest

from ruff2bitbucket.credentials import AutoCredentials


def test_autocred_with_empty_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRED_USER", "")
    monkeypatch.setenv("CRED_PASSWORD", "PASS")

    sut = AutoCredentials()
    assert len(sut) == 0


def test_autocred_with_empty_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRED_USER", "USER")
    monkeypatch.setenv("CRED_PASSWORD", "")

    sut = AutoCredentials()
    assert len(sut) == 0
