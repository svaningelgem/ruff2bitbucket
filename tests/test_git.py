# Not much to test in here...
from subprocess import CompletedProcess

import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from ruff2bitbucket.git import get_current_git_commit_hash, get_current_repo_uri


@pytest.fixture()
def mock_run(mocker: MockerFixture) -> MockType:
    return mocker.patch("ruff2bitbucket.git.run", return_value=CompletedProcess("", 0, "abc", "def"))


def test_get_current_git_commit_hash(mock_run: MockType) -> None:
    assert get_current_git_commit_hash() == "abc"
    mock_run.assert_called_once_with("git", "rev-parse", "HEAD", check=True)

    mock_run.reset_mock()

    assert get_current_git_commit_hash() == "abc"
    mock_run.assert_not_called()


def test_get_current_repo_uri(mock_run: MockType) -> None:
    assert get_current_repo_uri() == "abc"
    mock_run.assert_called_once_with("git", "config", "--get", "remote.origin.url", check=True)

    mock_run.reset_mock()

    assert get_current_repo_uri() == "abc"
    mock_run.assert_not_called()
