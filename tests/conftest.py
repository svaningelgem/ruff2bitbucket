import subprocess

import pytest
from pytest_mock import MockerFixture
from ruff2bitbucket.bitbucket import get_repo_info
from ruff2bitbucket.credentials import get_credentials
from ruff2bitbucket.git import get_current_git_commit_hash, get_current_repo_uri


@pytest.fixture(autouse=True)
def _inject_run_commands(mocker: MockerFixture) -> None:
    def local_run(*cmd: str, check: bool) -> subprocess.CompletedProcess:
        if cmd == ("git", "config", "--get", "remote.origin.url"):
            assert check is True
            return subprocess.CompletedProcess("", 0, "https://localhost:12345/scm/abc/repository.git\n\n", "")

        if cmd == ("git", "rev-parse", "HEAD"):
            assert check is True
            return subprocess.CompletedProcess("", 0, "abcde_commit_hash_fghij\n\n", "")

        raise ValueError(f"Unknown call to: {cmd}")

    mocker.patch("ruff2bitbucket.git.run", new=local_run)
    mocker.patch("ruff2bitbucket.capturer.run", new=local_run)


@pytest.fixture(autouse=True)
def _cleanup_caches() -> None:
    yield

    get_credentials.cache_clear()
    get_repo_info.cache_clear()
    get_current_git_commit_hash.cache_clear()
    get_current_repo_uri.cache_clear()


@pytest.fixture(autouse=True)
def _cleanup_get_repo_info_cache() -> None:
    return
