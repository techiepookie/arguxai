"""Issue management service orchestrating the diagnosis workflow"""

from typing import List, Optional
from datetime import datetime
import uuid
from app.models.issues import (
    Issue, IssueStatus, IssueSeverity, Anomaly, DiagnosisEvidence, AIDiagnosis, IssueCreateRequest
)
from app.integrations.deepseek_client import deepseek_client
from app.services.evidence_collector import evidence_collector
from app.integrations.convex_client import convex_client
from app.core.logging import logger


class IssueManager:
    """
    Manage conversion issues through their lifecycle
    
    Workflow:
    1. Anomaly detected → Create issue
    2. Collect evidence → Update issue
    3. AI diagnosis → Update issue with diagnosis
    4. Engineer marks fixed → Schedule measurement
    5. Measure uplift → Close issue
    """
    
    def __init__(self):
        # In-memory storage (for demo)
        # In production, use Convex
        self.issues: dict[str, Issue] = {}
        self._load_issues_from_db()
    
    def _load_issues_from_db(self):
        """Load existing issues from database on startup"""
        try:
            import sqlite3
            import json
            
            conn = sqlite3.connect("arguxai.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT issue_id, funnel_step, severity, status, detected_at, current_conversion_rate, baseline_conversion_rate, drop_percentage, sigma_value, diagnosis, github_pr, jira_ticket, is_significant, current_sessions, baseline_sessions, updated_at FROM issues")
            rows = cursor.fetchall()
            
            for row in rows:
                issue_id, funnel_step, severity, status, detected_at, current_rate, baseline_rate, drop_pct, sigma, diagnosis_str, pr_url, jira_key, is_significant, current_sessions, baseline_sessions, updated_at = row
                
                # Reconstruct anomaly
                anomaly = Anomaly(
                    funnel_step=funnel_step,
                    detected_at=detected_at,
                    current_conversion_rate=current_rate,
                    baseline_conversion_rate=baseline_rate,
                    drop_percentage=drop_pct,
                    sigma_value=sigma,
                    is_significant=bool(is_significant),
                    current_sessions=current_sessions,
                    baseline_sessions=baseline_sessions
                )
                
                # Reconstruct diagnosis if exists
                diagnosis = None
                if diagnosis_str:
                    diagnosis = AIDiagnosis(
                        root_cause=diagnosis_str,
                        confidence=85.0,
                        explanation="Loaded from database",
                        recommended_actions=["Review and fix"],
                        code_locations=[],
                        model_used="deepseek-chat",
                        diagnosis_time_ms=0
                    )
                
                # Create issue object
                issue = Issue(
                    id=issue_id,
                    status=IssueStatus(status),
                    severity=IssueSeverity(severity),
                    anomaly=anomaly,
                    evidence=DiagnosisEvidence(),  # Empty evidence
                    diagnosis=diagnosis,
                    fix_pr_url=pr_url,
                    jira_ticket_key=jira_key,
                    created_at=detected_at,
                    updated_at=updated_at
                )
                
                self.issues[issue_id] = issue
                
            conn.close()
            logger.info(f"Loaded {len(rows)} issues from database")
        except Exception as e:
            logger.warning(f"Could not load issues from database: {e}")
    
    def _save_issue_to_db(self, issue: Issue):
        """Save issue to database"""
        try:
            import sqlite3
            
            conn = sqlite3.connect("arguxai.db")
            cursor = conn.cursor()
            
            # Convert diagnosis to string if exists
            diagnosis_str = issue.diagnosis.root_cause if issue.diagnosis else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO issues 
                (issue_id, funnel_step, severity, status, detected_at,
                 current_conversion_rate, baseline_conversion_rate,
                 drop_percentage, sigma_value, diagnosis,
                 github_pr, jira_ticket, is_significant, current_sessions,
                 baseline_sessions, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue.id,
                issue.anomaly.funnel_step,
                issue.severity.value,
                issue.status.value,
                issue.anomaly.detected_at,
                issue.anomaly.current_conversion_rate,
                issue.anomaly.baseline_conversion_rate,
                issue.anomaly.drop_percentage,
                issue.anomaly.sigma_value,
                diagnosis_str,
                issue.fix_pr_url,
                issue.jira_ticket_key,
                1 if issue.anomaly.is_significant else 0,
                issue.anomaly.current_sessions,
                issue.anomaly.baseline_sessions,
                issue.updated_at
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save issue to database: {e}")
    
    def _generate_issue_id(self, anomaly: Anomaly) -> str:
        """Generate unique issue ID"""
        timestamp = anomaly.detected_at
        step = anomaly.funnel_step.replace("_", "")
        return f"issue_{timestamp}_{step}"
    
    def _calculate_severity(self, drop_percentage: float) -> IssueSeverity:
        """Calculate issue severity based on drop percentage"""
        if drop_percentage >= 20:
            return IssueSeverity.CRITICAL
        elif drop_percentage >= 15:
            return IssueSeverity.HIGH
        elif drop_percentage >= 12:
            return IssueSeverity.MEDIUM
        else:
            return IssueSeverity.LOW
    
    async def create_issue(
        self,
        anomaly: Anomaly,
        auto_diagnose: bool = True
    ) -> Issue:
        """
        Create a new issue from detected anomaly
        
        Args:
            anomaly: Detected anomaly
            auto_diagnose: Whether to immediately request AI diagnosis
            
        Returns:
            Created issue
        """
        try:
            # Generate issue ID
            issue_id = self._generate_issue_id(anomaly)
            
            # Check if issue already exists
            if issue_id in self.issues:
                logger.warning("Issue already exists", issue_id=issue_id)
                return self.issues[issue_id]
            
            # Calculate severity
            severity = self._calculate_severity(anomaly.drop_percentage)
            
            # Collect evidence
            logger.info("Collecting evidence for issue", issue_id=issue_id, funnel_step=anomaly.funnel_step)
            
            # Use the anomaly time as reference
            end_time = anomaly.detected_at
            start_time = end_time - (60 * 60 * 1000)  # 1 hour before
            
            evidence = await evidence_collector.collect_evidence(
                funnel_step=anomaly.funnel_step,
                start_time=start_time,
                end_time=end_time
            )
            
            # Create issue
            issue = Issue(
                id=issue_id,
                status=IssueStatus.DETECTED,
                severity=severity,
                anomaly=anomaly,
                evidence=evidence,
                created_at=anomaly.detected_at
            )
            
            # Store issue
            self.issues[issue_id] = issue
            self._save_issue_to_db(issue)
            
            logger.info(
                "Issue created",
                issue_id=issue_id,
                severity=severity,
                funnel_step=anomaly.funnel_step,
                drop_percentage=anomaly.drop_percentage
            )
            
            # Auto-diagnose if requested
            if auto_diagnose:
                await self.diagnose_issue(issue_id)
            
            return issue
            
        except Exception as e:
            logger.error("Failed to create issue", error=str(e))
            raise
    
    async def diagnose_issue(self, issue_id: str) -> Issue:
        """
        Run AI diagnosis on an issue
        
        Args:
            issue_id: ID of issue to diagnose
            
        Returns:
            Updated issue with diagnosis
        """
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise ValueError(f"Issue {issue_id} not found")
            
            logger.info("Running AI diagnosis", issue_id=issue_id)
            
            # Call DeepSeek for diagnosis
            diagnosis_dict = await deepseek_client.diagnose_conversion_drop(
                funnel_step=issue.anomaly.funnel_step,
                drop_percentage=issue.anomaly.drop_percentage,
                current_rate=issue.anomaly.current_conversion_rate,
                baseline_rate=issue.anomaly.baseline_conversion_rate,
                evidence=issue.evidence.model_dump()
            )
            
            # Create diagnosis object
            diagnosis = AIDiagnosis(**diagnosis_dict)
            
            # Update issue
            issue.diagnosis = diagnosis
            issue.status = IssueStatus.DIAGNOSED
            issue.diagnosed_at = int(datetime.utcnow().timestamp() * 1000)
            self._save_issue_to_db(issue)
            
            logger.info(
                "Issue diagnosed",
                issue_id=issue_id,
                root_cause=diagnosis.root_cause,
                confidence=diagnosis.confidence
            )
            
            return issue
            
        except Exception as e:
            logger.error("Failed to diagnose issue", error=str(e), issue_id=issue_id)
            raise
    
    async def mark_jira_created(
        self,
        issue_id: str,
        jira_ticket_key: str
    ) -> Issue:
        """
        Mark Jira ticket as created for issue
        
        Args:
            issue_id: Issue ID
            jira_ticket_key: Jira ticket key (e.g. CONV-123)
            
        Returns:
            Updated issue
        """
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise ValueError(f"Issue {issue_id} not found")
            
            issue.jira_ticket_key = jira_ticket_key
            issue.updated_at = int(datetime.utcnow().timestamp() * 1000)
            self._save_issue_to_db(issue)
            
            logger.info(
                "Jira ticket linked to issue",
                issue_id=issue_id,
                jira_key=jira_ticket_key
            )
            
            return issue
            
        except Exception as e:
            logger.error("Failed to link Jira ticket", error=str(e), issue_id=issue_id)
            raise
    
    async def mark_fixed(
        self,
        issue_id: str,
        commit_sha: Optional[str] = None,
        pr_url: Optional[str] = None
    ) -> Issue:
        """
        Mark issue as fixed by engineer
        
        Args:
            issue_id: Issue ID
            commit_sha: Git commit SHA of fix
            pr_url: Pull request URL
            
        Returns:
            Updated issue
        """
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise ValueError(f"Issue {issue_id} not found")
            
            issue.status = IssueStatus.FIXED
            issue.fixed_at = int(datetime.utcnow().timestamp() * 1000)
            issue.fix_commit_sha = commit_sha
            issue.fix_pr_url = pr_url
            issue.updated_at = int(datetime.utcnow().timestamp() * 1000)
            self._save_issue_to_db(issue)
            
            logger.info(
                "Issue marked as fixed",
                issue_id=issue_id,
                pr_url=pr_url,
                commit_sha=commit_sha
            )
            
            return issue
            
        except Exception as e:
            logger.error("Failed to mark issue as fixed", error=str(e), issue_id=issue_id)
            raise
    
    async def measure_impact(self, issue_id: str) -> Issue:
        """
        Measure impact of fix (should be called 24h after fix)
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Updated issue with measurement results
        """
        try:
            issue = self.issues.get(issue_id)
            if not issue:
                raise ValueError(f"Issue {issue_id} not found")
            
            # In demo mode, generate mock uplift
            from random import uniform
            post_fix_rate = issue.anomaly.baseline_conversion_rate + uniform(2, 8)
            uplift = ((post_fix_rate - issue.anomaly.current_conversion_rate) / 
                     issue.anomaly.current_conversion_rate * 100)
            
            issue.post_fix_conversion_rate = round(post_fix_rate, 2)
            issue.uplift_percentage = round(uplift, 2)
            issue.measured_at = int(datetime.utcnow().timestamp() * 1000)
            issue.status = IssueStatus.VERIFIED
            
            logger.info(
                "Impact measured",
                issue_id=issue_id,
                uplift_percentage=uplift,
                post_fix_rate=post_fix_rate
            )
            
            return issue
            
        except Exception as e:
            logger.error("Failed to measure impact", error=str(e), issue_id=issue_id)
            raise
    
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue by ID"""
        return self.issues.get(issue_id)
    
    def list_issues(
        self,
        status: Optional[IssueStatus] = None,
        severity: Optional[IssueSeverity] = None
    ) -> List[Issue]:
        """
        List all issues with optional filters
        
        Args:
            status: Filter by status
            severity: Filter by severity
            
        Returns:
            List of issues
        """
        issues = list(self.issues.values())
        
        if status:
            issues = [i for i in issues if i.status == status]
        
        if severity:
            issues = [i for i in issues if i.severity == severity]
        
        # Sort by creation time (newest first)
        issues.sort(key=lambda i: i.created_at, reverse=True)
        
        return issues


# Global issue manager instance
issue_manager = IssueManager()
