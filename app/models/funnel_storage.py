"""Funnel storage and management models"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class FunnelSource(str, Enum):
    """How the funnel was created"""
    AI_GENERATED = "ai_generated"
    MANUAL = "manual"
    AI_EDITED = "ai_edited"  # AI-generated but user edited


class StoredFunnelStep(BaseModel):
    """Funnel step for storage"""
    step_number: int
    step_name: str
    event_name: str
    description: Optional[str] = None
    expected_conversion_rate: Optional[float] = None


class StoredFunnel(BaseModel):
    """Stored funnel with metadata"""
    id: str = Field(..., description="Unique funnel ID")
    name: str
    description: Optional[str] = None
    steps: List[StoredFunnelStep]
    source: FunnelSource
    figma_file_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Is this funnel actively monitored?")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "funnel_signup_flow_001",
                "name": "User Signup Flow",
                "description": "From landing to verified account",
                "steps": [
                    {
                        "step_number": 1,
                        "step_name": "landing_page_view",
                        "event_name": "page_viewed_landing"
                    }
                ],
                "source": "ai_generated",
                "is_active": True
            }
        }


class FunnelUpdateRequest(BaseModel):
    """Request to update funnel"""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[StoredFunnelStep]] = None
    is_active: Optional[bool] = None


class FunnelCreateRequest(BaseModel):
    """Manually create funnel"""
    name: str = Field(..., description="Funnel name")
    description: Optional[str] = None
    steps: List[StoredFunnelStep] = Field(..., description="Funnel steps (min 2)")
    figma_file_key: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Checkout Flow",
                "description": "Cart to payment complete",
                "steps": [
                    {
                        "step_number": 1,
                        "step_name": "cart_view",
                        "event_name": "cart_page_viewed",
                        "description": "User views shopping cart"
                    },
                    {
                        "step_number": 2,
                        "step_name": "checkout_started",
                        "event_name": "checkout_button_clicked",
                        "description": "User starts checkout"
                    },
                    {
                        "step_number": 3,
                        "step_name": "payment_complete",
                        "event_name": "payment_success",
                        "description": "Payment processed successfully"
                    }
                ]
            }
        }


class FunnelListResponse(BaseModel):
    """List of funnels"""
    success: bool
    funnels: List[StoredFunnel]
    total: int
    active: int
