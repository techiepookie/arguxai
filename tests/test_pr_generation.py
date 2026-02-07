#!/usr/bin/env python3
"""Test PR generation with real GitHub access"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pr_generator import pr_generator
from app.services.issue_manager import issue_manager
from app.models.issues import IssueSeverity, Anomaly, DiagnosisEvidence, AIDiagnosis
from datetime import datetime


async def test_pr_generation():
    """Test PR generation end-to-end"""
    
    print("\n" + "="*60)
    print("Testing PR Generation")
    print("="*60 + "\n")
    
    # Create a test issue with diagnosis
    issue_id = f"test_issue_{int(datetime.utcnow().timestamp())}"
    
    anomaly = Anomaly(
        funnel_step="login_button_click",
        detected_at=int(datetime.utcnow().timestamp() * 1000),
        baseline_conversion_rate=85.0,
        current_conversion_rate=45.0,
        drop_percentage=47.1,
        sigma_value=5.2,
        is_significant=True,
        baseline_sessions=1000,
        current_sessions=500
    )
    
    evidence = DiagnosisEvidence(
        error_types={"TypeError": 15, "NetworkError": 8},
        affected_countries=["US", "UK"],
        affected_devices=["mobile"],
        affected_versions=["1.0.0"],
        struggling_session_ids=["sess1", "sess2"]
    )
    
    diagnosis = AIDiagnosis(
        root_cause="Login button click handler is broken",
        confidence=95,
        explanation="The login button click event is not properly attached, causing users to be unable to submit the login form.",
        recommended_actions=[
            "Fix the event listener attachment in login.js",
            "Add error handling for form submission",
            "Test on mobile devices"
        ],
        evidence=evidence,
        model_used="deepseek-chat",
        diagnosis_time_ms=1500
    )
    
    # Create issue
    issue = issue_manager.create_issue(
        anomaly=anomaly,
        severity=IssueSeverity.CRITICAL
    )
    
    # Add diagnosis
    issue.diagnosis = diagnosis
    issue_manager.issues[issue.id] = issue
    
    print(f"Created test issue: {issue.id}")
    print(f"Severity: {issue.severity.value}")
    print(f"Root cause: {diagnosis.root_cause}\n")
    
    # Generate PR
    print("Generating PR...")
    response = await pr_generator.generate_pr(
        issue_id=issue.id,
        repository="techiepookie/demo-login-app",
        target_files=["demo-login-app/login.js"],
        base_branch="main"
    )
    
    print("\n" + "="*60)
    print("PR Generation Result")
    print("="*60 + "\n")
    
    if response.success:
        print(f"✅ Success!")
        print(f"PR URL: {response.pr_url}")
        print(f"PR Number: {response.pr_number}")
        print(f"Branch: {response.branch_name}")
        print(f"Commit SHA: {response.commit_sha}")
        print(f"Files Changed: {response.files_changed}")
        print(f"Message: {response.message}\n")
        return True
    else:
        print(f"❌ Failed!")
        print(f"Message: {response.message}\n")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_pr_generation())
    sys.exit(0 if success else 1)
