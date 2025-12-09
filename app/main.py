import logging

from fastapi import FastAPI

from app.api.routes.mvola import router as mvola_router
from app.core.config import settings
from app.core.database import init_db


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        logging.info("Database initialized")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": settings.app_name}

    app.include_router(mvola_router)
    return app


app = create_app()
