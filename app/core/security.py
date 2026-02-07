"""API security and authentication"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.core.logging import logger

security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Verify API key from Authorization header
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    api_key = credentials.credentials
    
    if api_key != settings.api_key:
        logger.warning("Invalid API key attempt", provided_key=api_key[:8] + "...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key
