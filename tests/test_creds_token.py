import sys

import pytest
from ruff2bitbucket.credentials import UserPass, get_credentials


def test_tokencred(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "USER", "--token", "TOKEN"])

    sut = get_credentials()
    assert len(sut) == 1
    assert next(iter(sut)) == UserPass("USER", "TOKEN")
