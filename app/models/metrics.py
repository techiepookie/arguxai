"""Metrics data models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FunnelStep(str, Enum):
    """Standard funnel steps"""
    SIGNUP_FORM = "signup_form"
    OTP_VERIFICATION = "otp_verification"
    PROFILE_CREATION = "profile_creation"
    CONVERSION = "conversion"


class MetricPeriod(str, Enum):
    """Time periods for metric calculation"""
    LAST_HOUR = "last_hour"
    LAST_24_HOURS = "last_24_hours"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"


class RecentIssue(BaseModel):
    """Simplified issue for dashboard list"""
    id: str
    funnel_step: str
    severity: str
    drop_percentage: float
    detected_at: int



class FunnelMetrics(BaseModel):
    """
    Metrics for a single funnel step
    """
    funnel_step: str
    period: str
    timestamp_start: int  # Unix timestamp in ms
    timestamp_end: int
    
    # Raw counts
    total_sessions: int = Field(..., description="Total unique sessions")
    completed_sessions: int = Field(..., description="Sessions that completed this step")
    
    # Calculated metrics
    conversion_rate: float = Field(..., description="Completion rate (0-100%)")
    drop_off_rate: float = Field(..., description="Drop-off rate (0-100%)")
    
    # Segmentation
    by_country: dict[str, int] = Field(default_factory=dict)
    by_device: dict[str, int] = Field(default_factory=dict)
    
    # Statistical measures
    mean_time_on_step: Optional[float] = Field(None, description="Average time in seconds")
    median_time_on_step: Optional[float] = Field(None, description="Median time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "funnel_step": "otp_verification",
                "period": "last_24_hours",
                "timestamp_start": 1707203400000,
                "timestamp_end": 1707289800000,
                "total_sessions": 1000,
                "completed_sessions": 850,
                "conversion_rate": 85.0,
                "drop_off_rate": 15.0,
                "by_country": {"US": 600, "IN": 250, "UK": 150},
                "by_device": {"mobile": 800, "desktop": 200}
            }
        }


class ComparisonMetrics(BaseModel):
    """
    Comparison between current and baseline metrics
    """
    current: FunnelMetrics
    baseline: FunnelMetrics
    
    # Calculated differences
    conversion_rate_delta: float = Field(..., description="Change in conversion rate (percentage points)")
    sessions_delta: int = Field(..., description="Change in total sessions")
    drop_detected: bool = Field(..., description="Whether significant drop was detected")
    drop_percentage: Optional[float] = Field(None, description="Percentage drop if detected")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current": {
                    "funnel_step": "otp_verification",
                    "period": "last_hour",
                    "timestamp_start": 1707286200000,
                    "timestamp_end": 1707289800000,
                    "total_sessions": 100,
                    "completed_sessions": 72,
                    "conversion_rate": 72.0,
                    "drop_off_rate": 28.0
                },
                "baseline": {
                    "funnel_step": "otp_verification",
                    "period": "last_24_hours",
                    "timestamp_start": 1707203400000,
                    "timestamp_end": 1707289800000,
                    "total_sessions": 1000,
                    "completed_sessions": 850,
                    "conversion_rate": 85.0,
                    "drop_off_rate": 15.0
                },
                "conversion_rate_delta": -13.0,
                "sessions_delta": -900,
                "drop_detected": True,
                "drop_percentage": 15.3
            }
        }
