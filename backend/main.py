"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings, validate_required_env
from database import init_db
from routes.digest import router as digest_router
from scheduler import shutdown_scheduler, start_scheduler
from routes.health import router as health_router
from routes.intel import router as intel_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_required_env()
    if settings.database_url:
        init_db(settings.database_url)
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Watchtower",
    description="HappyCo Competitive Intelligence Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(intel_router)
app.include_router(digest_router)
