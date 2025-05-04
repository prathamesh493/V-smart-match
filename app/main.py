import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, resume, match, profile, job_description, candidate, github

app = FastAPI(
    title="VSmart API",
    description="API for resume parsing, job matching, and profile aggregation",
    version="0.1.0"
)

# Add CORS middleware with configuration for WSL environment
app.add_middleware(
    CORSMiddleware,
    # Allow requests from frontend running in WSL or Windows
    allow_origins=[
        "http://mj.local:3000",  # Local development 
        "http://127.0.0.1:3000",  # Alternative local
        "http://mj.local:3000",  # WSL IP
        "http://192.168.0.104:3000",  # Network IP (if needed)
        "*",  # For development, remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(job_description.router, prefix="/api", tags=["job_description"])
app.include_router(match.router, prefix="/api", tags=["match"])
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(candidate.router, prefix="/api", tags=["candidate"])
app.include_router(github.router, prefix="/api", tags=["github"])

if __name__ == "__main__":
    import uvicorn
    # Important: Use 0.0.0.0 to bind to all interfaces, making the API accessible from Windows
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)