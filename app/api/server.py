"""FastAPI application server for OraCLI 10G Web."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_health import router as health_router
from app.api.routes_sql import router as sql_router
from app.config.settings import settings


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Oracle 10g SQL*Plus Compatible Educational Web Platform",
    )

    # Enable CORS for local dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(health_router)
    app.include_router(sql_router)

    # Mount static frontend build if it exists
    dist_dir = Path("web/dist")
    if dist_dir.exists() and dist_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")

    return app


app = create_app()


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Launch the uvicorn web server."""
    import uvicorn

    uvicorn.run("app.api.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    start_server()
