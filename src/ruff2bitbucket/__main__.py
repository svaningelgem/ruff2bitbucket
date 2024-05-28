import json
import logging
import sys
from itertools import chain
from typing import List

import requests

from .bitbucket import get_repo_info
from .capturer import check_code_mistakes, check_formatting
from .common import CapturedLine
from .credentials import get_credentials

__all__ = ["main"]

logger = logging.getLogger(__name__)


def bitbucket_upload(upload_uri: str, report: dict, name: str, error_code: int) -> None:
    for credential in get_credentials():
        response = requests.put(upload_uri, json=report, auth=credential.as_tuple())
        if response.status_code == 401:  # Unauthorized
            continue

        get_credentials().report_correct_combination(credential)

        if response.status_code == error_code:
            logger.warning("'PUT %s' reported one or more errors:", upload_uri)
            text = json.dumps(response.json(), indent=4).splitlines()
            for line in text:
                logger.warning("%s", line)
        break  # But my authentication user was right, so we will stop here
    else:
        logger.error("Cannot upload the %s to bitbucket. No valid user/pass found.", name)
        sys.exit(1)


def upload_code_insights(upload_uri: str, captured_lines: List[CapturedLine]) -> None:
    annotations = []
    for message in captured_lines[:1_000]:  # Bitbucket can receive at most 1000 annotations
        annotations.append(
            {
                "reportKey": "ruff2bitbucket",
                "path": message.filename,
                "line": message.line,
                "message": message.description,
                "severity": "LOW",
                "type": "CODE_SMELL",
            }
        )

    bitbucket_upload(upload_uri, report={"annotations": annotations}, name="annotations", error_code=404)


def upload_code_statistics(upload_uri: str, captured_lines: List[CapturedLine]) -> None:
    need_reformat = sum(1 for cl in captured_lines if "reformat" in cl.description)

    report = {
        "result": "FAIL" if captured_lines else "PASS",
        "title": "ruff report",
        "reporter": "ruff2bitbucket",
        "report_type": "CODE_SMELL",
        "data": [
            {
                "title": "Need reformat",
                "type": "NUMBER",
                "value": need_reformat,
            },
            {
                "title": "Issue count",
                "type": "NUMBER",
                "value": len(captured_lines) - need_reformat,
            },
        ],
    }

    bitbucket_upload(upload_uri, report=report, name="report", error_code=400)


def main() -> None:
    logging.basicConfig()

    creds = get_credentials()
    if not creds:
        logger.error("No valid credentials found.")
        sys.exit(1)

    captured_lines = list(chain(check_code_mistakes(), check_formatting()))

    if not captured_lines:
        logger.info("no errors detected. No report will be uploaded.")
        sys.exit(0)

    upload_code_statistics(get_repo_info().report_endpoint, captured_lines)
    upload_code_insights(get_repo_info().annotations_endpoint, captured_lines)

    logger.info("reports were succesfully uploaded:\n%s", get_repo_info().commit_url)
