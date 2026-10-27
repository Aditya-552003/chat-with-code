"""Repository loading service using LlamaIndex GithubRepositoryReader."""

from __future__ import annotations

import os
from typing import Any

from llama_index.readers.github import GithubClient, GithubRepositoryReader

from app.config import get_settings
from app.core.logging import logger

# File extensions to include for indexing
INCLUDED_EXTENSIONS = {
    # Python
    ".py", ".pyi",
    # JavaScript / TypeScript
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    # Web
    ".html", ".css", ".scss", ".vue", ".svelte",
    # Java / Kotlin
    ".java", ".kt", ".kts",
    # C / C++
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh",
    # Go
    ".go",
    # Rust
    ".rs",
    # Ruby
    ".rb",
    # PHP
    ".php",
    # Swift
    ".swift",
    # Shell
    ".sh", ".bash", ".zsh",
    # SQL
    ".sql",
    # Config / Data
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    # Documentation
    ".md", ".rst", ".txt",
    # Docker
    ".dockerfile",
    # Project files
    ".xml", ".gradle",
}

# Directories to exclude
EXCLUDED_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".env", "dist", "build", ".next", ".nuxt", "target", "out",
    ".idea", ".vscode", ".cache", ".pytest_cache", ".mypy_cache",
    ".tox", "vendor", "bower_components", "coverage", ".coverage",
    "htmlcov", "eggs", ".eggs", "*.egg-info",
}

# Files to exclude by name
EXCLUDED_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Pipfile.lock", "poetry.lock", "composer.lock",
    "Gemfile.lock", "Cargo.lock", ".DS_Store", "thumbs.db",
}


def _should_include_file(file_path: str) -> bool:
    """Determine if a file should be included based on extension and path rules."""
    # Check excluded directories
    parts = file_path.split("/")
    for part in parts:
        if part in EXCLUDED_DIRS:
            return False

    # Check excluded files
    filename = parts[-1] if parts else ""
    if filename in EXCLUDED_FILES:
        return False

    # Check if it's a dotfile in root (except common ones)
    if filename.startswith(".") and filename not in {".env.example", ".gitignore", ".dockerignore"}:
        # Allow config dotfiles like .eslintrc, .prettierrc
        if not any(filename.startswith(p) for p in [".eslint", ".prettier", ".babel", ".stylelint"]):
            return False

    # Check extension
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()

    # Allow common project root files without extension
    if not ext and filename in {"Makefile", "Dockerfile", "Procfile", "Rakefile", "Gemfile", "Pipfile"}:
        return True

    return ext in INCLUDED_EXTENSIONS


def load_repository_documents(
    owner: str,
    repo: str,
    branch: str = "main",
) -> list[Any]:
    """
    Load documents from a GitHub repository using LlamaIndex's GithubRepositoryReader.

    This preserves the core functionality from the original main.py but adds
    file filtering and size limits.
    """
    settings = get_settings()
    github_token = settings.github_token or os.getenv("GITHUB_TOKEN", "")

    if not github_token:
        logger.warning("No GITHUB_TOKEN configured. Rate limits may apply for public repos.")

    github_client = GithubClient(github_token=github_token, verbose=False)

    loader = GithubRepositoryReader(
        github_client,
        owner=owner,
        repo=repo,
        filter_file_extensions=(list(INCLUDED_EXTENSIONS), GithubRepositoryReader.FilterType.INCLUDE),
        verbose=False,
        concurrent_requests=settings.concurrent_github_requests,
    )

    logger.info(f"Loading repository {owner}/{repo} branch={branch}")
    documents = loader.load_data(branch=branch)
    logger.info(f"Loaded {len(documents)} raw documents from {owner}/{repo}")

    # Post-filter by path rules and size
    filtered = []
    for doc in documents:
        file_path = doc.metadata.get("file_path", "")
        if not _should_include_file(file_path):
            continue
        if len(doc.text) > settings.max_file_size_bytes:
            logger.debug(f"Skipping oversized file: {file_path} ({len(doc.text)} bytes)")
            continue
        filtered.append(doc)

        if len(filtered) >= settings.max_files_per_repo:
            logger.warning(f"Reached max file limit ({settings.max_files_per_repo})")
            break

    logger.info(f"After filtering: {len(filtered)} documents from {owner}/{repo}")
    return filtered
