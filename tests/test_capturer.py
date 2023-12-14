import subprocess

from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from ruff2bitbucket.capturer import check_code_mistakes, check_formatting, has_executable
from ruff2bitbucket.common import CapturedLine


def test_has_executable(mocker: MockerFixture) -> None:
    mocker.patch("distutils.spawn.find_executable", side_effect=lambda x: "abc" if x == "A" else None)

    assert has_executable("A")
    assert not has_executable("B")


def test_code_mistakes(mocker: MockerFixture) -> None:
    mocker.patch(
        "ruff2bitbucket.capturer.run",
        return_value=subprocess.CompletedProcess(
            "",
            0,
            """
src/some_repo/filter/fltr.py:337:21: G004 Logging statement uses f-string
src/some_repo/filter/wrk.py:24:66: Q000 [*] Single quotes found but double quotes preferred
[..]
Found 1592 errors.
[*] 993 fixable with the `--fix` option (218 hidden fixes can be enabled with the `--unsafe-fixes` option).
""",
        ),
    )

    assert list(check_code_mistakes()) == [
        CapturedLine("src/some_repo/filter/fltr.py", 337, 21, "G004 Logging statement uses f-string"),
        CapturedLine("src/some_repo/filter/wrk.py", 24, 66, "Q000 [*] Single quotes found but double quotes preferred"),
    ]


def test_code_mistakes_no_ruff(mocker: MockerFixture, caplog: LogCaptureFixture) -> None:
    mocker.patch("distutils.spawn.find_executable", return_value=None)
    list(check_code_mistakes())
    assert any(
        rec.levelname == "WARNING" and "No code validation is done as ruff is not available" in rec.message
        for rec in caplog.records
    )


def test_check_formatting(mocker: MockerFixture) -> None:
    mocker.patch(
        "ruff2bitbucket.capturer.run",
        return_value=subprocess.CompletedProcess(
            "",
            0,
            """
Would reformat: src/some_repo/filter/fltr.py
Would reformat: src/some_repo/filter/wrk.py
37 files would be reformatted, 9 files left unchanged
""",
        ),
    )

    assert list(check_formatting()) == [
        CapturedLine("src/some_repo/filter/fltr.py", description="Would reformat"),
        CapturedLine("src/some_repo/filter/wrk.py", description="Would reformat"),
    ]


def test_check_formatting_no_ruff(mocker: MockerFixture, caplog: LogCaptureFixture) -> None:
    mocker.patch("distutils.spawn.find_executable", return_value=None)
    list(check_formatting())
    assert any(
        rec.levelname == "WARNING" and "No format check is done because ruff is not available" in rec.message
        for rec in caplog.records
    )
