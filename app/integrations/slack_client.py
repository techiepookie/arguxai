"""Slack notification client"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import settings
from app.core.logging import logger
from app.models.issues import Issue, IssueSeverity


class SlackClient:
    """
    Slack webhook client for notifications
    
    Uses Block Kit for rich, interactive messages
    """
    
    def __init__(self):
        self.webhook_url = settings.slack_webhook_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def send_anomaly_alert(
        self,
        issue: Issue,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send anomaly detection alert to Slack
        
        Args:
            issue: Detected issue
            channel: Optional channel override
            
        Returns:
            Slack API response
        """
        try:
            # Severity emoji mapping
            severity_emoji = {
                IssueSeverity.CRITICAL: "🚨",
                IssueSeverity.HIGH: "⚠️",
                IssueSeverity.MEDIUM: "⚡",
                IssueSeverity.LOW: "ℹ️"
            }
            
            emoji = severity_emoji.get(issue.severity, "📊")
            
            # Build Block Kit message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} Conversion Drop Detected - {issue.severity.value.upper()}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Funnel Step:*\n{issue.anomaly.funnel_step.replace('_', ' ').title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Drop:*\n{issue.anomaly.drop_percentage:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Current Rate:*\n{issue.anomaly.current_conversion_rate:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Baseline:*\n{issue.anomaly.baseline_conversion_rate:.1f}%"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Significance:*\n{issue.anomaly.sigma_value}σ"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Sessions:*\n{issue.anomaly.current_sessions}"
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
            
            # Add diagnosis if available
            if issue.diagnosis:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🤖 AI Diagnosis ({issue.diagnosis.confidence:.0f}% confidence)*\n{issue.diagnosis.root_cause}"
                    }
                })
                
                # Add recommended actions
                if issue.diagnosis.recommended_actions:
                    actions_text = "\n".join([
                        f"• {action}" 
                        for action in issue.diagnosis.recommended_actions[:3]
                    ])
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*💡 Recommended Actions:*\n{actions_text}"
                        }
                    })
            
            # Add evidence summary
            if issue.evidence.error_types:
                top_errors = list(issue.evidence.error_types.items())[:2]
                error_text = "\n".join([
                    f"• `{error}`: {count} occurrences"
                    for error, count in top_errors
                ])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 Top Errors:*\n{error_text}"
                    }
                })
            
            # Add action buttons
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔧 Generate PR",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": issue.id,
                        "action_id": "generate_pr"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 View Details",
                            "emoji": True
                        },
                        "value": issue.id,
                        "action_id": "view_issue"
                    }
                ]
            })
            
            # Build payload
            payload = {
                "blocks": blocks,
                "text": f"Conversion drop detected: {issue.anomaly.funnel_step}"  # Fallback text
            }
            
            if channel:
                payload["channel"] = channel
            
            # Send to Slack
            response = await self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(
                "Slack anomaly alert sent",
                issue_id=issue.id,
                severity=issue.severity
            )
            
            return {"success": True, "message": "Alert sent"}
            
        except Exception as e:
            logger.error("Failed to send Slack alert", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def send_pr_created(
        self,
        issue: Issue,
        pr_url: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Send PR creation notification
        
        Args:
            issue: Issue that was fixed
            pr_url: Pull request URL
            pr_number: PR number
            
        Returns:
            Slack API response
        """
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Pull Request Created",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"AI-generated fix for *{issue.anomaly.funnel_step}* conversion drop"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Issue:*\n{issue.id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*PR:*\n<{pr_url}|#{pr_number}>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Root Cause:*\n{issue.diagnosis.root_cause if issue.diagnosis else 'N/A'}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Review PR",
                                "emoji": True
                            },
                            "style": "primary",
                            "url": pr_url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Mark as Merged",
                                "emoji": True
                            },
                            "value": issue.id,
                            "action_id": "mark_merged"
                        }
                    ]
                }
            ]
            
            payload = {
                "blocks": blocks,
                "text": f"PR #{pr_number} created"
            }
            
            response = await self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Slack PR notification sent", pr_number=pr_number)
            
            return {"success": True}
            
        except Exception as e:
            logger.error("Failed to send PR notification", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def send_fix_verified(
        self,
        issue: Issue,
        uplift_percentage: float
    ) -> Dict[str, Any]:
        """
        Send fix verification notification with uplift metrics
        
        Args:
            issue: Verified issue
            uplift_percentage: Measured uplift
            
        Returns:
            Slack API response
        """
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎉 Fix Verified - Conversion Improved!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"The fix for *{issue.anomaly.funnel_step}* has been verified"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Uplift:*\n+{uplift_percentage:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Post-Fix Rate:*\n{issue.post_fix_conversion_rate:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Original Rate:*\n{issue.anomaly.current_conversion_rate:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*PR:*\n<{issue.fix_pr_url}|View PR>"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Issue: {issue.id} | Severity: {issue.severity.value}"
                        }
                    ]
                }
            ]
            
            payload = {
                "blocks": blocks,
                "text": f"Fix verified: +{uplift_percentage:.1f}% uplift"
            }
            
            response = await self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Slack verification notification sent", uplift=uplift_percentage)
            
            return {"success": True}
            
        except Exception as e:
            logger.error("Failed to send verification notification", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def send_daily_summary(
        self,
        issues_detected: int,
        issues_fixed: int,
        avg_uplift: float
    ) -> Dict[str, Any]:
        """
        Send daily summary report
        
        Args:
            issues_detected: Number of issues detected today
            issues_fixed: Number of issues fixed today
            avg_uplift: Average uplift percentage
            
        Returns:
            Slack API response
        """
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 ArguxAI Daily Summary",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Issues Detected:*\n{issues_detected}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Issues Fixed:*\n{issues_fixed}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Avg Uplift:*\n+{avg_uplift:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Date:*\n{datetime.utcnow().strftime('%Y-%m-%d')}"
                        }
                    ]
                }
            ]
            
            payload = {"blocks": blocks, "text": "Daily summary"}
            
            response = await self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Slack daily summary sent")
            
            return {"success": True}
            
        except Exception as e:
            logger.error("Failed to send daily summary", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if Slack webhook is configured"""
        return bool(self.webhook_url)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global Slack client instance
slack_client = SlackClient()
