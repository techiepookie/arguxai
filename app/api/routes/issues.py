"""Issues and diagnosis API endpoints"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.issues import (
    Issue, IssueStatus, IssueSeverity, IssueCreateRequest, IssueResponse, Anomaly
)
from app.models.metrics import MetricPeriod
from app.services.anomaly_detector import anomaly_detector
from app.services.issue_manager import issue_manager
from app.core.dependencies import APIKeyDep
from app.core.logging import logger
from app.config import settings

router = APIRouter()


class DetectIssuesResponse(BaseModel):
    """Response for detect issues endpoint"""
    issues_detected: int
    issues: List[Issue]
    timestamp: int


@router.post("/detect-single", response_model=IssueResponse)
async def detect_and_create_issue(
    funnel_step: str = Query(..., description="Funnel step to check for anomalies"),
    current_period: MetricPeriod = Query(
        MetricPeriod.LAST_HOUR,
        description="Current period to analyze"
    ),
    baseline_period: MetricPeriod = Query(
        MetricPeriod.LAST_7_DAYS,
        description="Baseline period for comparison"
    ),
    auto_diagnose: bool = Query(True, description="Automatically run AI diagnosis"),
    api_key: APIKeyDep = None
) -> IssueResponse:
    """
    Detect anomalies and create issue with AI diagnosis
    
    **Workflow**:
    1. Run anomaly detection on funnel step
    2. If anomaly detected, create issue
    3. Collect evidence (errors, segments, behavior)
    4. Run AI diagnosis (if auto_diagnose=true)
    5. Return complete issue with diagnosis
    
    **Example**:
    ```
    POST /api/issues/detect?funnel_step=otp_verification&auto_diagnose=true
    ```
    """
@router.post("/detect", response_model=DetectIssuesResponse)
async def detect_conversion_issues(
    api_key: APIKeyDep = None
) -> DetectIssuesResponse:
    """
    Detect conversion anomalies across all funnel steps
    
    Returns list of issues with anomaly details
    """
    try:
        # In demo mode, use demo anomalies
        if settings.demo_mode:
            anomalies = anomaly_detector._generate_demo_anomalies()
        else:
            # Login funnel steps for demo app
            funnel_steps = [
                "login_page",
               "login_form",
                "login_button_click",
                "login_complete"
            ]
            
            # Scan for anomalies
            anomalies = await anomaly_detector.scan_all_funnel_steps(funnel_steps)
        
        # Create issues from anomalies
        issues = []
        for anomaly in anomalies:
            issue = await issue_manager.create_issue(anomaly, auto_diagnose=True)
            issues.append(issue)
        
        logger.info(f"Detected {len(issues)} conversion issues")
        
        return DetectIssuesResponse(
            issues_detected=len(issues),
            issues=issues,
            timestamp=int(datetime.utcnow().timestamp() * 1000)
        )
        
    except Exception as e:
        logger.error(f"Issue detection failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Issue detection failed: {str(e)}"
        )


@router.get("", response_model=List[Issue])
async def list_issues(
    status_filter: Optional[IssueStatus] = Query(None, alias="status"),
    severity_filter: Optional[IssueSeverity] = Query(None, alias="severity"),
    api_key: APIKeyDep = None
) -> List[Issue]:
    """
    List all issues with optional filters
    
    **Query Parameters**:
    - `status`: Filter by status (detected, diagnosed, fixed, measuring, verified, closed)
    - `severity`: Filter by severity (critical, high, medium, low)
    
    **Example**:
    ```
    GET /api/issues?status=diagnosed&severity=high
    ```
    
    **Returns**: List of issues sorted by creation time (newest first)
    """
    try:
        issues = issue_manager.list_issues(
            status=status_filter,
            severity=severity_filter
        )
        
        logger.info(
            "Issues listed",
            total_count=len(issues),
            status_filter=status_filter,
            severity_filter=severity_filter
        )
        
        return issues
        
    except Exception as e:
        logger.error("Failed to list issues", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list issues: {str(e)}"
        )


@router.get("/{issue_id}", response_model=Issue)
async def get_issue(
    issue_id: str,
    api_key: APIKeyDep = None
) -> Issue:
    """
    Get details of a specific issue
    
    **Parameters**:
    - `issue_id`: Unique issue identifier
    
    **Returns**: Complete issue with anomaly, evidence, diagnosis, and fix status
    """
    try:
        issue = issue_manager.get_issue(issue_id)
        
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue {issue_id} not found"
            )
        
        return issue
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get issue", error=str(e), issue_id=issue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get issue: {str(e)}"
        )


@router.post("/{issue_id}/diagnose", response_model=Issue)
async def diagnose_issue(
    issue_id: str,
    api_key: APIKeyDep = None
) -> Issue:
    """
    Run AI diagnosis on an existing issue
    
    Uses DeepSeek to analyze evidence and provide:
    - Root cause identification
    - Confidence score
    - Detailed explanation
    - Recommended actions
    - Code locations to fix
    
    **Example**:
    
    POST /api/issues/{issue_id}/diagnose
    """
    try:
        issue = await issue_manager.diagnose_issue(issue_id)
        
        logger.info(
            "Issue diagnosed via API",
            issue_id=issue_id,
            confidence=issue.diagnosis.confidence if issue.diagnosis else None
        )
        
        return issue
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to diagnose issue", error=str(e), issue_id=issue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis failed: {str(e)}"
        )


@router.post("/{issue_id}/mark-fixed", response_model=Issue)
async def mark_issue_fixed(
    issue_id: str,
    commit_sha: Optional[str] = Query(None, description="Git commit SHA"),
    pr_url: Optional[str] = Query(None, description="Pull request URL"),
    api_key: APIKeyDep = None
) -> Issue:
    """
    Mark issue as fixed by engineer
    
    **Parameters**:
    - `commit_sha`: Git commit SHA of the fix
    - `pr_url`: Pull request URL
    
    **Next Steps**: System will schedule measurement 24h after fix
    
    **Example**:
    ```
    POST /api/issues/{issue_id}/mark-fixed?pr_url=https://github.com/org/repo/pull/123
    ```
    """
    
    
    try:
        issue = await issue_manager.mark_fixed(
            issue_id=issue_id,
            commit_sha=commit_sha,
            pr_url=pr_url
        )
        
        return issue
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to mark issue as fixed", error=str(e), issue_id=issue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark as fixed: {str(e)}"
        )


@router.post("/{issue_id}/measure", response_model=Issue)
async def measure_issue_impact(
    issue_id: str,
    api_key: APIKeyDep = None
) -> Issue:
    """
    Measure impact of fix (typically called 24h after fix)
    
    **Returns**: Issue with:
    - Post-fix conversion rate
    - Uplift percentage
    - Verification status
    
    **Example**:
    ```
    POST /api/issues/{issue_id}/measure
    ```
    """
    try:
        issue = await issue_manager.measure_impact(issue_id)
        
        logger.info(
            "Impact measured",
            issue_id=issue_id,
            uplift=issue.uplift_percentage
        )
        
        return issue
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to measure impact", error=str(e), issue_id=issue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Measurement failed: {str(e)}"
        )
