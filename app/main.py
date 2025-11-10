import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from app.config import load_settings
from app.logging import CorrelationIdMiddleware, setup_logging
from connectors.whatsapp import get_router as get_whatsapp_router
from connectors.calendar.provider import get_calendar_provider


def create_app() -> FastAPI:
    settings = load_settings()
    setup_logging(redact=settings.redact_logs)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):  # type: ignore
        logging.getLogger(__name__).info("service starting")
        try:
            yield
        finally:
            logging.getLogger(__name__).info("service stopping")

    app = FastAPI(title="Mediflow API", version=settings.app_version, lifespan=lifespan)

    # Middleware
    app.add_middleware(CorrelationIdMiddleware)

    # Routers
    app.include_router(get_whatsapp_router(settings))

    # Debug: show active calendar provider (dev only)
    if (settings.app_env or "dev").lower() != "prod":
        @app.get("/_debug/provider")
        async def provider_info():  # type: ignore
            s = load_settings()
            provider = get_calendar_provider(s)
            provider_name = provider.__class__.__name__ if provider else None
            return {
                "provider": provider_name,
                "google_configured": bool(s.google_creds_json and s.google_calendar_id),
                "calendar_id": s.google_calendar_id,
            }

    # Health endpoint
    @app.get("/healthz")
    async def healthz():  # type: ignore
        now = datetime.now(timezone.utc)
        s = load_settings()  # reload to reflect env changes if any
        agents_configured = bool(s.openai_api_key)
        return {
            "status": "ok",
            "service": "mediflow",
            "version": s.app_version,
            "commit": s.git_sha,
            "env": s.app_env,
            "time": now.isoformat(),
            "agents_configured": agents_configured,
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=load_settings().port, reload=True)
