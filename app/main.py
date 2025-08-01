# --- START OF FIX ---
from dotenv import load_dotenv
load_dotenv() # This line loads the variables from your .env file
# --- END OF FIX ---

# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from starlette_prometheus import PrometheusMiddleware, metrics
import structlog
from firebase_admin import auth as firebase_auth
from app.observability.logging_config import user_id_var
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.logging_config import setup_logging # Functions we made
from app.observability.tracing import setup_tracing # Functions we made

from api.routes import health, resume, match, profile, job_description, candidate, github, mcq, chatbot


app = FastAPI(
    title="VSmart API",
    description="API for resume parsing, job matching, and profile aggregation",
    version="0.1.0"
)


class UserIdContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/metrics":
            # Proceed without setting user_id or span attributes.
            return await call_next(request)
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            bearer_token = auth_header.split(" ", 1)[1]
            try:
                decoded_token = firebase_auth.verify_id_token(bearer_token)
                user_id = decoded_token.get("uid")
            except Exception as e:
                logger.warning("Firebase token verification failed", error=str(e))
        user_id_var.set(user_id)
        # Set user.id on OpenTelemetry span for Jaeger searchability
        span = trace.get_current_span()
        if user_id and span and span.is_recording():
            span.set_attribute("user.id", user_id)
            logger.debug("User ID set in context", user_id=user_id)
        response = await call_next(request)
        return response

# Add the middleware in your main.py before routers
app.add_middleware(UserIdContextMiddleware)


FastAPIInstrumentor.instrument_app(app, excluded_urls="/metrics",)
RequestsInstrumentor().instrument()


setup_logging()
setup_tracing()

logger = structlog.get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)


# Routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(job_description.router, prefix="/api", tags=["job_description"])
app.include_router(match.router, prefix="/api", tags=["match"])
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(candidate.router, prefix="/api", tags=["candidate"])
app.include_router(github.router, prefix="/api", tags=["github"])
app.include_router(mcq.router, prefix="/api", tags=["mcq"])
app.include_router(chatbot.router, prefix="/api", tags=["chatbot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
