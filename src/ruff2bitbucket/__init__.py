import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from dataclasses import dataclass, field
from itertools import combinations, product
from typing import ClassVar, Iterator


capturer = re.compile(r'^(?P<filename>.*?):(?P<line>\d+):(?P<column>\d+):\s*(?P<description>.*)$')


@dataclass
class Credentials:
    correct_combinations: list[tuple[str, str]] = field(default_factory=list)

    potential_user_envvars: ClassVar[tuple[str, ...]] = ('USER', 'USR')
    potential_pass_envvars: ClassVar[tuple[str, ...]] = ('PASS', 'PW', 'PWD', 'PASSWORD')

    def __post_init__(self) -> None:
        user_vars = [(user_var, user_var[:-len(ending)]) for user_var in os.environ for ending in self.potential_user_envvars if user_var.endswith(ending)]
        pass_vars = [(pass_var, pass_var[:-len(ending)]) for pass_var in os.environ for ending in self.potential_pass_envvars if pass_var.endswith(ending)]

        for (user_var, user_prefix), (pass_var, pass_prefix) in product(user_vars, pass_vars):
            if user_prefix != pass_prefix:
                continue

            self.correct_combinations.append((user_var, pass_var))

    def __bool__(self) -> bool:
        return len(self.correct_combinations) > 0

    def __iter__(self) -> Iterator[tuple[str, str]]:
        yield from self.correct_combinations


def get_credentials() -> Credentials:
    parser = ArgumentParser()

    parser.add_argument("--user", help="Specify a username", default=None)
    parser.add_argument("--pass", help="Specify a password", default=None)
    args = parser.parse_args()

    creds = Credentials()
    potential = (args.user, getattr(args, 'pass'))  # I don't know how they do this, because `pass` is an Python command??
    if all(potential):
        creds.correct_combinations.insert(0, potential)  # Make it the first

    return creds


def get_current_git_commit_hash() -> str:
    return subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()


@dataclass
class CapturedLine:
    filename: str
    line: int
    column: int
    description: str

    def __post_init__(self):
        self.line_number = int(self.line)
        self.column_number = int(self.column)


def capture_output(*cmd) -> Iterator[CapturedLine]:
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    lines = output.stdout.strip().splitlines()
    for line in lines:
        match = capturer.match(line)
        if not match:
            continue

        yield CapturedLine(**match.groupdict())


def main():
    creds = get_credentials()
    if not creds:
        print("No valid credentials found.")
        sys.exit(1)

    # git_hash = get_current_git_commit_hash()

    list(capture_output("ruff", "check", "--no-fix", "."))
    list(capture_output("ruff", "format", "--check", "."))


if __name__ == '__main__':
    os.environ['TESTUSER'] = 'test'
    os.environ['TESTPWD'] = 'test'
    main()
