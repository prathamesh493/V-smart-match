# app/observability/logging_config.py

import sys
import logging
import structlog
import contextvars
from opentelemetry import trace

# Context variable that holds user_id for each request
user_id_var = contextvars.ContextVar("user_id", default=None)

def add_user_id(logger, method_name, event_dict):
    """
    Include user_id (if any) in the log event.
    The user_id_var is set in middleware per request.
    """
    user_id = user_id_var.get()
    if user_id is not None:
        event_dict["user_id"] = user_id
    return event_dict

def add_opentelemetry_ids(logger, method_name, event_dict):
    """
    Add trace_id and span_id from the current OpenTelemetry span.
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        span_context = current_span.get_span_context()
        if span_context and span_context.trace_id:
            # 32-char hex for trace, 16-char for span
            event_dict["trace_id"] = format(span_context.trace_id, "032x")
            event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict

def setup_logging():
    """
    Configures structlog for JSON logs with user/context/tracing info.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )
    structlog.configure(
        processors=[
            add_user_id,                         # <-- Always include user_id
            structlog.stdlib.add_log_level,       # level field (info/warning)
            add_opentelemetry_ids,                # trace_id and span_id fields
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    print("✅ Structlog JSON logging configured successfully.")
