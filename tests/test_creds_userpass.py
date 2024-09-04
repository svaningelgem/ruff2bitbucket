import pytest

from ruff2bitbucket.credentials import UserPass


def test_userpass_no_password() -> None:
    with pytest.raises(ValueError, match="No password found"):
        UserPass(username="Bumba")


def test_userpass_no_username() -> None:
    with pytest.raises(ValueError, match="No username found"):
        UserPass(password="Bumba")
