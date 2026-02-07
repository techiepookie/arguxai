"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.core.logging import logger
from app.api.routes import health, events, metrics, issues, github, slack, figma, jira, funnel, funnels, dashboard
import os

# Create FastAPI app
app = FastAPI(
    title="ArguxAI",
    description="AI-Powered Conversion Optimization & Funnel Analytics System",
    version="0.1.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info("Frontend mounted at /frontend")

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(issues.router, prefix="/api/issues", tags=["Issues"])
app.include_router(funnels.router, prefix="/api/funnels", tags=["Funnels"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub"])
app.include_router(slack.router, prefix="/api/slack", tags=["Slack"])
app.include_router(figma.router, prefix="/api/figma", tags=["Figma"])
app.include_router(jira.router, prefix="/api/jira", tags=["Jira"])
app.include_router(funnel.router, prefix="/api/funnel", tags=["Funnel Auto-Generation"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(
        "Starting ArguxAI",
        environment=settings.environment,
        demo_mode=settings.demo_mode
    )

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down ArguxAI")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ArguxAI",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.environment,
        "frontend_url": "/frontend/",
        "docs_url": "/docs" if settings.environment == "development" else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
