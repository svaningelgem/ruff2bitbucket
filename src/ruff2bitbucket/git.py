from functools import lru_cache

from .common import run

__all__ = ["get_current_git_commit_hash", "get_current_repo_uri"]


@lru_cache(1)
def get_current_git_commit_hash() -> str:
    return run("git", "rev-parse", "HEAD", check=True).stdout.strip()


@lru_cache(1)
def get_current_repo_uri() -> str:
    return run("git", "config", "--get", "remote.origin.url", check=True).stdout.strip()
