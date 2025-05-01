from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, resume, match, profile, job_description

app = FastAPI(
    title="VSmart API",
    description="API for resume parsing, job matching, and profile aggregation",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(job_description.router, prefix="/api", tags=["job_description"])
#app.include_router(match.router, prefix="/api", tags=["match"])
#app.include_router(profile.router, prefix="/api", tags=["profile"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)