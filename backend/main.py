"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import settings
from database import init_db
from routes.digest import router as digest_router
from routes.health import router as health_router
from routes.intel import router as intel_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.database_url:
        init_db(settings.database_url)
    yield


app = FastAPI(
    title="Watchtower",
    description="HappyCo Competitive Intelligence Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(intel_router)
app.include_router(digest_router)
