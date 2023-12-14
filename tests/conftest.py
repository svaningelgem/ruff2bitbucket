import os
import subprocess
import sys

import pytest
from pytest_mock import MockerFixture
from ruff2bitbucket.bitbucket import get_repo_info
from ruff2bitbucket.credentials import get_credentials
from ruff2bitbucket.git import get_current_git_commit_hash, get_current_repo_uri


@pytest.fixture(autouse=True)
def _credentials_environment_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure that no leakage from the build environment happens to the tests."""

    monkeypatch.setattr(sys, "argv", ["script"])
    monkeypatch.setattr(os, "environ", {})


@pytest.fixture(autouse=True)
def _inject_run_commands(mocker: MockerFixture) -> None:
    def local_run(*cmd: str, check: bool) -> subprocess.CompletedProcess:
        if cmd == ("git", "config", "--get", "remote.origin.url"):
            assert check is True
            return subprocess.CompletedProcess("", 0, "https://localhost:12345/scm/abc/repository.git\n\n")

        if cmd == ("git", "rev-parse", "HEAD"):
            assert check is True
            return subprocess.CompletedProcess("", 0, "abcde_commit_hash_fghij\n\n")

        if cmd == ("ruff", "check", "--no-fix", "."):
            assert check is False
            return subprocess.CompletedProcess(
                "",
                0,
                (
                    "src/some_repo/filter/fltr.py:337:21: G004 Logging statement uses f-string\n"
                    "src/some_repo/filter/wrk.py:24:66: Q000 [*] Single quotes found but double quotes preferred\n"
                    "[..]\n"
                    "Found 1592 errors.\n"
                    "[*] 993 fixable with the `--fix` option (218 hidden fixes can be enabled with the `--unsafe-fixes` option).\n"  # noqa: E501
                ),
            )

        if cmd == ("ruff", "format", "--check", "."):
            assert check is False
            return subprocess.CompletedProcess(
                "",
                0,
                (
                    "Would reformat: src/some_repo/filter/fltr.py\n"
                    "Would reformat: src/some_repo/filter/wrk.py\n"
                    "37 files would be reformatted, 9 files left unchanged\n"
                ),
            )

        raise ValueError(f"Unknown call to: {cmd}")

    mocker.patch("ruff2bitbucket.git.run", new=local_run)
    mocker.patch("ruff2bitbucket.capturer.run", new=local_run)


@pytest.fixture(autouse=True)
def _enable_all_executables(mocker: MockerFixture) -> None:
    mocker.patch("distutils.spawn.find_executable", return_value="I'm there!")


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
