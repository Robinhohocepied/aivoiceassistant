import os
from dataclasses import dataclass
from typing import Optional


def _try_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(override=False)
    except Exception:
        # dotenv is optional for local dev; ignore if missing
        pass


@dataclass(frozen=True)
class Settings:
    # Core
    app_env: str = "dev"
    clinic_tz: str = "Europe/Brussels"
    default_locale: str = "fr-FR"

    # OpenAI / Agents SDK
    openai_api_key: Optional[str] = None
    agent_model: str = "gpt-4.1"
    openai_base_url: Optional[str] = None
    openai_org_id: Optional[str] = None
    openai_project: Optional[str] = None
    agent_auto_reply: bool = False
    agent_dry_run: bool = True
    agent_generate_replies: bool = False
    agent_generate_followups: bool = False
    agent_generate_confirmations: bool = True
    agent_generate_alternatives: bool = True
    agent_generate_greeting: bool = False
    agent_generate_id_ack: bool = False
    flow_v2_enabled: bool = False
    calendar_send_updates: bool = False
    # Demo / web chat config
    demo_daily_limit: int = 20
    demo_timezone: str = "Europe/Amsterdam"
    demo_session_ttl_hours: int = 48
    max_messages_per_demo_session: int = 40

    # WhatsApp (Cloud API)
    whatsapp_token: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    whatsapp_base_url: str = "https://graph.facebook.com/v18.0"

    # Google Calendar
    google_creds_json: Optional[str] = None
    google_creds_json_b64: Optional[str] = None
    google_delegated_subject: Optional[str] = None
    google_calendar_id: Optional[str] = None
    calendar_id_whatsapp: Optional[str] = None
    calendar_id_web_demo: Optional[str] = None

    # Scheduling / Jobs
    reminder_hours_before: int = 24

    # Security & Privacy
    redact_logs: bool = True
    data_retention_days: int = 90

    # Webhook / Server
    port: int = 8080
    base_url: str = "http://localhost:8080"

    # Build metadata
    app_version: str = "0.1.0"
    git_sha: str = "unknown"


def load_settings() -> Settings:
    _try_load_dotenv()

    def getenv(name: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(name, default)

    def getenv_int(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def getenv_bool(name: str, default: bool) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.lower() in {"1", "true", "yes", "on"}

    return Settings(
        app_env=getenv("APP_ENV", "dev") or "dev",
        clinic_tz=getenv("CLINIC_TZ", "Europe/Brussels") or "Europe/Brussels",
        default_locale=getenv("DEFAULT_LOCALE", "fr-FR") or "fr-FR",
        openai_api_key=getenv("OPENAI_API_KEY"),
        agent_model=getenv("AGENT_MODEL", "gpt-4.1") or "gpt-4.1",
        openai_base_url=getenv("OPENAI_BASE_URL"),
        openai_org_id=getenv("OPENAI_ORG_ID"),
        openai_project=getenv("OPENAI_PROJECT"),
        agent_auto_reply=getenv_bool("AGENT_AUTO_REPLY", False),
        agent_dry_run=getenv_bool("AGENT_DRY_RUN", True),
        agent_generate_replies=getenv_bool("AGENT_GENERATE_REPLIES", False),
        agent_generate_followups=getenv_bool("AGENT_GENERATE_FOLLOWUPS", False),
        agent_generate_confirmations=getenv_bool("AGENT_GENERATE_CONFIRMATIONS", True),
        agent_generate_alternatives=getenv_bool("AGENT_GENERATE_ALTERNATIVES", True),
        agent_generate_greeting=getenv_bool("AGENT_GENERATE_GREETING", False),
        agent_generate_id_ack=getenv_bool("AGENT_GENERATE_ID_ACK", False),
        flow_v2_enabled=getenv_bool("FLOW_V2_ENABLED", False),
        calendar_send_updates=getenv_bool("CALENDAR_SEND_UPDATES", False),
        demo_daily_limit=int(os.getenv("DEMO_DAILY_LIMIT", "20")),
        demo_timezone=getenv("DEMO_TIMEZONE", "Europe/Amsterdam") or "Europe/Amsterdam",
        demo_session_ttl_hours=int(os.getenv("DEMO_SESSION_TTL_HOURS", "48")),
        max_messages_per_demo_session=int(os.getenv("MAX_MESSAGES_PER_DEMO_SESSION", "40")),
        whatsapp_token=getenv("WHATSAPP_TOKEN"),
        whatsapp_verify_token=getenv("WHATSAPP_VERIFY_TOKEN"),
        whatsapp_phone_id=getenv("WHATSAPP_PHONE_ID"),
        whatsapp_base_url=getenv("WHATSAPP_BASE_URL", "https://graph.facebook.com/v18.0")
        or "https://graph.facebook.com/v18.0",
        google_creds_json=getenv("GOOGLE_CREDS_JSON"),
        google_creds_json_b64=getenv("GOOGLE_CREDS_JSON_B64"),
        google_delegated_subject=getenv("GOOGLE_DELEGATED_SUBJECT"),
        google_calendar_id=getenv("GOOGLE_CALENDAR_ID"),
        calendar_id_whatsapp=getenv("CALENDAR_ID_WHATSAPP"),
        calendar_id_web_demo=getenv("CALENDAR_ID_WEB_DEMO"),
        reminder_hours_before=getenv_int("REMINDER_HOURS_BEFORE", 24),
        redact_logs=getenv_bool("REDACT_LOGS", True),
        data_retention_days=getenv_int("DATA_RETENTION_DAYS", 90),
        port=getenv_int("PORT", 8080),
        base_url=getenv("BASE_URL", "http://localhost:8080") or "http://localhost:8080",
        app_version=getenv("APP_VERSION", "0.1.0") or "0.1.0",
        git_sha=getenv("GIT_SHA", "unknown") or "unknown",
    )
