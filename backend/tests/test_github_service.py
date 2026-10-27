"""Tests for GitHub URL parsing and service utilities."""

import pytest
from app.services.github_service import parse_github_url, build_github_file_url
from app.core.errors import InvalidRepositoryURLError


class TestParseGithubUrl:
    """Test GitHub URL parsing with various URL formats."""

    def test_basic_repo_url(self):
        owner, repo, branch = parse_github_url("https://github.com/facebook/react")
        assert owner == "facebook"
        assert repo == "react"
        assert branch is None

    def test_repo_with_trailing_slash(self):
        owner, repo, branch = parse_github_url("https://github.com/facebook/react/")
        assert owner == "facebook"
        assert repo == "react"
        assert branch is None

    def test_repo_with_branch(self):
        owner, repo, branch = parse_github_url("https://github.com/facebook/react/tree/main")
        assert owner == "facebook"
        assert repo == "react"
        assert branch == "main"

    def test_repo_with_slash_branch(self):
        """Branch names containing slashes must be supported."""
        owner, repo, branch = parse_github_url(
            "https://github.com/owner/repo/tree/feature/my-branch"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert branch == "feature/my-branch"

    def test_repo_with_deep_slash_branch(self):
        owner, repo, branch = parse_github_url(
            "https://github.com/owner/repo/tree/feature/v2/experimental"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert branch == "feature/v2/experimental"

    def test_repo_with_git_extension(self):
        owner, repo, branch = parse_github_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_invalid_url_no_github(self):
        with pytest.raises(InvalidRepositoryURLError):
            parse_github_url("https://gitlab.com/owner/repo")

    def test_invalid_url_no_repo(self):
        with pytest.raises(InvalidRepositoryURLError):
            parse_github_url("https://github.com/owner")

    def test_invalid_url_empty(self):
        with pytest.raises(InvalidRepositoryURLError):
            parse_github_url("")

    def test_invalid_url_random(self):
        with pytest.raises(InvalidRepositoryURLError):
            parse_github_url("not a url at all")

    def test_invalid_url_different_host(self):
        with pytest.raises(InvalidRepositoryURLError):
            parse_github_url("https://evil.com/github.com/owner/repo")

    def test_owner_with_hyphens(self):
        owner, repo, _ = parse_github_url("https://github.com/my-org/my-repo")
        assert owner == "my-org"
        assert repo == "my-repo"

    def test_owner_with_dots(self):
        owner, repo, _ = parse_github_url("https://github.com/my.org/my.repo")
        assert owner == "my.org"
        assert repo == "my.repo"


class TestBuildGithubFileUrl:
    """Test GitHub file URL construction."""

    def test_basic_file_url(self):
        url = build_github_file_url("owner", "repo", "main", "src/main.py")
        assert url == "https://github.com/owner/repo/blob/main/src/main.py"

    def test_file_url_with_lines(self):
        url = build_github_file_url("owner", "repo", "main", "src/main.py", 10, 20)
        assert url == "https://github.com/owner/repo/blob/main/src/main.py#L10-L20"

    def test_file_url_with_start_line_only(self):
        url = build_github_file_url("owner", "repo", "main", "src/main.py", 5)
        assert url == "https://github.com/owner/repo/blob/main/src/main.py#L5"

    def test_file_url_with_slash_branch(self):
        url = build_github_file_url("owner", "repo", "feature/v2", "src/main.py")
        assert url == "https://github.com/owner/repo/blob/feature/v2/src/main.py"
