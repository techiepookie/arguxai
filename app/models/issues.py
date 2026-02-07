"""Issue and anomaly data models"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IssueStatus(str, Enum):
    """Issue lifecycle status"""
    DETECTED = "detected"
    DIAGNOSED = "diagnosed"
    FIXED = "fixed"
    MEASURING = "measuring"
    VERIFIED = "verified"
    CLOSED = "closed"


class IssueSeverity(str, Enum):
    """Issue severity levels"""
    CRITICAL = "critical"  # > 20% drop
    HIGH = "high"  # 15-20% drop
    MEDIUM = "medium"  # 12-15% drop
    LOW = "low"  # < 12% drop


class Anomaly(BaseModel):
    """
    Detected anomaly in conversion metrics
    """
    funnel_step: str
    detected_at: int  # Unix timestamp in ms
    
    # Metrics
    current_conversion_rate: float
    baseline_conversion_rate: float
    drop_percentage: float
    
    # Statistical significance
    sigma_value: float  # How many standard deviations from baseline
    is_significant: bool  # Whether drop is statistically significant
    
    # Session counts
    current_sessions: int
    baseline_sessions: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "funnel_step": "otp_verification",
                "detected_at": 1707289800000,
                "current_conversion_rate": 72.0,
                "baseline_conversion_rate": 85.0,
                "drop_percentage": 15.3,
                "sigma_value": 2.8,
                "is_significant": True,
                "current_sessions": 100,
                "baseline_sessions": 1000
            }
        }


class DiagnosisEvidence(BaseModel):
    """
    Evidence collected for AI diagnosis
    """
    # Error patterns
    error_types: Dict[str, int] = Field(default_factory=dict, description="Error type frequency")
    top_errors: List[str] = Field(default_factory=list, description="Most common error messages")
    
    # User behavior
    avg_retry_count: Optional[float] = Field(None, description="Average retries before success")
    time_to_completion_change: Optional[float] = Field(None, description="Change in completion time (%)")
    
    # Segmentation
    affected_countries: List[str] = Field(default_factory=list)
    affected_devices: List[str] = Field(default_factory=list)
    affected_versions: List[str] = Field(default_factory=list)
    
    # Sample sessions
    struggling_session_ids: List[str] = Field(default_factory=list, description="Sessions with issues")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_types": {"network_timeout": 45, "invalid_otp": 23, "rate_limit": 12},
                "top_errors": [
                    "Connection timeout after 30s",
                    "Invalid OTP code entered",
                    "Too many attempts - rate limited"
                ],
                "avg_retry_count": 2.3,
                "time_to_completion_change": 45.5,
                "affected_countries": ["IN", "PH"],
                "affected_devices": ["mobile"],
                "affected_versions": ["2.1.0"],
                "struggling_session_ids": ["sess_abc123", "sess_def456"]
            }
        }


class AIDiagnosis(BaseModel):
    """
    AI-generated diagnosis from DeepSeek
    """
    root_cause: str = Field(..., description="Identified root cause")
    confidence: float = Field(..., description="Confidence score 0-100")
    explanation: str = Field(..., description="Detailed explanation")
    
    # Actionable insights
    recommended_actions: List[str] = Field(default_factory=list)
    code_locations: List[str] = Field(default_factory=list, description="Suspected code locations")
    
    # AI metadata
    model_used: str = Field(..., description="AI model used for diagnosis")
    diagnosis_time_ms: int = Field(..., description="Time taken for diagnosis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "root_cause": "Twilio API timeout during high traffic in India region",
                "confidence": 87.5,
                "explanation": "Analysis shows 45 network timeout errors concentrated in India mobile users. The timeout pattern (30s) matches Twilio's default, suggesting the OTP provider is experiencing latency during peak hours (7-9pm IST).",
                "recommended_actions": [
                    "Increase Twilio timeout to 45s",
                    "Add retry logic with exponential backoff",
                    "Consider India-specific OTP provider as backup"
                ],
                "code_locations": [
                    "services/otp_service.py:sendOTP()",
                    "config/twilio.py:TIMEOUT setting"
                ],
                "model_used": "deepseek-chat",
                "diagnosis_time_ms": 2340
            }
        }


class Issue(BaseModel):
    """
    Tracked conversion issue
    """
    id: str
    status: IssueStatus
    severity: IssueSeverity
    
    # Core data
    anomaly: Anomaly
    evidence: DiagnosisEvidence
    diagnosis: Optional[AIDiagnosis] = None
    
    # Tracking
    created_at: int  # Unix timestamp in ms
    diagnosed_at: Optional[int] = None
    fixed_at: Optional[int] = None
    measured_at: Optional[int] = None
    
    # Results
    fix_commit_sha: Optional[str] = None
    fix_pr_url: Optional[str] = None
    jira_ticket_key: Optional[str] = None
    post_fix_conversion_rate: Optional[float] = None
    uplift_percentage: Optional[float] = None
    updated_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))
    
    # Slack tracking
    slack_thread_ts: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "issue_1707289800_otp_verification",
                "status": "diagnosed",
                "severity": "high",
                "anomaly": {
                    "funnel_step": "otp_verification",
                    "detected_at": 1707289800000,
                    "drop_percentage": 15.3
                },
                "created_at": 1707289800000,
                "diagnosed_at": 1707289860000
            }
        }


class IssueCreateRequest(BaseModel):
    """Request to create a new issue from detected anomaly"""
    anomaly: Anomaly
    evidence: DiagnosisEvidence


class IssueResponse(BaseModel):
    """Response with issue details"""
    issue: Optional[Issue]
    message: str
