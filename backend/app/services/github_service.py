"""GitHub service for URL parsing, validation, and repository metadata."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.core.errors import (
    BranchNotFoundError,
    InvalidRepositoryURLError,
    RateLimitError,
    RepositoryNotFoundError,
)
from app.core.logging import logger


# Strict pattern: github.com/owner/repo with optional /tree/branch...
_GITHUB_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9\-_.]+)/(?P<repo>[A-Za-z0-9\-_.]+?)(?:\.git)?(?:/tree/(?P<branch>.+))?$"
)


def parse_github_url(url: str) -> tuple[str, str, str | None]:
    """
    Parse a GitHub repository URL.

    Returns (owner, repo, branch_or_None).
    Supports branch names containing slashes (e.g., feature/my-branch).
    """
    url = url.strip().rstrip("/")
    parsed = urlparse(url)

    # Security: only allow github.com
    if parsed.hostname not in ("github.com", "www.github.com"):
        raise InvalidRepositoryURLError(url)

    match = _GITHUB_URL_RE.match(url)
    if not match:
        raise InvalidRepositoryURLError(url)

    owner = match.group("owner")
    repo = match.group("repo")
    branch = match.group("branch")  # None if not present

    if not owner or not repo:
        raise InvalidRepositoryURLError(url)

    # Strip trailing slashes from branch
    if branch:
        branch = branch.strip("/")
        if not branch:
            branch = None

    return owner, repo, branch


async def verify_repository(owner: str, repo: str) -> dict:
    """Verify that a repository exists and is accessible."""
    settings = get_settings()
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
        )

    if resp.status_code == 404:
        raise RepositoryNotFoundError(owner, repo)
    if resp.status_code == 403:
        remaining = resp.headers.get("x-ratelimit-remaining", "?")
        if remaining == "0":
            raise RateLimitError()
        raise RepositoryNotFoundError(owner, repo)
    if resp.status_code != 200:
        raise RepositoryNotFoundError(owner, repo)

    data = resp.json()
    return {
        "default_branch": data.get("default_branch", "main"),
        "description": data.get("description", ""),
        "full_name": data.get("full_name", f"{owner}/{repo}"),
    }


async def verify_branch(owner: str, repo: str, branch: str) -> bool:
    """Verify that a branch exists in the repository."""
    settings = get_settings()
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}",
            headers=headers,
        )

    if resp.status_code == 404:
        raise BranchNotFoundError(branch, owner, repo)
    if resp.status_code == 403:
        remaining = resp.headers.get("x-ratelimit-remaining", "?")
        if remaining == "0":
            raise RateLimitError()

    return resp.status_code == 200


def build_github_file_url(owner: str, repo: str, branch: str, file_path: str,
                           start_line: int | None = None, end_line: int | None = None) -> str:
    """Build a GitHub URL pointing to a specific file, optionally with line anchors."""
    base = f"https://github.com/{owner}/{repo}/blob/{branch}/{file_path}"
    if start_line is not None and end_line is not None:
        return f"{base}#L{start_line}-L{end_line}"
    if start_line is not None:
        return f"{base}#L{start_line}"
    return base
