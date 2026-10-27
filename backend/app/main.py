"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, conversations, health, repositories
from app.config import get_settings
from app.core.errors import AppError
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown hooks."""
    settings = get_settings()
    logger.info(f"Starting Chat with Code v{settings.app_version}")
    logger.info(f"Gemini model: {settings.gemini_model}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    logger.info(f"CORS origin: {settings.frontend_origin}")

    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not configured — chat will fail")
    if not settings.github_token:
        logger.warning("GITHUB_TOKEN not configured — rate limits may apply")

    yield

    logger.info("Shutting down Chat with Code")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Chat with Code API",
        description="Ask questions about any GitHub repository using AI-powered code analysis.",
        version=settings.app_version,
        lifespan=lifespan,
    )

    # CORS
    origins = [settings.frontend_origin]
    # Also allow common local dev origins
    if "localhost" in settings.frontend_origin:
        origins.extend([
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Global exception handler for AppError
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    # Generic exception handler (don't leak stack traces)
    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {type(exc).__name__}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred."},
        )

    # Register routes
    app.include_router(health.router)
    app.include_router(repositories.router)
    app.include_router(chat.router)
    app.include_router(conversations.router)

    return app


app = create_app()
