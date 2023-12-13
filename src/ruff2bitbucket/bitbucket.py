"""
https://developer.atlassian.com/server/bitbucket/rest/v815/api-group-builds-and-deployments/#api-insights-latest-projects-projectkey-repos-repositoryslug-commits-commitid-reports-key-annotations-post
"""

import re
from functools import lru_cache
from urllib.parse import urlparse

from .git import get_current_git_commit_hash, get_current_repo_uri

__all__ = ["get_repo_info"]


class RepoInfo:
    def __init__(self) -> None:
        url = get_current_repo_uri()
        if not url:
            raise ValueError("No git has been set up, so we can't upload anything to BitBucket.")

        self.parse_result = urlparse(url)

        match = re.search(r"/scm/(?P<key>.*?)/(?P<slug>.*?)\.git", self.parse_result.path, re.IGNORECASE)
        if not match:
            match = re.search(
                r"/projects/(?P<key>.*?)/repos/(?P<slug>.*?)[/\\.].*$",
                self.parse_result.path,
                re.IGNORECASE,
            )

        if not match:
            raise ValueError(
                f"Couldn't interpret '{url}' as a BitBucket url. Please file an issue if this is in error!"
            )

        self.repo_key = match.group(1)
        self.repo_slug = match.group(2)
        self.commit_id = get_current_git_commit_hash()

    @property
    def report_endpoint(self) -> str:
        return (
            f"{self.parse_result.scheme}://{self.parse_result.netloc}/rest/insights/latest/projects/{self.repo_key}"
            f"/repos/{self.repo_slug}/commits/{self.commit_id}/reports/ruff2bitbucket"
        )

    @property
    def annotations_endpoint(self) -> str:
        return self.report_endpoint + "/annotations"

    @property
    def commit_url(self) -> str:
        return (
            f"{self.parse_result.scheme}://{self.parse_result.netloc}/projects/{self.repo_key}"
            f"/repos/{self.repo_slug}/commits/{self.commit_id}"
        )


@lru_cache(1)
def get_repo_info() -> RepoInfo:
    return RepoInfo()
