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

from app.observability.logging_config import setup_logging
from app.observability.tracing import setup_tracing

from api.routes import health, resume, match, profile, job_description, candidate, github, mcq, chatbot

setup_logging()
setup_tracing()

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="VSmart API",
    description="API for resume parsing, job matching, and profile aggregation",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

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
