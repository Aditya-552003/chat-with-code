"""Repository loading and management endpoints."""

from __future__ import annotations

import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.api.schemas import (
    IndexingJob,
    IndexingStatus,
    RepositoryInfo,
    RepositoryLoadRequest,
)
from app.core.errors import AppError, app_error_to_http
from app.core.logging import logger
from app.services import github_service
from app.services.chunking_service import chunk_documents
from app.services.indexing_service import (
    build_index,
    get_index,
    get_index_metadata,
    store_index_metadata,
)
from app.services.repository_service import load_repository_documents
from app.config import get_settings

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

# Background job tracking
_jobs: dict[str, IndexingJob] = {}
_executor = ThreadPoolExecutor(max_workers=2)


def _run_indexing(job_id: str, owner: str, repo: str, branch: str, repository_id: str) -> None:
    """Run the full indexing pipeline in a background thread."""
    try:
        # Phase 1: Loading
        _jobs[job_id].status = IndexingStatus.LOADING
        _jobs[job_id].progress_message = f"Loading files from {owner}/{repo}..."

        documents = load_repository_documents(owner, repo, branch)
        _jobs[job_id].total_files = len(documents)
        _jobs[job_id].progress_message = f"Loaded {len(documents)} files"

        if not documents:
            _jobs[job_id].status = IndexingStatus.FAILED
            _jobs[job_id].error_message = "No indexable files found in repository."
            return

        # Phase 2: Chunking
        _jobs[job_id].status = IndexingStatus.CHUNKING
        _jobs[job_id].progress_message = "Chunking source files..."

        chunks = chunk_documents(documents, owner, repo, branch, repository_id)
        _jobs[job_id].indexed_chunks = len(chunks)
        _jobs[job_id].progress_message = f"Created {len(chunks)} chunks"

        # Phase 3: Embedding + Indexing
        _jobs[job_id].status = IndexingStatus.EMBEDDING
        _jobs[job_id].progress_message = "Generating embeddings and building index..."

        build_index(repository_id, chunks)

        # Store metadata
        store_index_metadata(repository_id, {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "total_files": len(documents),
            "indexed_chunks": len(chunks),
            "github_url": f"https://github.com/{owner}/{repo}",
        })

        # Done
        _jobs[job_id].status = IndexingStatus.COMPLETED
        _jobs[job_id].progress_message = (
            f"Indexing complete: {len(documents)} files, {len(chunks)} chunks"
        )
        logger.info(f"Indexing completed for {repository_id}: {len(documents)} files, {len(chunks)} chunks")

    except Exception as e:
        logger.error(f"Indexing failed for {repository_id}: {e}")
        _jobs[job_id].status = IndexingStatus.FAILED
        _jobs[job_id].error_message = str(e)[:500]


@router.post("/load", response_model=IndexingJob)
async def load_repository(request: RepositoryLoadRequest) -> IndexingJob:
    """
    Load and index a GitHub repository.

    Validates the URL and branch, then starts background indexing.
    Returns a job ID for polling status.
    """
    try:
        owner, repo, parsed_branch = github_service.parse_github_url(request.repository_url)
    except AppError as e:
        raise app_error_to_http(e)

    branch = request.branch or parsed_branch

    # Verify repository exists
    try:
        repo_info = await github_service.verify_repository(owner, repo)
    except AppError as e:
        raise app_error_to_http(e)

    # Use default branch if none specified
    if branch is None:
        branch = repo_info.get("default_branch", "main")

    # Verify branch exists
    try:
        await github_service.verify_branch(owner, repo, branch)
    except AppError as e:
        raise app_error_to_http(e)

    # Generate IDs
    repository_id = f"{owner}-{repo}-{branch}".replace("/", "-")
    job_id = str(uuid.uuid4())

    # Check if already indexed
    existing = get_index(repository_id)
    if existing is not None:
        meta = get_index_metadata(repository_id) or {}
        return IndexingJob(
            job_id=job_id,
            repository_id=repository_id,
            status=IndexingStatus.COMPLETED,
            progress_message="Repository already indexed.",
            total_files=meta.get("total_files", 0),
            indexed_chunks=meta.get("indexed_chunks", 0),
        )

    # Create job and start background indexing
    job = IndexingJob(
        job_id=job_id,
        repository_id=repository_id,
        status=IndexingStatus.QUEUED,
        progress_message="Indexing job queued...",
    )
    _jobs[job_id] = job

    # Run in thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    loop.run_in_executor(_executor, _run_indexing, job_id, owner, repo, branch, repository_id)

    return job


@router.get("/jobs/{job_id}", response_model=IndexingJob)
async def get_job_status(job_id: str) -> IndexingJob:
    """Get the status of an indexing job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{repository_id}", response_model=RepositoryInfo)
async def get_repository(repository_id: str) -> RepositoryInfo:
    """Get repository info and indexing status."""
    meta = get_index_metadata(repository_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Repository not found")

    index = get_index(repository_id)
    status = IndexingStatus.COMPLETED if index else IndexingStatus.FAILED

    return RepositoryInfo(
        repository_id=repository_id,
        owner=meta.get("owner", ""),
        repo=meta.get("repo", ""),
        branch=meta.get("branch", "main"),
        github_url=meta.get("github_url", ""),
        status=status,
        total_files=meta.get("total_files", 0),
        indexed_chunks=meta.get("indexed_chunks", 0),
    )
