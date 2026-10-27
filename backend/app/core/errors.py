"""Custom exception classes and error handling."""

from fastapi import HTTPException, status


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class RepositoryNotFoundError(AppError):
    """Raised when a GitHub repository cannot be found."""

    def __init__(self, owner: str, repo: str):
        super().__init__(
            f"Repository '{owner}/{repo}' not found or inaccessible.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class BranchNotFoundError(AppError):
    """Raised when a branch does not exist."""

    def __init__(self, branch: str, owner: str, repo: str):
        super().__init__(
            f"Branch '{branch}' not found in '{owner}/{repo}'.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidRepositoryURLError(AppError):
    """Raised when the GitHub URL is invalid."""

    def __init__(self, url: str):
        super().__init__(
            f"Invalid GitHub repository URL: '{url}'. Expected format: https://github.com/owner/repo",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class IndexNotReadyError(AppError):
    """Raised when the index is not yet built."""

    def __init__(self, repository_id: str):
        super().__init__(
            f"Repository index '{repository_id}' is not ready. Please wait for indexing to complete.",
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitError(AppError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self):
        super().__init__(
            "GitHub API rate limit exceeded. Please try again later or configure a GITHUB_TOKEN.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class GeminiAPIError(AppError):
    """Raised when the Gemini API returns an error."""

    def __init__(self, detail: str = ""):
        msg = "Gemini API error"
        if detail:
            msg += f": {detail}"
        super().__init__(msg, status_code=status.HTTP_502_BAD_GATEWAY)


def app_error_to_http(error: AppError) -> HTTPException:
    """Convert an AppError to a FastAPI HTTPException."""
    return HTTPException(status_code=error.status_code, detail=error.message)
