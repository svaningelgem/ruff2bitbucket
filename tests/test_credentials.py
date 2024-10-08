import sys
from itertools import product

import pytest
from pytest_mock import MockerFixture

from ruff2bitbucket import main
from ruff2bitbucket.credentials import AutoCredentials, UserPass, get_credentials


def test_credentials_is_same_object() -> None:
    assert get_credentials() is get_credentials()


def test_credentials_via_cmdline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "USER", "--pass", "PASS"])
    creds = get_credentials()

    assert len(creds) == 1
    assert creds

    assert next(iter(creds)) == UserPass("USER", "PASS")


def test_no_credentials_from_anywhere() -> None:
    creds = get_credentials()
    assert len(creds) == 0
    assert not creds

    with pytest.raises(StopIteration):
        next(iter(creds))


@pytest.mark.parametrize(
    ("usr", "pwd"),
    product(
        (f"{front}{p}" for p in AutoCredentials.potential_pass_envvars for front in ["CRED", ""]),
        (f"{front}{u}" for u in AutoCredentials.potential_user_envvars for front in ["CRED", ""]),
    ),
)
def test_credentials_in_environment(monkeypatch: pytest.MonkeyPatch, usr: str, pwd: str) -> None:
    monkeypatch.setenv(usr, "USER")
    monkeypatch.setenv(pwd, "PASS")

    has_usr_cred = usr.startswith("CRED")
    has_pwd_cred = pwd.startswith("CRED")

    expected_length = 0 if has_usr_cred ^ has_pwd_cred else 1  # ^ = XOR in python

    assert len(get_credentials()) == expected_length


def test_multiple_creds_incoming_with_argv_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "USER", "--pass", "PASS"])
    monkeypatch.setenv("CREDUSR", "USER1")
    monkeypatch.setenv("CREDPWD", "PASS1")
    monkeypatch.setenv("OTHUSER", "USER2")
    monkeypatch.setenv("OTHPASSWORD", "PASS2")

    assert len(get_credentials()) == 1
    assert next(iter(get_credentials())) == UserPass("USER", "PASS")


def test_multiple_creds_incoming_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CREDUSR", "USER1")
    monkeypatch.setenv("CREDPWD", "PASS1")
    monkeypatch.setenv("OTHUSER", "USER2")
    monkeypatch.setenv("OTHPASSWORD", "PASS2")

    assert len(get_credentials()) == 2

    assert list(get_credentials()) == [UserPass("USER1", "PASS1"), UserPass("USER2", "PASS2")]


def test_creds_get_stored(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRED_USER", "USER")
    monkeypatch.setenv("CRED_PASSWORD", "PASS")

    put_mock = mocker.patch("requests.put")
    put_mock.return_value = mocker.Mock(status_code=200)
    assert get_credentials()._correct_combination is None
    main()
    assert get_credentials()._correct_combination is not None
    main()  # Here this new combination gets used, and we shouldn't crash!


def test_cred_only_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["script", "--user", "USER"])

    with pytest.raises(ValueError, match="I found a user without an authentication method"):
        get_credentials()
