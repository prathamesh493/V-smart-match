# app/observability/tracing.py

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

def setup_tracing():
    """Configures OpenTelemetry for tracing to be sent to a Collector/Agent."""
    resource = Resource.create({SERVICE_NAME: "vsmart-backend"})
    provider = TracerProvider(resource=resource)

    # ❗ THE FIX IS HERE ❗
    # We read the endpoint from an environment variable.
    # The default value is for local non-docker testing.
    # Docker Compose will provide the correct value.
    otel_exporter_otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")

    print(f"✅ Configuring OTLP gRPC exporter to send traces to: {otel_exporter_otlp_endpoint}")

    # The gRPC exporter endpoint should just be "host:port".
    # The 'insecure=True' is needed when the target doesn't use TLS, which is our case.
    exporter = OTLPSpanExporter(
        endpoint=otel_exporter_otlp_endpoint,
        insecure=True
    )
    
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)