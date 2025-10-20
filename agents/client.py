
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - handled at runtime if SDK not installed
    OpenAI = None  # type: ignore

from typing import Optional

from app.config import Settings


def _normalize_base_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return url
    u = url.strip()
    if not u:
        return None
    if not (u.startswith("http://") or u.startswith("https://")):
        u = "https://" + u
    return u


def create_agents_client(settings: Settings):
    """Create and return an OpenAI Agents SDK client.

    This does not perform any network calls. Returns None if API key or SDK missing.
    """
    if settings.openai_api_key is None or OpenAI is None:
        return None

    # Organization/base_url/project are optional and only set if provided.
    kwargs = {}
    base_url = _normalize_base_url(settings.openai_base_url)
    if base_url:
        kwargs["base_url"] = base_url
    if settings.openai_org_id:
        kwargs["organization"] = settings.openai_org_id

    client = OpenAI(api_key=settings.openai_api_key, **kwargs)

    # Optionally, project configuration can be stored/used at higher layers
    # (e.g., selecting an agent or project ID during Phase 3).
    return client
