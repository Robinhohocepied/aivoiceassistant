import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from app.config import load_settings
from app.logging import CorrelationIdMiddleware, setup_logging
from connectors.whatsapp import get_router as get_whatsapp_router
from connectors.calendar.provider import get_calendar_provider
from agents.session import store as session_store
from connectors.whatsapp.store import store as wa_store


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

        @app.post("/_debug/calendar/book_test")
        async def book_test(  # type: ignore
            waid: str | None = None,
            iso: str | None = None,
            duration_min: int = 30,
        ):
            """Create a single test event with title 'Mediflow - {name} 🦷'.

            - Picks the last inbound WAID if not provided.
            - Uses session.preferred_time_iso unless 'iso' is provided.
            - Returns event details.
            """
            s = load_settings()
            provider = get_calendar_provider(s)
            if provider is None:
                return {"error": "no_calendar_provider"}

            # Determine WAID
            from_waid = waid
            if not from_waid:
                msgs = wa_store.all()
                if not msgs:
                    return {"error": "no_messages_in_store_and_no_waid_provided"}
                from_waid = msgs[-1].from_waid

            st = session_store.get(from_waid)
            target_iso = iso or st.preferred_time_iso
            if not target_iso:
                return {"error": "no_iso_available", "hint": "pass iso=YYYY-MM-DDTHH:MM:SS+TZ or send a message with preferred time first"}

            from datetime import datetime

            start_dt = datetime.fromisoformat(target_iso)
            title = f"Mediflow - {st.name or ''} 🦷".strip()
            desc = f"Motif: {st.reason or ''}".strip()
            available = provider.is_available(start_dt, duration_min=duration_min)
            evt = provider.create_event(
                start_dt,
                duration_min=duration_min,
                title=title,
                description=desc,
                patient_phone=from_waid,
                patient_name=st.name,
            )
            st.event_id = evt.id
            session_store.put(st)
            return {
                "created": True,
                "available": available,
                "event": {
                    "id": evt.id,
                    "start": evt.start.isoformat(),
                    "end": evt.end.isoformat(),
                    "title": evt.title,
                    "description": evt.description,
                },
                "session": {
                    "from_waid": st.from_waid,
                    "name": st.name,
                    "reason": st.reason,
                    "preferred_time_iso": st.preferred_time_iso,
                },
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
