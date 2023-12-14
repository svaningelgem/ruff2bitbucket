import distutils.spawn
import logging
import re
from typing import Iterable

from .common import CapturedLine, run

__all__ = ["check_code_mistakes", "check_formatting"]


capturer = re.compile(r"^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*(?P<description>.*)$", flags=re.IGNORECASE)
formater = re.compile(r"^(?P<description>Would reformat):?\s*(?P<filename>.*?)$", flags=re.IGNORECASE)
logger = logging.getLogger(__name__)


def has_executable(name: str) -> bool:
    return distutils.spawn.find_executable(name) is not None


def yield_from_regex(*cmd: str, regex_to_use: re.Pattern) -> Iterable[CapturedLine]:
    output = run(*cmd, check=False)
    for line in output.stdout.strip().splitlines():
        if match := regex_to_use.match(line):
            yield CapturedLine(**match.groupdict())


def check_code_mistakes() -> Iterable[CapturedLine]:
    """
    Yields a list of detected errors in the files.
    Falls back to flake8 if ruff doesn't exist on the system (which it should, as it's a dependency of this package!).
    """

    if has_executable("ruff"):
        yield from yield_from_regex("ruff", "check", "--no-fix", ".", regex_to_use=capturer)
    # elif has_executable("flake8"):
    #     yield from yield_from_regex("flake8", ".", regex_to_use=capturer)
    else:
        logger.warning("No code validation is done as ruff is not available.")


def check_formatting() -> Iterable[CapturedLine]:
    """
    Yields a list of files that would be reformatted.
    Falls back to black if ruff isn't there.
    """

    if has_executable("ruff"):
        yield from yield_from_regex("ruff", "format", "--check", ".", regex_to_use=formater)
    else:
        logger.warning("No format check is done because ruff is not available.")
