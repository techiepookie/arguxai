"""Figma data models for design review"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class FigmaNodeType(str, Enum):
    """Figma node types"""
    FRAME = "FRAME"
    GROUP = "GROUP"
    COMPONENT = "COMPONENT"
    INSTANCE = "INSTANCE"
    TEXT = "TEXT"
    RECTANGLE = "RECTANGLE"
    VECTOR = "VECTOR"


class DesignIssueType(str, Enum):
    """Types of design issues affecting conversion"""
    POOR_CONTRAST = "poor_contrast"
    SMALL_TEXT = "small_text"
    UNCLEAR_CTA = "unclear_cta"
    CROWDED_LAYOUT = "crowded_layout"
    MISSING_FEEDBACK = "missing_feedback"
    INCONSISTENT_STYLING = "inconsistent_styling"
    POOR_HIERARCHY = "poor_hierarchy"


class FigmaFrame(BaseModel):
    """Figma frame/screen to analyze"""
    id: str = Field(..., description="Figma node ID")
    name: str = Field(..., description="Frame name")
    node_type: FigmaNodeType = Field(..., description="Node type")
    width: float
    height: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123:456",
                "name": "OTP Verification Screen",
                "node_type": "FRAME",
                "width": 375,
                "height": 812
            }
        }


class DesignIssue(BaseModel):
    """AI-detected design issue"""
    issue_type: DesignIssueType
    severity: str = Field(..., description="low, medium, high, critical")
    description: str = Field(..., description="What's wrong")
    recommendation: str = Field(..., description="How to fix it")
    confidence: float = Field(..., description="AI confidence 0-100")
    location: Optional[str] = Field(None, description="Where in the design")
    
    class Config:
        json_schema_extra = {
            "example": {
                "issue_type": "unclear_cta",
                "severity": "high",
                "description": "The 'Verify OTP' button has poor contrast (ratio 2.1:1)",
                "recommendation": "Increase contrast to at least 4.5:1. Use primary brand color with white text.",
                "confidence": 92.5,
                "location": "Bottom right, main CTA button"
            }
        }


class DesignAnalysis(BaseModel):
    """Complete design analysis from AI"""
    frame_id: str
    frame_name: str
    
    # Analysis results
    overall_score: float = Field(..., description="Overall design score 0-100")
    issues: List[DesignIssue] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    
    # Conversion impact
    conversion_impact_assessment: str = Field(..., description="How this affects conversion")
    priority_fixes: List[str] = Field(default_factory=list, description="Top 3 fixes")
    
    # AI metadata
    model_used: str
    analysis_time_ms: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "frame_id": "123:456",
                "frame_name": "OTP Verification",
                "overall_score": 68.5,
                "issues": [
                    {
                        "issue_type": "unclear_cta",
                        "severity": "high",
                        "description": "Button contrast too low"
                    }
                ],
                "strengths": ["Clear input fields", "Good error messaging"],
                "conversion_impact_assessment": "Low contrast CTA likely reducing click-through by 10-15%",
                "priority_fixes": [
                    "Increase button contrast",
                    "Add loading state",
                    "Clarify OTP format"
                ],
                "model_used": "deepseek-vl",
                "analysis_time_ms": 3200
            }
        }


class FigmaReviewRequest(BaseModel):
    """Request to review a Figma design"""
    file_key: str = Field(..., description="Figma file key from URL")
    frame_ids: Optional[List[str]] = Field(None, description="Specific frames to analyze (all if empty)")
    issue_id: Optional[str] = Field(None, description="Link to conversion issue")


class FigmaReviewResponse(BaseModel):
    """Response from Figma design review"""
    success: bool
    file_key: str
    frames_analyzed: int
    analyses: List[DesignAnalysis]
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "file_key": "abc123def456",
                "frames_analyzed": 3,
                "analyses": [],
                "message": "Design review completed"
            }
        }
