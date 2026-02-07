"""Dependency injection utilities for FastAPI"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Bearer token"""
    if settings.environment == "development" or settings.demo_mode:
        # In development/demo mode, be lenient with API key
        return credentials.credentials
    
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

# Reusable dependency for API key verification
APIKeyDep = Annotated[str, Depends(verify_api_key)]
