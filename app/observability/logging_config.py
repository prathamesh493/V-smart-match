# app/observability/logging_config.py
import sys
import logging
import structlog
from opentelemetry import trace

# This custom processor is the magic that links your logs and traces.
def add_opentelemetry_ids(logger, method_name, event_dict):
    """A structlog processor that adds span_id and trace_id to the log record."""
    current_span = trace.get_current_span()
    if current_span.is_recording():
        span_context = current_span.get_span_context()
        event_dict['trace_id'] = format(span_context.trace_id, '032x')
        event_dict['span_id'] = format(span_context.span_id, '016x')
    return event_dict

def setup_logging():
    """Configures Structlog for JSON logging with OpenTelemetry context."""
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            add_opentelemetry_ids,  # Add trace context to all logs!
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    print("✅ Structlog JSON logging configured successfully.")