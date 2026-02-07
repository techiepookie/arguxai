"""Slack notification API endpoints"""

from fastapi import APIRouter, HTTPException, status
from app.integrations.slack_client import slack_client
from app.services.issue_manager import issue_manager
from app.core.dependencies import APIKeyDep
from app.core.logging import logger

router = APIRouter()


@router.post("/notify-anomaly/{issue_id}")
async def notify_anomaly(
    issue_id: str,
    api_key: APIKeyDep = None
):
    """
    Send anomaly detection alert to Slack
    
    **Workflow**:
    - Fetches issue details
    - Builds Block Kit message with severity emoji, metrics, AI diagnosis
    - Sends to configured Slack webhook
    - Includes action buttons (Generate PR, View Details)
    
    **Example**:
    ```
    POST /api/slack/notify-anomaly/issue_1707289800_otpverification
    ```
    
    **Slack Message Includes**:
    - Severity level with emoji (🚨 Critical, ⚠️ High, ⚡ Medium, ℹ️ Low)
    - Drop percentage and conversion rates
    - Statistical significance (sigma value)
    - AI diagnosis with confidence score
    - Top errors and affected segments
    - Action buttons for quick response
    """
    try:
        # Get issue
        issue = issue_manager.get_issue(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue {issue_id} not found"
            )
        
        # Send Slack notification
        result = await slack_client.send_anomaly_alert(issue)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send Slack notification: {result.get('error')}"
            )
        
        logger.info("Anomaly notification sent to Slack", issue_id=issue_id)
        
        return {
            "success": True,
            "message": "Anomaly alert sent to Slack",
            "issue_id": issue_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to send anomaly notification", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification failed: {str(e)}"
        )


@router.post("/notify-pr/{issue_id}")
async def notify_pr_created(
    issue_id: str,
    api_key: APIKeyDep = None
):
    """
    Send PR creation notification to Slack
    
    **Triggered After**: PR is generated for an issue
    
    **Slack Message Includes**:
    - Issue ID and PR link
    - Root cause from AI diagnosis
    - Action button to review PR
    - Button to mark as merged
    
    **Example**:
    ```
    POST /api/slack/notify-pr/issue_1707289800_otpverification
    ```
    """
    try:
        # Get issue
        issue = issue_manager.get_issue(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue {issue_id} not found"
            )
        
        if not issue.fix_pr_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issue does not have a PR yet"
            )
        
        # Extract PR number from URL (simple parsing)
        pr_number = int(issue.fix_pr_url.split("/")[-1]) if issue.fix_pr_url else 0
        
        # Send notification
        result = await slack_client.send_pr_created(
            issue=issue,
            pr_url=issue.fix_pr_url,
            pr_number=pr_number
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send notification: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": "PR notification sent to Slack",
            "pr_url": issue.fix_pr_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to send PR notification", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification failed: {str(e)}"
        )


@router.post("/notify-verified/{issue_id}")
async def notify_fix_verified(
    issue_id: str,
    api_key: APIKeyDep = None
):
    """
    Send fix verification notification to Slack
    
    **Triggered After**: Impact measurement (24h after fix)
    
    **Slack Message Includes**:
    - Uplift percentage
    - Post-fix conversion rate vs original
    - PR link
    - Celebration message 🎉
    
    **Example**:
    ```
    POST /api/slack/notify-verified/issue_1707289800_otpverification
    ```
    """
    try:
        # Get issue
        issue = issue_manager.get_issue(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue {issue_id} not found"
            )
        
        if not issue.uplift_percentage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issue has not been measured yet"
            )
        
        # Send notification
        result = await slack_client.send_fix_verified(
            issue=issue,
            uplift_percentage=issue.uplift_percentage
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send notification: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": "Verification notification sent to Slack",
            "uplift": issue.uplift_percentage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to send verification notification", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification failed: {str(e)}"
        )


@router.post("/daily-summary")
async def send_daily_summary(
    api_key: APIKeyDep = None
):
    """
    Send daily summary report to Slack
    
    **Scheduled**: Called by background job (once per day)
    
    **Summary Includes**:
    - Issues detected today
    - Issues fixed today
    - Average uplift percentage
    - Date
    
    **Example**:
    ```
    POST /api/slack/daily-summary
    ```
    """
    try:
        # Calculate stats
        all_issues = issue_manager.list_issues()
        
        # In real implementation, filter by date
        # For demo, use all issues
        issues_detected = len([i for i in all_issues if i.status])
        issues_fixed = len([i for i in all_issues if i.fix_pr_url])
        
        uplifts = [i.uplift_percentage for i in all_issues if i.uplift_percentage]
        avg_uplift = sum(uplifts) / len(uplifts) if uplifts else 0
        
        # Send summary
        result = await slack_client.send_daily_summary(
            issues_detected=issues_detected,
            issues_fixed=issues_fixed,
            avg_uplift=avg_uplift
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send summary: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": "Daily summary sent to Slack",
            "stats": {
                "detected": issues_detected,
                "fixed": issues_fixed,
                "avg_uplift": avg_uplift
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to send daily summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary failed: {str(e)}"
        )
