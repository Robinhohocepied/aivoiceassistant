import logging
from datetime import datetime, timezone

from fastapi import FastAPI

from app.config import load_settings
from app.logging import CorrelationIdMiddleware, setup_logging
from connectors.whatsapp import get_router as get_whatsapp_router
from app.debug import get_router as get_debug_router


def create_app() -> FastAPI:
    settings = load_settings()
    setup_logging(redact=settings.redact_logs)

    app = FastAPI(title="Mediflow API", version=settings.app_version)

    # Middleware
    app.add_middleware(CorrelationIdMiddleware)

    # Routers
    app.include_router(get_whatsapp_router(settings))
    # Debug endpoints (hidden in prod by the router itself)
    app.include_router(get_debug_router(settings))

    # Startup/Shutdown hooks
    @app.on_event("startup")
    async def _on_startup() -> None:
        logging.getLogger(__name__).info(
            "service starting",
        )

    @app.on_event("shutdown")
    async def _on_shutdown() -> None:
        logging.getLogger(__name__).info(
            "service stopping",
        )

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
