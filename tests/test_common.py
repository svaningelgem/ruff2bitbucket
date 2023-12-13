import subprocess

from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType
from ruff2bitbucket.common import CapturedLine, run


def test_run(mocker: MockerFixture) -> None:
    run_mock: MockType = mocker.patch("subprocess.run", return_value="abc")

    assert run("a", "b", check=True) == "abc"
    run_mock.assert_called_once_with(("a", "b"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

    run_mock.reset_mock()
    assert run("a", "b", check=False) == "abc"
    run_mock.assert_called_once_with(("a", "b"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def test_captured_line_happy_flow() -> None:
    sut = CapturedLine("  file  ", "1", "2", "  desc  ")

    assert sut.filename == "file"
    assert sut.line == 1
    assert sut.column == 2
    assert sut.description == "  desc"


def test_captured_line_default() -> None:
    sut = CapturedLine("  file  ")

    assert sut.filename == "file"
    assert sut.line == 0
    assert sut.column == 0
    assert sut.description == ""
