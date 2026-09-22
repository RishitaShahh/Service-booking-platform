"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.database import Base, engine
from app.routers import (
    auth_router,
    bookings_router,
    providers_router,
    services_router,
    slots_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to create database tables on startup.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    # Create all database tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
setup_cors(app)

# Include API routers under prefix
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(services_router, prefix=settings.API_V1_STR)
app.include_router(slots_router, prefix=settings.API_V1_STR)
app.include_router(bookings_router, prefix=settings.API_V1_STR)
app.include_router(providers_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health Check"])
async def root():
    """Root health check endpoint.

    Returns:
        dict: Basic API status payload.
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }
