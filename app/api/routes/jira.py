"""Jira ticket creation API endpoints"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.models.jira import JiraCreateResponse, JiraIssue
from app.services.jira_ticket_service import jira_ticket_service
from app.services.issue_manager import issue_manager
from app.core.dependencies import APIKeyDep
from app.core.logging import logger

router = APIRouter()


@router.post("/create-ticket/{issue_id}", response_model=JiraCreateResponse)
async def create_jira_ticket(
    issue_id: str,
    project_key: Optional[str] = Query(None, description="Jira project key override"),
    api_key: APIKeyDep = None
) -> JiraCreateResponse:
    """
    Create Jira ticket for detected conversion issue
    
    **Workflow**:
    1. Fetch ArguxAI issue details
    2. Map to Jira issue format
    3. Determine team assignment based on funnel step
    4. Add rich description with metrics, AI diagnosis, evidence
    5. Create Jira ticket
    6. Return ticket details
    
    **Team Assignment Logic**:
    - `signup_form` → Frontend Team
    - `otp_verification` → Backend Team
    - `payment` → Payments Team
    - `checkout` → Frontend Team
    - `onboarding` → Product Team
    
    **Jira Ticket Includes**:
    - Severity-based priority (Critical → Highest, High → High, etc.)
    - Conversion metrics (current rate, baseline, drop %)
    - Statistical significance (sigma value)
    - AI diagnosis with confidence
    - Recommended actions
    - Top errors and affected segments
    - Links to ArguxAI issue and GitHub PR (if available)
    
    **Example**:
    ```
    POST /api/jira/create-ticket/issue_1707289800_otpverification?project_key=CONV
    ```
    
    **Returns**: Jira ticket key, URL, and status
    """
    try:
        # Get issue
        issue = issue_manager.get_issue(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue {issue_id} not found"
            )
        
        logger.info(
            "Creating Jira ticket",
            issue_id=issue_id,
            severity=issue.severity
        )
        
        # Create Jira ticket
        jira_issue = await jira_ticket_service.create_ticket_for_issue(
            issue=issue,
            project_key=project_key
        )
        
        # Update issue with Jira ticket key
        await issue_manager.mark_jira_created(issue_id, jira_issue.key)
        
        return JiraCreateResponse(
            success=True,
            jira_issue=jira_issue,
            message=f"Jira ticket {jira_issue.key} created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create Jira ticket", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ticket creation failed: {str(e)}"
        )


@router.post("/link-pr/{jira_key}")
async def link_pr_to_ticket(
    jira_key: str,
    pr_url: str = Query(..., description="GitHub PR URL"),
    api_key: APIKeyDep = None
):
    """
    Add PR link as comment to Jira ticket
    
    **Use Case**: After generating a PR, link it to the Jira ticket
    
    **Example**:
    ```
    POST /api/jira/link-pr/CONV-123?pr_url=https://github.com/org/repo/pull/456
    ```
    """
    try:
        await jira_ticket_service.add_pr_comment(jira_key, pr_url)
        
        return {
            "success": True,
            "message": f"PR linked to {jira_key}"
        }
        
    except Exception as e:
        logger.error("Failed to link PR", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link PR: {str(e)}"
        )


@router.post("/resolve/{jira_key}")
async def resolve_jira_ticket(
    jira_key: str,
    uplift_percentage: float = Query(..., description="Measured uplift %"),
    api_key: APIKeyDep = None
):
    """
    Mark Jira ticket as resolved with uplift metrics
    
    **Triggered After**: Impact measurement (24h after fix deployment)
    
    **Actions**:
    - Adds comment with uplift metrics
    - Transitions ticket to "Done" status
    
    **Example**:
    ```
    POST /api/jira/resolve/CONV-123?uplift_percentage=15.2
    ```
    """
    try:
        await jira_ticket_service.mark_resolved(jira_key, uplift_percentage)
        
        return {
            "success": True,
            "message": f"{jira_key} marked as resolved with +{uplift_percentage:.1f}% uplift"
        }
        
    except Exception as e:
        logger.error("Failed to resolve ticket", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve: {str(e)}"
        )


@router.get("/issue/{jira_key}", response_model=JiraIssue)
async def get_jira_issue(
    jira_key: str,
    api_key: APIKeyDep = None
) -> JiraIssue:
    """
    Get Jira issue details
    
    **Returns**: Current status, assignee, summary
    
    **Example**:
    ```
    GET /api/jira/issue/CONV-123
    ```
    """
    try:
        from app.integrations.jira_client import jira_client
        
        issue = await jira_client.get_issue(jira_key)
        return issue
        
    except Exception as e:
        logger.error("Failed to get Jira issue", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue not found: {str(e)}"
        )
