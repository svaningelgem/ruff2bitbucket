import logging
import re

import pytest
from pytest_mock import MockerFixture
from ruff2bitbucket import main


base_url = (
    "https://localhost:12345/rest/insights/latest/projects/abc/repos/"
    "repository/commits/abcde_commit_hash_fghij/reports/ruff2bitbucket"
)


@pytest.fixture(autouse=True)
def _setting_default_credential(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRED_USER", "USER")
    monkeypatch.setenv("CRED_PASSWORD", "PASS")


def test_main_no_credentials(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    mocker.patch("os.environ", new={})

    with pytest.raises(SystemExit) as ex:
        main()

    assert ex.value.code == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "No valid credentials found."


def test_main_no_valid_credentials_found(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    put_mock = mocker.patch("requests.put")
    put_mock.return_value = mocker.Mock(status_code=401)  # UnAuthorized

    with pytest.raises(SystemExit) as ex:
        main()

    assert ex.value.code == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == 'Cannot upload the report to bitbucket. No valid user/pass found.'


def test_main_some_bitbucket_error_happened_on_statistics(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    put_mock = mocker.patch("requests.put")
    put_mock.return_value.status_code = 400
    put_mock.return_value.json.return_value = {'dummy': 123}

    main()

    assert all(rec.levelname == "WARNING" for rec in caplog.records)
    expected = [
        f"'PUT {base_url}' reported one or more errors:",
        "{",
        '    "dummy": 123',
        "}",
    ]

    assert len(caplog.records) == len(expected)
    for idx, message in enumerate(expected):
        assert message == caplog.records[idx].message


def test_main_some_bitbucket_error_happened_on_annotations(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    put_mock = mocker.patch("requests.put")
    put_mock.return_value.status_code = 404
    put_mock.return_value.json.return_value = {'dummy': 123}

    main()

    assert all(rec.levelname == "WARNING" for rec in caplog.records)
    expected = [
        f"'PUT {base_url}/annotations' reported one or more errors:",
        "{",
        '    "dummy": 123',
        "}",
    ]

    assert len(caplog.records) == len(expected)
    for idx, message in enumerate(expected):
        assert message == caplog.records[idx].message


def test_main_no_errors_occurred(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    mocker.patch('ruff2bitbucket.__main__.check_code_mistakes', return_value=[])
    mocker.patch('ruff2bitbucket.__main__.check_formatting', return_value=[])
    put_mock = mocker.patch("requests.put")
    caplog.set_level(logging.INFO)

    with pytest.raises(SystemExit) as ex:
        main()

    assert ex.value.code == 0

    put_mock.assert_not_called()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == "no errors detected. No report will be uploaded."


def test_main_happy_flow(mocker: MockerFixture) -> None:
    put_mock = mocker.patch("requests.put")
    put_mock.return_value = mocker.Mock(status_code=200)

    main()

    assert put_mock.call_count == 2

    put_mock.assert_any_call(
        base_url,
        json={
            "result": "FAIL",
            "title": "ruff report",
            "reporter": "ruff2bitbucket",
            "report_type": "CODE_SMELL",
            "data": [
                {"title": "Need reformat", "type": "NUMBER", "value": 2},
                {"title": "Issue count", "type": "NUMBER", "value": 2},
            ]
        },
        auth=("USER", "PASS"),
    )

    put_mock.assert_any_call(
        f"{base_url}/annotations",
        json={
            "annotations": [
                {
                    "reportKey": "ruff2bitbucket",
                    "path": "src/some_repo/filter/fltr.py",
                    "line": 337,
                    "message": "G004 Logging statement uses f-string",
                    "severity": "LOW",
                    "type": "CODE_SMELL",
                },
                {
                    "reportKey": "ruff2bitbucket",
                    "path": "src/some_repo/filter/wrk.py",
                    "line": 24,
                    "message": "Q000 [*] Single quotes found but double quotes preferred",
                    "severity": "LOW",
                    "type": "CODE_SMELL",
                },
                {
                    "reportKey": "ruff2bitbucket",
                    "path": "src/some_repo/filter/fltr.py",
                    "line": 0,
                    "message": "Would reformat",
                    "severity": "LOW",
                    "type": "CODE_SMELL",
                },
                {
                    "reportKey": "ruff2bitbucket",
                    "path": "src/some_repo/filter/wrk.py",
                    "line": 0,
                    "message": "Would reformat",
                    "severity": "LOW",
                    "type": "CODE_SMELL",
                },
            ]
        },
        auth=("USER", "PASS"),
    )
