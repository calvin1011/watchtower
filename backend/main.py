"""FastAPI application entry point."""

from fastapi import FastAPI

from routes.health import router as health_router

app = FastAPI(
    title="Watchtower",
    description="HappyCo Competitive Intelligence Agent API",
    version="0.1.0",
)

app.include_router(health_router)
