"""Funnels API endpoints"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.funnels import (
    Funnel, FunnelCreate, FunnelUpdate,
    AIPromptEnhanceRequest, AIPromptEnhanceResponse,
    AIFunnelGenerateRequest, AIFunnelGenerateResponse
)
from app.services.funnel_storage import funnel_storage
from app.services.ai_funnel_service import ai_funnel_service
from app.core.dependencies import APIKeyDep
from app.core.logging import logger

router = APIRouter()


@router.post("/", response_model=Funnel, status_code=status.HTTP_201_CREATED)
async def create_funnel(
    funnel_data: FunnelCreate,
    api_key: APIKeyDep = None
) -> Funnel:
    """
    Create a new funnel
    
    Can be created manually or from AI generation
    """
    try:
        funnel = funnel_storage.create_funnel(funnel_data)
        return funnel
    except Exception as e:
        logger.error("Failed to create funnel", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create funnel: {str(e)}"
        )


@router.get("/", response_model=List[Funnel])
async def list_funnels(
    api_key: APIKeyDep = None
) -> List[Funnel]:
    """List all funnels"""
    try:
        return funnel_storage.list_funnels()
    except Exception as e:
        logger.error("Failed to list funnels", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list funnels: {str(e)}"
        )


@router.get("/{funnel_id}", response_model=Funnel)
async def get_funnel(
    funnel_id: str,
    api_key: APIKeyDep = None
) -> Funnel:
    """Get funnel by ID"""
    funnel = funnel_storage.get_funnel(funnel_id)
    if not funnel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funnel {funnel_id} not found"
        )
    return funnel


@router.put("/{funnel_id}", response_model=Funnel)
async def update_funnel(
    funnel_id: str,
    updates: FunnelUpdate,
    api_key: APIKeyDep = None
) -> Funnel:
    """Update funnel"""
    funnel = funnel_storage.update_funnel(funnel_id, updates)
    if not funnel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funnel {funnel_id} not found"
        )
    return funnel


@router.delete("/{funnel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_funnel(
    funnel_id: str,
    api_key: APIKeyDep = None
):
    """Delete funnel"""
    deleted = funnel_storage.delete_funnel(funnel_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funnel {funnel_id} not found"
        )


@router.post("/enhance-prompt", response_model=AIPromptEnhanceResponse)
async def enhance_prompt(
    request: AIPromptEnhanceRequest,
    api_key: APIKeyDep = None
) -> AIPromptEnhanceResponse:
    """
    Enhance user's funnel prompt using AI
    
    Takes a basic prompt and makes it more detailed and actionable
    """
    try:
        result = await ai_funnel_service.enhance_prompt(request.prompt)
        return result
    except Exception as e:
        logger.error("Failed to enhance prompt", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance prompt: {str(e)}"
        )


@router.post("/generate-ai", response_model=AIFunnelGenerateResponse)
async def generate_ai_funnel(
    request: AIFunnelGenerateRequest,
    api_key: APIKeyDep = None
) -> AIFunnelGenerateResponse:
    """
    Generate complete funnel using AI
    
    Provide a prompt describing your desired funnel and AI will generate
    the complete structure including all steps
    """
    try:
        # Get real events from system context
        from app.integrations.sqlite_client import sqlite_client
        available_events = await sqlite_client.get_distinct_event_types()
        
        result = await ai_funnel_service.generate_funnel(request.prompt, available_events)
        return result
    except Exception as e:
        logger.error("Failed to generate AI funnel", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate funnel: {str(e)}"
        )
