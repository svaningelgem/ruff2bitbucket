from __future__ import annotations

import os
from argparse import ArgumentParser
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import product
from typing import ClassVar, Iterator

__all__ = ["get_credentials"]


@dataclass
class Credentials:
    correct_combinations: list[tuple[str, str]] = field(default_factory=list)

    potential_user_envvars: ClassVar[tuple[str, ...]] = ("USER", "USR")
    potential_pass_envvars: ClassVar[tuple[str, ...]] = ("PASS", "PW", "PWD", "PASSWORD")

    _correct_combination: tuple[str, str] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        user_vars = [
            (user_var, user_var[: -len(ending)])
            for user_var in os.environ
            for ending in self.potential_user_envvars
            if user_var.endswith(ending)
        ]
        pass_vars = [
            (pass_var, pass_var[: -len(ending)])
            for pass_var in os.environ
            for ending in self.potential_pass_envvars
            if pass_var.endswith(ending)
        ]

        for (user_var, user_prefix), (pass_var, pass_prefix) in product(user_vars, pass_vars):
            if user_prefix != pass_prefix:
                continue

            self.correct_combinations.append((os.getenv(user_var), os.getenv(pass_var)))

    def __len__(self) -> int:
        if self._correct_combination:
            return 1
        return len(self.correct_combinations)

    def __iter__(self) -> Iterator[tuple[str, str]]:
        if self._correct_combination:
            yield self._correct_combination
        else:
            yield from self.correct_combinations

    def report_correct_combination(self, combo: tuple[str, str]) -> None:
        self._correct_combination = combo


@lru_cache(1)
def get_credentials() -> Credentials:
    parser = ArgumentParser()

    parser.add_argument("--user", help="Specify a username", default=None, nargs="?")
    parser.add_argument("--pass", help="Specify a password", default=None, nargs="?")
    args = parser.parse_args()

    creds = Credentials()
    potential = (args.user, getattr(args, "pass"))  # I don't know how they do this... Isn't `pass` a reserved keyword??
    if all(potential):
        creds.report_correct_combination(potential)

    return creds
