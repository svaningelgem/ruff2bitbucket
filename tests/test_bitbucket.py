import subprocess

import pytest
from pytest_mock import MockerFixture
from ruff2bitbucket.bitbucket import get_repo_info


def test_get_repo_info(mocker: MockerFixture) -> None:
    class Dummy:
        ...

    mocker.patch("ruff2bitbucket.bitbucket.RepoInfo", new=Dummy)

    sut = get_repo_info()
    assert isinstance(sut, Dummy)
    assert sut is get_repo_info(), "I expect the call to be cached!"


def test_repo_info_happy_flow() -> None:
    sut = get_repo_info()

    assert (
        sut.annotations_endpoint
        == "https://localhost:12345/rest/insights/latest/projects/abc/repos/repository/commits/abcde_commit_hash_fghij/reports/ruff2bitbucket/annotations"
    )
    assert sut.commit_id == "abcde_commit_hash_fghij"
    assert sut.commit_url == "https://localhost:12345/projects/abc/repos/repository/commits/abcde_commit_hash_fghij"
    assert sut.repo_key == "abc"
    assert sut.repo_slug == "repository"
    assert (
        sut.report_endpoint
        == "https://localhost:12345/rest/insights/latest/projects/abc/repos/repository/commits/abcde_commit_hash_fghij/reports/ruff2bitbucket"
    )


def test_repo_info_happy_flow_2(mocker: MockerFixture) -> None:
    import ruff2bitbucket.git

    old_run = ruff2bitbucket.git.run

    def local_run(*cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        if cmd == ("git", "config", "--get", "remote.origin.url"):
            return subprocess.CompletedProcess(
                "",
                0,
                "https://localhost:12345/projects/def/repos/some_repo/some_other_text\n\n",
                "",
            )
        return old_run(*cmd, check=check)

    mocker.patch("ruff2bitbucket.git.run", new=local_run)
    sut = get_repo_info()

    assert sut.annotations_endpoint == (
        "https://localhost:12345/rest/insights/latest/projects/def/repos/"
        "some_repo/commits/abcde_commit_hash_fghij/reports/ruff2bitbucket/annotations"
    )
    assert sut.commit_id == "abcde_commit_hash_fghij"
    assert sut.commit_url == "https://localhost:12345/projects/def/repos/some_repo/commits/abcde_commit_hash_fghij"
    assert sut.repo_key == "def"
    assert sut.repo_slug == "some_repo"
    assert sut.report_endpoint == (
        "https://localhost:12345/rest/insights/latest/projects/def/repos/"
        "some_repo/commits/abcde_commit_hash_fghij/reports/ruff2bitbucket"
    )


def test_repo_info_github_url(mocker: MockerFixture) -> None:
    mocker.patch(
        "ruff2bitbucket.git.run",
        return_value=subprocess.CompletedProcess("", 0, "https://github.com/user/repo.git"),
    )

    with pytest.raises(ValueError, match=r"Couldn't interpret 'https://github.com/user/repo.git' as a BitBucket url"):
        get_repo_info()


def test_repo_info_no_url(mocker: MockerFixture) -> None:
    mocker.patch("ruff2bitbucket.git.run", return_value=subprocess.CompletedProcess("", 0, ""))

    with pytest.raises(ValueError, match=r"No git has been set up"):
        get_repo_info()
