from __future__ import annotations

import contextlib
import os
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import product
from typing import ClassVar, Iterator, List, Tuple

__all__ = ["UserPass", "get_credentials"]


@dataclass(frozen=True)
class UserPass:
    username: str = ""
    password: str = ""

    def __post_init__(self) -> None:
        super().__setattr__("username", (self.username or "").strip())
        super().__setattr__("password", (self.password or "").strip())

        if not self.username:
            raise ValueError(
                "No username found. Please check the 'SECURITY' section in the readme on how to provide one."
            )

        if not self.password:
            raise ValueError(
                "No password found. Please check the 'SECURITY' section in the readme on how to provide one."
            )

    def as_tuple(self) -> Tuple[str, str]:
        return self.username, self.password


@dataclass
class Credentials(ABC):
    _correct_combination: UserPass | None = field(default=None, init=False)

    @property
    @abstractmethod
    def _up(self) -> List[UserPass]:
        """returns the enumeration of possible user/pass combinations"""

    def __len__(self) -> int:
        """Gets back the amount of user/pass/token/... to try. Most likely just 1."""
        if self._correct_combination:
            return 1

        return len(self._up)

    def __iter__(self) -> Iterator[UserPass]:
        """Returns the user/pass to pass on to BitBucket."""
        if self._correct_combination:
            yield self._correct_combination
        else:
            yield from self._up

    def report_correct_combination(self, combo: UserPass) -> None:
        self._correct_combination = combo


@dataclass
class AutoCredentials(Credentials):
    potential_user_envvars: ClassVar[Tuple[str, ...]] = ("USER", "USR")
    potential_pass_envvars: ClassVar[Tuple[str, ...]] = ("PASS", "PW", "PWD", "PASSWORD")

    @property
    def _up(self) -> List[UserPass]:
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

        values = []
        for (user_var, user_prefix), (pass_var, pass_prefix) in product(user_vars, pass_vars):
            if user_prefix != pass_prefix:
                continue

            with contextlib.suppress(ValueError):
                values.append(UserPass(os.getenv(user_var), os.getenv(pass_var)))

        return values


@dataclass
class UserPassCredentials(Credentials):
    user: str
    pass_: str

    @property
    def _up(self) -> List[UserPass]:
        return [UserPass(self.user, self.pass_)]


@dataclass
class EnvCredentials(Credentials):
    user: str
    passvar: str

    @property
    def _up(self) -> List[UserPass]:
        return [UserPass(os.getenv(self.user), os.getenv(self.passvar))]


@dataclass
class TokenCredentials(Credentials):
    user: str
    token: str

    @property
    def _up(self) -> List[UserPass]:
        return [UserPass(self.user, self.token)]


@dataclass
class KeyringCredentials(Credentials):
    user: str
    service_name: str

    @property
    def _up(self) -> List[UserPass]:
        try:
            from keyring import get_password
        except ImportError:
            raise ValueError(
                "Couldn't import the 'keyring' package."
                " Did you install it (`poetry install -E keyring` or `poetry add ruff2bitbucket[keyring]`)?"
            ) from None

        return [UserPass(self.user, get_password(self.service_name, self.user))]


@lru_cache(1)
def get_credentials() -> Credentials:
    parser = ArgumentParser()

    parser.add_argument("--user", help="Username (or username env var) for authentication", default=None, nargs="?")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--pass", help="Password used for authentication", default=None, dest="pass_")
    group.add_argument("--token", help="BitBucket API token used for authentication", default=None)
    group.add_argument("--service_name", help="Service name for keyring authentication", default=None)
    group.add_argument("--passvar", help="Environment variable for password", default=None)

    args = parser.parse_args()

    if args.pass_:
        return UserPassCredentials(args.user, args.pass_)
    if args.token:
        return TokenCredentials(args.user, args.token)
    if args.service_name:
        return KeyringCredentials(args.user, args.service_name)
    if args.passvar:
        return EnvCredentials(args.user, args.passvar)

    if args.user:
        raise ValueError(
            "I found a user without an authentication method?"
            " Please provide one, or remove for automatic envvar checking."
        )

    return AutoCredentials()
