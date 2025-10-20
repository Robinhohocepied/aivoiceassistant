import json
import logging
import re
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        rid = _request_id_ctx.get()
        if rid:
            setattr(record, "request_id", rid)
        else:
            setattr(record, "request_id", None)
        return True


PII_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PII_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def mask_pii(value: Any) -> Any:
    try:
        s = str(value)
    except Exception:
        return value
    s = PII_EMAIL_RE.sub("<redacted:email>", s)
    s = PII_PHONE_RE.sub("<redacted:phone>", s)
    return s


class JsonFormatter(logging.Formatter):
    def __init__(self, redact: bool = True) -> None:
        super().__init__()
        self.redact = redact

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage() if not self.redact else mask_pii(record.getMessage()),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        # Include structured extras added via logger.*(..., extra={...})
        builtin = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "request_id",
        }
        for key, value in record.__dict__.items():
            if key in builtin or key.startswith("_"):
                continue
            payload[key] = mask_pii(value) if self.redact else value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(redact: bool = True) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(redact=redact))
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)

    # Silence noisy loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next):  # type: ignore
        existing = request.headers.get(self.header_name)
        rid = existing or str(uuid.uuid4())
        token = _request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers[self.header_name] = rid
            return response
        finally:
            _request_id_ctx.reset(token)
