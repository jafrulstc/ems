import contextvars
from typing import Any

tenant_context: contextvars.ContextVar[Any] = contextvars.ContextVar("tenant_context", default=None)
user_context: contextvars.ContextVar[Any] = contextvars.ContextVar("user_context", default=None)
