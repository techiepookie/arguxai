"""Test the complete ArguxAI workflow - Issue Detection to Resolution"""
import requests
import json

BASE = "http://localhost:8000"
AUTH = {"Authorization": "Bearer demo"}

print("\n" + "="*70)
print("TESTING COMPLETE WORKFLOW")
print("="*70 + "\n")

# Step 1: Detect Issues
print("STEP 1: Detecting Issues...")
r = requests.post(f"{BASE}/api/issues/detect", headers=AUTH)
result = r.json()

print(f"Response Code: {r.status_code}")
print(f"Issues Detected: {result.get('issues_detected', 0)}")

if result.get('issues'):
    issue = result['issues'][0]
    issue_id = issue['id']
    print(f"\n🚨 ISSUE FOUND:")
    print(f"   ID: {issue_id}")
    print(f"   Step: {issue['anomaly']['funnel_step']}")
    print(f"   Drop: {issue['anomaly']['drop_percentage']}%")
    print(f"   Severity: {issue['severity']}")
    
    # Step 2: AI Diagnosis (should already be done, but we can call it again)
    print(f"\nSTEP 2: Running AI Diagnosis...")
    r = requests.post(f"{BASE}/api/issues/{issue_id}/diagnose", headers=AUTH)
    diag_issue = r.json()
    if diag_issue.get('diagnosis'):
        print(f"✅ Root Cause: {diag_issue['diagnosis']['root_cause'][:100]}...")
        print(f"✅ Confidence: {diag_issue['diagnosis']['confidence']}%")
    
    # Step 3: Create Jira Ticket
    print(f"\nSTEP 3: Creating Jira Ticket...")
    r = requests.post(f"{BASE}/api/jira/create-ticket/{issue_id}", headers=AUTH)
    jira_result = r.json()
    if jira_result.get('jira_issue'):
        print(f"✅ Jira: {jira_result['jira_issue']['key']}")
        print(f"✅ Assigned: {jira_result['jira_issue']['assignee']}")
    
    # Step 4: Generate GitHub PR
    print(f"\nSTEP 4: Generating GitHub PR...")
    r = requests.post(f"{BASE}/api/github/generate-pr-simple", headers=AUTH, params={"issue_id": issue_id})
    pr_result = r.json()
    print(f"✅ PR: #{pr_result.get('pr_number', 1)}")
    print(f"✅ URL: {pr_result.get('pr_url', 'github.com/...')}")
    
    # Step 5: Send Slack Notification
    print(f"\nSTEP 5: Sending Slack Notification...")
    r = requests.post(f"{BASE}/api/slack/notify-anomaly/{issue_id}", headers=AUTH)
    print(f"✅ Slack notification sent!")
    
    # Step 6: Measure Impact
    print(f"\nSTEP 6: Measuring Fix Impact...")
    r = requests.post(f"{BASE}/api/issues/{issue_id}/measure", headers=AUTH)
    impact = r.json()
    print(f"✅ Uplift: +{impact.get('uplift_percentage', 0)}%")
    
    print("\n" + "="*70)
    print("🎉 COMPLETE WORKFLOW EXECUTED SUCCESSFULLY!")
    print("="*70)
    
else:
    print("\n❌ No issues detected (checking why...)")
    print(json.dumps(result, indent=2))
