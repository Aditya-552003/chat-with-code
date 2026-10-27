"""Repository loading service with GitHub Archive stream and LlamaIndex reader fallback."""

from __future__ import annotations

import io
import os
import zipfile
from typing import Any

import httpx
from llama_index.core import Document
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
    parts = file_path.replace("\\", "/").split("/")
    for part in parts:
        if part in EXCLUDED_DIRS:
            return False

    filename = parts[-1] if parts else ""
    if filename in EXCLUDED_FILES:
        return False

    if filename.startswith(".") and filename not in {".env.example", ".gitignore", ".dockerignore"}:
        if not any(filename.startswith(p) for p in [".eslint", ".prettier", ".babel", ".stylelint"]):
            return False

    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()

    if not ext and filename in {"Makefile", "Dockerfile", "Procfile", "Rakefile", "Gemfile", "Pipfile"}:
        return True

    return ext in INCLUDED_EXTENSIONS


def load_repository_from_archive(
    owner: str,
    repo: str,
    branch: str = "main",
) -> list[Document]:
    """
    Download and extract repository files using GitHub zip archive.
    
    This avoids dozens of round-trip GitHub API calls, completely bypasses
    unauthenticated API rate limits (60 req/hr), and prevents illegal header errors.
    """
    settings = get_settings()
    urls = [
        f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip",
        f"https://github.com/{owner}/{repo}/archive/{branch}.zip",
    ]
    
    headers = {
        "User-Agent": "ChatWithCode/2.0",
        "Accept": "application/vnd.github.v3+json",
    }
    
    token = (settings.github_token or os.getenv("GITHUB_TOKEN", "")).strip()
    if token:
        headers["Authorization"] = f"token {token}"

    content = None
    last_error = None

    for url in urls:
        try:
            logger.info(f"Attempting repository archive download from {url}")
            with httpx.Client(timeout=45.0, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200 and resp.content:
                    content = resp.content
                    logger.info(f"Downloaded archive for {owner}/{repo} ({len(content)} bytes)")
                    break
                else:
                    logger.warning(f"Archive fetch {url} returned status {resp.status_code}")
        except Exception as exc:
            last_error = exc
            logger.warning(f"Failed archive fetch from {url}: {exc}")

    if not content:
        raise RuntimeError(f"Could not download repository archive for {owner}/{repo}@{branch}: {last_error}")

    try:
        zf = zipfile.ZipFile(io.BytesIO(content))
    except Exception as exc:
        raise RuntimeError(f"Failed to parse downloaded archive as zip: {exc}")

    documents: list[Document] = []
    
    for zip_entry in zf.namelist():
        # Zip files contain top-level directory e.g. 'repo-name-main/src/index.ts'
        parts = zip_entry.split("/", 1)
        if len(parts) < 2 or not parts[1]:
            continue

        rel_path = parts[1]
        if not _should_include_file(rel_path):
            continue

        try:
            file_bytes = zf.read(zip_entry)
            if len(file_bytes) > settings.max_file_size_bytes:
                logger.debug(f"Skipping oversized file: {rel_path} ({len(file_bytes)} bytes)")
                continue

            text = file_bytes.decode("utf-8", errors="replace")
            doc = Document(
                text=text,
                metadata={
                    "file_path": rel_path,
                    "file_name": rel_path.split("/")[-1],
                },
            )
            documents.append(doc)

            if len(documents) >= settings.max_files_per_repo:
                logger.warning(f"Reached max file limit ({settings.max_files_per_repo})")
                break
        except Exception as e:
            logger.debug(f"Could not read {zip_entry} from zip: {e}")

    logger.info(f"Extracted {len(documents)} source files from archive for {owner}/{repo}")
    return documents


def load_repository_documents(
    owner: str,
    repo: str,
    branch: str = "main",
) -> list[Any]:
    """
    Load documents from a GitHub repository.
    
    First tries the fast archive stream (0 rate-limit consumption).
    Falls back to LlamaIndex GithubRepositoryReader if archive stream fails.
    """
    settings = get_settings()
    github_token = (settings.github_token or os.getenv("GITHUB_TOKEN", "")).strip()

    # 1. Primary path: Fast archive stream
    try:
        docs = load_repository_from_archive(owner, repo, branch)
        if docs:
            return docs
    except Exception as exc:
        logger.warning(f"Archive loader failed for {owner}/{repo} ({exc}). Trying GithubRepositoryReader...")

    # 2. Fallback path: LlamaIndex GithubRepositoryReader with safe token header
    if github_token:
        github_client = GithubClient(github_token=github_token, verbose=False)
    else:
        # Avoid illegal header 'Bearer ' when token is empty
        github_client = GithubClient(github_token="dummy_token", verbose=False)
        github_client._headers.pop("Authorization", None)

    loader = GithubRepositoryReader(
        github_client,
        owner=owner,
        repo=repo,
        filter_file_extensions=(list(INCLUDED_EXTENSIONS), GithubRepositoryReader.FilterType.INCLUDE),
        verbose=False,
        concurrent_requests=settings.concurrent_github_requests,
    )

    logger.info(f"Loading repository {owner}/{repo} branch={branch} via API reader")
    documents = loader.load_data(branch=branch)
    logger.info(f"Loaded {len(documents)} raw documents from {owner}/{repo}")

    filtered = []
    for doc in documents:
        file_path = doc.metadata.get("file_path", "")
        if not _should_include_file(file_path):
            continue
        if len(doc.text) > settings.max_file_size_bytes:
            continue
        filtered.append(doc)

        if len(filtered) >= settings.max_files_per_repo:
            break

    logger.info(f"After filtering: {len(filtered)} documents from {owner}/{repo}")
    return filtered
