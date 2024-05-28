import sys
import types

import pytest
from pytest_mock import MockerFixture
from ruff2bitbucket.credentials import UserPass, get_credentials


def test_keyring_cred(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "USER", "--service_name", "system"])
    mocker.patch("keyring.get_password", return_value="PASS")

    sut = get_credentials()
    assert len(sut) == 1
    assert next(iter(sut)) == UserPass("USER", "PASS")


def test_keyring_cred_no_keyring_available(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "USER", "--service_name", "system"])

    def custom_import(name: str, *args: object, **kwargs: object) -> types.ModuleType:
        if name == "keyring":
            raise ImportError
        return original_import(name, *args, **kwargs)

    original_import = __import__

    mocker.patch("builtins.__import__", side_effect=custom_import)

    sut = get_credentials()
    with pytest.raises(ValueError, match="Couldn't import the 'keyring' package"):
        len(sut)
