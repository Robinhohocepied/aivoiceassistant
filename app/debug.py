from dataclasses import asdict
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import Settings, load_settings
from connectors.whatsapp.store import store
from connectors.whatsapp.types import NormalizedMessage


def get_router(settings: Optional[Settings] = None) -> APIRouter:
    s = settings or load_settings()
    router = APIRouter(prefix="/debug", tags=["debug"])

    def _ensure_non_prod() -> None:
        env = (s.app_env or "").lower()
        if env in {"prod", "production"}:
            # Hide in production
            raise HTTPException(status_code=404, detail="Not Found")

    @router.get("/messages")
    async def list_messages(limit: int = Query(50, ge=1, le=500)) -> List[dict]:  # type: ignore
        _ensure_non_prod()
        msgs: List[NormalizedMessage] = store.all()
        recent = msgs[-limit:]
        return [asdict(m) for m in recent]

    @router.delete("/messages")
    async def clear_messages() -> dict:  # type: ignore
        _ensure_non_prod()
        store.clear()
        return {"status": "ok"}

    return router

