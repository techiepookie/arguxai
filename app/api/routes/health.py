"""Health check endpoints"""

from fastapi import APIRouter
from datetime import datetime
from app.config import settings
from app.integrations.convex_client import convex_client
from app.integrations.deepseek_client import deepseek_client
from app.integrations.github_client import github_client
from app.integrations.figma_client import figma_client
from app.integrations.jira_client import jira_client

router = APIRouter()


@router.get("")
async def health_check():
    """
    Health check endpoint
    
    Returns system status and service availability
    """
    # Check Convex connection
    convex_healthy = await convex_client.health_check()
    
    # Check DeepSeek connection
    deepseek_healthy = await deepseek_client.health_check()
    
    # Check GitHub connection
    github_healthy = await github_client.health_check()
    
    # Check Figma connection
    figma_healthy = await figma_client.health_check()
    
    # Check Jira connection
    jira_healthy = await jira_client.health_check()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "version": "0.1.0",
        "services": {
            "api": "operational",
            "convex": "connected" if convex_healthy else "disconnected",
            "deepseek": "connected" if deepseek_healthy else "disconnected",
            "slack": "configured" if settings.slack_webhook_url else "not_configured",
            "github": "connected" if github_healthy else "not_configured",
            "figma": "connected" if figma_healthy else "not_configured",
            "jira": "connected" if jira_healthy else "not_configured",
        },
        "demo_mode": settings.demo_mode
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint for monitoring"""
    return {"ping": "pong", "timestamp": datetime.utcnow().isoformat()}
