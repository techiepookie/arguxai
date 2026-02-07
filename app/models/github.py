"""GitHub data models for PR generation"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CodeLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUBY = "ruby"


class FileChange(BaseModel):
    """Individual file change in a PR"""
    file_path: str = Field(..., description="Relative path to file in repo")
    original_content: str = Field(..., description="Original file content")
    modified_content: str = Field(..., description="AI-generated fixed content")
    language: CodeLanguage = Field(..., description="Programming language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "services/otp_service.py",
                "original_content": "TIMEOUT = 30",
                "modified_content": "TIMEOUT = 45",
                "language": "python"
            }
        }


class PRMetadata(BaseModel):
    """Pull request metadata"""
    title: str = Field(..., description="PR title")
    description: str = Field(..., description="PR description (markdown)")
    branch_name: str = Field(..., description="Feature branch name")
    base_branch: str = Field("main", description="Base branch (default: main)")
    labels: List[str] = Field(default_factory=list, description="PR labels")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Fix: Increase Twilio timeout for OTP verification",
                "description": "## Issue\nOTP verification experiencing 15% drop...",
                "branch_name": "fix/otp-timeout-increase",
                "base_branch": "main",
                "labels": ["bug", "conversion-fix", "ai-generated"]
            }
        }


class PRGenerationRequest(BaseModel):
    """Request to generate a pull request"""
    issue_id: str = Field(..., description="Issue ID to fix")
    repository: str = Field(..., description="GitHub repository (owner/repo)")
    target_files: List[str] = Field(..., description="Files to modify")
    base_branch: Optional[str] = Field("main", description="Base branch")


class PRGenerationResponse(BaseModel):
    """Response from PR generation"""
    success: bool
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    branch_name: Optional[str] = None
    commit_sha: Optional[str] = None
    files_changed: int = 0
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "pr_url": "https://github.com/owner/repo/pull/123",
                "pr_number": 123,
                "branch_name": "fix/otp-timeout-increase",
                "commit_sha": "abc123def456",
                "files_changed": 2,
                "message": "PR created successfully"
            }
        }
