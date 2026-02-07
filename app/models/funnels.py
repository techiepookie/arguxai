"""
Funnel models for ArguxAI
Stores user-defined conversion funnels for tracking
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class FunnelStep(BaseModel):
    """Individual step in a conversion funnel"""
    id: Optional[str] = None
    name: str = Field(..., description="Step name (e.g., 'Login Page View')")
    event_type: str = Field(..., description="Event type that triggers this step")
    order: int = Field(..., description="Step order in funnel (1-based)")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Additional properties for matching")


class FunnelCreate(BaseModel):
    """Request to create a new funnel"""
    name: str = Field(..., description="Funnel name")
    description: Optional[str] = Field(None, description="Funnel description")
    steps: List[FunnelStep] = Field(..., description="Funnel steps in order")
    created_by_ai: bool = Field(default=False, description="Whether created by AI")
    ai_prompt: Optional[str] = Field(None, description="Original AI prompt if AI-generated")


class Funnel(BaseModel):
    """Complete funnel model"""
    id: str
    name: str
    description: Optional[str] = None
    steps: List[FunnelStep]
    created_by_ai: bool = False
    ai_prompt: Optional[str] = None
    created_at: int  # Unix timestamp ms
    updated_at: int  # Unix timestamp ms


class FunnelUpdate(BaseModel):
    """Request to update an existing funnel"""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[FunnelStep]] = None


class AIPromptEnhanceRequest(BaseModel):
    """Request to enhance a funnel generation prompt"""
    prompt: str = Field(..., description="User's original prompt")


class AIPromptEnhanceResponse(BaseModel):
    """Enhanced prompt response"""
    original_prompt: str
    enhanced_prompt: str
    improvements: List[str] = Field(description="What was improved")


class AIFunnelGenerateRequest(BaseModel):
    """Request to generate funnel using AI"""
    prompt: str = Field(..., description="Prompt describing desired funnel")


class AIFunnelGenerateResponse(BaseModel):
    """AI-generated funnel"""
    funnel: FunnelCreate
    reasoning: str = Field(description="AI's reasoning for funnel structure")
