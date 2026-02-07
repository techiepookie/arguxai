"""Jira data models for issue tracking"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class JiraIssueType(str, Enum):
    """Jira issue types"""
    BUG = "Bug"
    TASK = "Task"
    STORY = "Story"
    INCIDENT = "Incident"


class JiraPriority(str, Enum):
    """Jira priority levels"""
    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"


class JiraTeam(str, Enum):
    """Teams that can be assigned"""
    BACKEND = "Backend"
    FRONTEND = "Frontend"
    MOBILE = "Mobile"
    DEVOPS = "DevOps"
    QA = "QA"
    DESIGN = "Design"


class JiraIssueCreate(BaseModel):
    """Request to create Jira issue"""
    project_key: str = Field(..., description="Jira project key (e.g., 'CONV')")
    summary: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description in Jira markdown")
    issue_type: JiraIssueType = Field(default=JiraIssueType.BUG)
    priority: JiraPriority = Field(default=JiraPriority.HIGH)
    assignee: Optional[str] = Field(None, description="Jira username or email")
    labels: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_key": "CONV",
                "summary": "OTP Verification - 21% Drop in Conversion",
                "description": "AI detected conversion drop...",
                "issue_type": "Bug",
                "priority": "High",
                "assignee": "admin@arguxai.com",
                "labels": ["arguxai", "conversion", "urgent"],
                "components": ["OTP Service"]
            }
        }


class JiraIssue(BaseModel):
    """Created Jira issue"""
    key: str = Field(..., description="Jira issue key (e.g., 'CONV-123')")
    id: str = Field(..., description="Jira issue ID")
    url: str = Field(..., description="Issue URL")
    summary: str
    status: str
    assignee: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "key": "CONV-123",
                "id": "10234",
                "url": "https://yourcompany.atlassian.net/browse/CONV-123",
                "summary": "OTP Verification - 21% Drop",
                "status": "To Do",
                "assignee": "John Doe"
            }
        }


class JiraCreateResponse(BaseModel):
    """Response from creating Jira issue"""
    success: bool
    jira_issue: Optional[JiraIssue] = None
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "jira_issue": {
                    "key": "CONV-123",
                    "url": "https://yourcompany.atlassian.net/browse/CONV-123"
                },
                "message": "Jira issue created successfully"
            }
        }
