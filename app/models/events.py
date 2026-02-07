"""Event data models using Pydantic"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Supported event types"""
    PAGE_VIEW = "page_view"
    BUTTON_CLICK = "button_click"
    FORM_SUBMIT = "form_submit"
    OTP_SENT = "otp_sent"
    OTP_VERIFIED = "otp_verified"
    OTP_FAILED = "otp_failed"
    ERROR = "error"
    RESEND_CLICK = "resend_click"
    CUSTOM = "custom"


class DeviceType(str, Enum):
    """Device types"""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    UNKNOWN = "unknown"


class Event(BaseModel):
    """
    User event model
    
    Represents a single user interaction event from the SDK
    """
    # Event identification
    event_type: str = Field(..., description="Type of event")  # Changed from EventType enum to str
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User ID if logged in")
    
    # Timing
    timestamp: int = Field(..., description="UTC timestamp in milliseconds")
    
    # Context
    funnel_step: Optional[str] = Field(None, description="Funnel step name")
    device_type: str = Field("unknown", description="Device type")  # Changed from DeviceType enum to str
    country: str = Field("US", description="ISO country code")
    app_version: str = Field("1.0.0", description="Application version")
    
    # Error tracking
    error_type: Optional[str] = Field(None, description="Error type if applicable")
    error_message: Optional[str] = Field(None, description="Error message")
    
    # Custom properties
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom event properties")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Ensure timestamp is reasonable (not in future, not too old)"""
        now = int(datetime.utcnow().timestamp() * 1000)
        
        # Not more than 1 day in the future
        if v > now + (24 * 60 * 60 * 1000):
            raise ValueError("Timestamp cannot be more than 1 day in the future")
        
        # Not more than 30 days in the past
        if v < now - (30 * 24 * 60 * 60 * 1000):
            raise ValueError("Timestamp cannot be more than 30 days in the past")
        
        return v
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Ensure session ID is not empty"""
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "otp_sent",
                "session_id": "sess_abc123xyz",
                "user_id": "user_12345",
                "timestamp": 1675890123456,
                "funnel_step": "otp_verification",
                "device_type": "mobile",
                "country": "IN",
                "app_version": "2.1.0",
                "properties": {
                    "phone_number": "+91XXXXXXXXXX",
                    "provider": "twilio"
                }
            }
        }


class EventBatch(BaseModel):
    """Batch of events from SDK"""
    events: list[Event] = Field(..., description="List of events to ingest")
    
    @field_validator('events')
    @classmethod
    def validate_events(cls, v: list[Event]) -> list[Event]:
        """Ensure batch is not empty and not too large"""
        if not v:
            raise ValueError("Event batch cannot be empty")
        
        if len(v) > 1000:
            raise ValueError("Event batch cannot exceed 1000 events")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "events": [
                    {
                        "event_type": "page_view",
                        "session_id": "sess_abc123",
                        "timestamp": 1675890123456,
                        "funnel_step": "signup_form",
                        "device_type": "mobile",
                        "country": "US",
                        "app_version": "2.0.0"
                    }
                ]
            }
        }


class EventIngestResponse(BaseModel):
    """Response from event ingestion endpoint"""
    success: bool
    events_ingested: int
    events_rejected: int = 0
    message: str
    errors: list[str] = Field(default_factory=list)
