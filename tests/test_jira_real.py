#!/usr/bin/env python3
"""Test real Jira integration"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.jira_client import jira_client
from app.models.jira import JiraIssueCreate, JiraIssueType, JiraPriority
from app.core.logging import logger


async def test_jira():
    """Test Jira API"""
    
    print("\n" + "="*60)
    print("Testing Jira Integration")
    print("="*60 + "\n")
    
    # Test 1: Health check
    print("1. Testing Jira API connection...")
    is_healthy = await jira_client.health_check()
    
    if is_healthy:
        print("   ✅ Jira API is accessible\n")
    else:
        print("   ❌ Jira API is not accessible")
        print("   Check your JIRA_DOMAIN, JIRA_EMAIL, and JIRA_API_TOKEN in .env\n")
        return False
    
    # Test 2: Create a simple issue
    print("2. Creating test Jira issue...")
    
    try:
        issue_data = JiraIssueCreate(
            project_key="KAN",
            summary="Test Issue from ArguxAI",
            description="This is a test issue created by ArguxAI to verify the integration is working.",
            issue_type=JiraIssueType.BUG,
            priority=JiraPriority.MEDIUM,
            labels=["arguxai", "test"]
        )
        
        jira_issue = await jira_client.create_issue(issue_data)
        
        print(f"   ✅ Issue created successfully!")
        print(f"   Key: {jira_issue.key}")
        print(f"   URL: {jira_issue.url}\n")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create issue")
        print(f"   Error: {str(e)}\n")
        
        # Common issues
        print("Common issues:")
        print("  - Project key 'KAN' doesn't exist in your Jira")
        print("  - API token doesn't have permission to create issues")
        print("  - Email address doesn't match the token owner")
        print("  - Issue type 'Bug' doesn't exist in the project")
        
        return False


if __name__ == "__main__":
    success = asyncio.run(test_jira())
    sys.exit(0 if success else 1)
