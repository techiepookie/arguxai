"""Jira ticket creation service"""

from typing import Optional
from datetime import datetime
from app.models.issues import Issue, IssueSeverity
from app.models.jira import JiraIssueCreate, JiraIssue, JiraIssueType, JiraPriority, JiraTeam
from app.integrations.jira_client import jira_client
from app.core.logging import logger
from app.config import settings


class JiraTicketService:
    """
    Orchestrate Jira ticket creation for conversion issues
    
    Workflow:
    1. Map ArguxAI issue to Jira issue
    2. Determine team assignment based on funnel step
    3. Create Jira ticket
    4. Post updates back to issue
    """
    
    def __init__(self):
        self.default_project_key = settings.jira_project_key or "CONV"
    
    async def create_ticket_for_issue(
        self,
        issue: Issue,
        project_key: Optional[str] = None
    ) -> JiraIssue:
        """
        Create Jira ticket for detected issue
        
        Args:
            issue: ArguxAI issue
            project_key: Optional Jira project key override
            
        Returns:
            Created Jira issue
        """
        try:
            # Use demo mode if Jira not configured
            if settings.demo_mode or not settings.jira_api_token:
                return self._generate_demo_ticket(issue)
            
            logger.info(
                "Creating Jira ticket for issue",
                issue_id=issue.id,
                severity=issue.severity
            )
            
            # Build ticket data
            ticket_data = self._build_ticket_data(issue, project_key)
            
            # Create Jira issue
            jira_issue = await jira_client.create_issue(ticket_data)
            
            logger.info(
                "Jira ticket created",
                jira_key=jira_issue.key,
                issue_id=issue.id
            )
            
            return jira_issue
            
        except Exception as e:
            logger.error("Failed to create Jira ticket", error=str(e))
            raise
    
    def _build_ticket_data(
        self,
        issue: Issue,
        project_key: Optional[str]
    ) -> JiraIssueCreate:
        """Build Jira ticket from ArguxAI issue"""
        
        # Map severity to priority
        priority_map = {
            IssueSeverity.CRITICAL: JiraPriority.HIGHEST,
            IssueSeverity.HIGH: JiraPriority.HIGH,
            IssueSeverity.MEDIUM: JiraPriority.MEDIUM,
            IssueSeverity.LOW: JiraPriority.LOW
        }
        
        priority = priority_map.get(issue.severity, JiraPriority.MEDIUM)
        
        # Build summary
        summary = f"{issue.anomaly.funnel_step.replace('_', ' ').title()} - {abs(issue.anomaly.drop_percentage):.1f}% Conversion Drop"
        
        # Build description (Jira markdown)
        description = self._build_description(issue)
        
        # Determine team assignment
        assignee = self._determine_assignee(issue)
        
        # Build labels
        labels = [
            "arguxai",
            "conversion",
            issue.severity.value,
            issue.anomaly.funnel_step.replace("_", "-")
        ]
        
        # Components based on funnel step
        components = self._determine_components(issue)
        
        return JiraIssueCreate(
            project_key=project_key or self.default_project_key,
            summary=summary,
            description=description,
            issue_type=JiraIssueType.BUG,
            priority=priority,
            assignee=assignee,
            labels=labels,
            components=components
        )
    
    def _build_description(self, issue: Issue) -> str:
        """Build Jira ticket description"""
        
        desc = f"""🤖 **AI-Detected Conversion Issue**

**Severity**: {issue.severity.value.upper()}
**Detected At**: {datetime.fromtimestamp(issue.created_at/1000).strftime('%Y-%m-%d %H:%M UTC')}

---

## 📊 Metrics

- **Funnel Step**: {issue.anomaly.funnel_step.replace('_', ' ').title()}
- **Current Conversion Rate**: {issue.anomaly.current_conversion_rate:.1f}%
- **Baseline Rate**: {issue.anomaly.baseline_conversion_rate:.1f}%
- **Drop**: {abs(issue.anomaly.drop_percentage):.1f} percentage points
- **Statistical Significance**: {issue.anomaly.sigma_value}σ (p < 0.05)
- **Affected Sessions**: {issue.anomaly.current_sessions}

---

## 🔍 AI Diagnosis
"""
        
        if issue.diagnosis:
            desc += f"""
**Root Cause**: {issue.diagnosis.root_cause}

**Confidence**: {issue.diagnosis.confidence:.0f}%

**Recommended Actions**:
"""
            for i, action in enumerate(issue.diagnosis.recommended_actions, 1):
                desc += f"{i}. {action}\n"
        
        # Add evidence
        if issue.evidence.error_types:
            desc += "\n---\n\n## 🐛 Top Errors\n\n"
            for error, count in list(issue.evidence.error_types.items())[:3]:
                desc += f"- `{error}`: {count} occurrences\n"
        
        # Add segment breakdown
        desc += "\n## 📱 Affected Segments\n\n"
        if issue.evidence.affected_countries:
            desc += f"- **Countries**: {', '.join(issue.evidence.affected_countries[:3])}\n"
        if issue.evidence.affected_devices:
            desc += f"- **Devices**: {', '.join(issue.evidence.affected_devices[:2])}\n"
        if issue.evidence.affected_versions:
            desc += f"- **Versions**: {', '.join(issue.evidence.affected_versions[:2])}\n"
        
        # Add links
        desc += f"""
---

## 🔗 Links

- **ArguxAI Issue ID**: `{issue.id}`
- **Status**: {issue.status.value}
"""
        
        if issue.fix_pr_url:
            desc += f"- **GitHub PR**: {issue.fix_pr_url}\n"
        
        desc += f"""
---

*This ticket was automatically created by ArguxAI - AI-powered conversion optimization*
"""
        
        return desc
    
    def _determine_assignee(self, issue: Issue) -> Optional[str]:
        """
        Determine which team/person to assign based on funnel step
        
        In a real implementation, this would map funnel steps to team members
        """
        
        # Map funnel steps to teams
        team_map = {
            "signup_form": "frontend-team@company.com",
            "otp_verification": "backend-team@company.com",
            "payment": "payments-team@company.com",
            "checkout": "frontend-team@company.com",
            "onboarding": "product-team@company.com"
        }
        
        # Get assignee from map
        assignee = team_map.get(issue.anomaly.funnel_step.lower())
        
        # For demo/testing, you can use your email
        # assignee = "your-email@company.com"
        
        return assignee
    
    def _determine_components(self, issue: Issue) -> list[str]:
        """Determine Jira components based on funnel step"""
        
        component_map = {
            "signup_form": ["Frontend", "Authentication"],
            "otp_verification": ["Backend", "SMS Service"],
            "payment": ["Payments", "Backend"],
            "checkout": ["Frontend", "Cart"],
            "onboarding": ["Frontend", "User Experience"]
        }
        
        return component_map.get(issue.anomaly.funnel_step.lower(), ["General"])
    
    def _generate_demo_ticket(self, issue: Issue) -> JiraIssue:
        """Generate demo Jira ticket"""
        
        return JiraIssue(
            key="CONV-123",
            id="10234",
            url=f"https://yourcompany.atlassian.net/browse/CONV-123",
            summary=f"{issue.anomaly.funnel_step} - {abs(issue.anomaly.drop_percentage):.1f}% Drop",
            status="To Do",
            assignee="Backend Team"
        )
    
    async def add_pr_comment(
        self,
        jira_key: str,
        pr_url: str
    ) -> None:
        """Add PR link as comment to Jira ticket"""
        try:
            comment = f"✅ **GitHub PR Created**\n\nAI-generated fix available: {pr_url}"
            await jira_client.add_comment(jira_key, comment)
            
            logger.info("PR comment added to Jira", jira_key=jira_key)
        except Exception as e:
            logger.error("Failed to add PR comment", error=str(e))
    
    async def mark_resolved(
        self,
        jira_key: str,
        uplift_percentage: float
    ) -> None:
        """Mark Jira ticket as resolved with uplift metrics"""
        try:
            # Add verification comment
            comment = f"""🎉 **Fix Verified - Conversion Improved!**

**Uplift**: +{uplift_percentage:.1f}%

The fix has been deployed and measured. Conversion rate has recovered to baseline.
"""
            await jira_client.add_comment(jira_key, comment)
            
            # Transition to Done
            await jira_client.transition_issue(jira_key, "Done")
            
            logger.info(
                "Jira ticket marked resolved",
                jira_key=jira_key,
                uplift=uplift_percentage
            )
        except Exception as e:
            logger.error("Failed to mark resolved", error=str(e))


# Global service instance
jira_ticket_service = JiraTicketService()
