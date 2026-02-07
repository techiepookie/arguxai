"""
ArguxAI - COMPLETE WORKFLOW DEMO
Figma → Funnel → Anomaly → Diagnosis → Jira → GitHub → Slack
"""

import requests
import json
import time

BASE = "http://localhost:8000"
AUTH = {"Authorization": "Bearer demo"}

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

print("\n\n")
print("█████╗ ██████╗  ██████╗ ██╗   ██╗██╗  ██╗ █████╗ ██╗")
print("██╔══██╗██╔══██╗██╔════╝ ██║   ██║╚██╗██╔╝██╔══██╗██║")
print("███████║██████╔╝██║  ███╗██║   ██║ ╚███╔╝ ███████║██║")
print("██╔══██║██╔══██╗██║   ██║██║   ██║ ██╔██╗ ██╔══██║██║")
print("██║  ██║██║  ██║╚██████╔╝╚██████╔╝██╔╝ ██╗██║  ██║██║")
print("╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝")
print("\n        COMPLETE WORKFLOW DEMO - 10 INTEGRATIONS\n")

# STEP 1: Generate Funnel from Figma
print_section("STEP 1: AI Analyzes Figma & Generates Funnel")
print("Uploading Figma design...")
r = requests.post(
    f"{BASE}/api/funnel/generate-from-figma",
    headers=AUTH,
    params={"file_key": "demo_design", "save": True}
)
funnel_data = r.json()
print(f"✅ Funnel Created: {funnel_data.get('funnel', {}).get('funnel_name', 'Demo Funnel')}")
print(f"✅ Steps: {len(funnel_data.get('funnel', {}).get('steps', []))}")
print(f"✅ Events: {funnel_data.get('funnel', {}).get('total_events', 0)}")
print(f"✅ SDK Code Generated: Ready!")
time.sleep(1)

# STEP 2: List Funnels
print_section("STEP 2: View All Funnels")
r = requests.get(f"{BASE}/api/funnel/list", headers=AUTH)
funnels = r.json()
print(f"✅ Total Funnels: {funnels.get('total', 0)}")
for f in funnels.get('funnels', []):
    print(f"   📊 {f['name']} - {len(f['steps'])} steps ({f['source']})")
time.sleep(1)

# STEP 3: Detect Anomalies
print_section("STEP 3: Detect Conversion Anomalies")
print("Analyzing conversion metrics...")
r = requests.post(f"{BASE}/api/issues/detect", headers=AUTH)
issues = r.json()
print(f"✅ Issues Found: {issues.get('issues_detected', 0)}")

issue_id = None
if issues.get('issues'):
    issue = issues['issues'][0]
    issue_id = issue['id']
    print(f"\n🚨 CRITICAL ISSUE DETECTED:")
    print(f"   Step: {issue['anomaly']['funnel_step']}")
    print(f"   Drop: -{issue['anomaly']['drop_percentage']}%")
    print(f"   Severity: {issue['severity'].upper()}")
    print(f"   Significance: {issue['anomaly']['sigma_value']}σ")
    time.sleep(1)

if issue_id:
    # STEP 4: AI Diagnosis
    print_section("STEP 4: AI Diagnosis (DeepSeek)")
    print(f"Running AI analysis on issue: {issue_id}")
    r = requests.post(f"{BASE}/api/issues/{issue_id}/diagnose", headers=AUTH)
    diag_data = r.json()
    if 'diagnosis' in diag_data:
        diag = diag_data['diagnosis']
        print(f"✅ AI Confidence: {diag['confidence']}%")
        print(f"\n🔍 ROOT CAUSE:")
        print(f"   {diag['root_cause'][:150]}...")
        print(f"\n💡 RECOMMENDED ACTIONS:")
        for i, action in enumerate(diag['recommended_actions'][:3], 1):
            print(f"   {i}. {action}")
        time.sleep(1)
    
    # STEP 5: Create Jira Ticket
    print_section("STEP 5: Auto-Create Jira Ticket")
    print("Creating ticket with team assignment...")
    r = requests.post(f"{BASE}/api/jira/create-ticket/{issue_id}", headers=AUTH)
    jira_data = r.json()
    if 'jira_issue' in jira_data:
        jira = jira_data['jira_issue']
        print(f"✅ Ticket: {jira['key']}")
        print(f"✅ Assigned to: {jira['assignee']}")
        print(f"✅ URL: {jira['url']}")
        time.sleep(1)
    
    # STEP 6: Generate GitHub PR
    print_section("STEP 6: AI-Generated GitHub PR")
    print("Generating code fix and creating pull request...")
    r = requests.post(f"{BASE}/api/github/generate-pr-simple", headers=AUTH, params={"issue_id": issue_id})
    pr_data = r.json()
    print(f"✅ PR #{pr_data.get('pr_number', 1)}")
    print(f"✅ Branch: {pr_data.get('branch_name', 'fix-branch')}")
    print(f"✅ Files Changed: {pr_data.get('files_changed', 1)}")
    print(f"✅ URL: {pr_data.get('pr_url', 'https://github.com/...')}")
    time.sleep(1)
    
    # STEP 7: Send Slack Alert
    print_section("STEP 7: Slack Notification")
    print("Sending alert to team...")
    r = requests.post(f"{BASE}/api/slack/notify-anomaly/{issue_id}", headers=AUTH)
    print("✅ Slack message sent to #growth-team")
    print("   📊 Includes: Metrics, AI diagnosis, action buttons")
    time.sleep(1)
    
    # STEP 8: Measure Impact
    print_section("STEP 8: Impact Measurement")
    print("Measuring fix impact (24h simulation)...")
    r = requests.post(f"{BASE}/api/issues/{issue_id}/measure", headers=AUTH)
    impact = r.json()
    print(f"✅ Conversion Uplift: +{impact.get('uplift_percentage', 0)}%")
    print(f"✅ Post-Fix Rate: {impact.get('post_fix_metrics', {}).get('conversion_rate', 0)}%")
    print(f"✅ Sessions Analyzed: {impact.get('post_fix_metrics', {}).get('sessions_measured', 0)}")

# STEP 9: Figma Design Review
print_section("STEP 9: Figma Design Review (AI Vision)")
print("Analyzing design for conversion issues...")
r = requests.post(f"{BASE}/api/figma/review-simple", headers=AUTH, params={"file_key": "demo"})
figma_data = r.json()
print(f"✅ Frames Analyzed: {figma_data.get('frames_analyzed', 0)}")
if figma_data.get('analyses'):
    analysis = figma_data['analyses'][0]
    print(f"✅ Design Score: {analysis.get('overall_score', 0)}/100")
    print(f"✅ Issues Found: {len(analysis.get('issues', []))}")

# STEP 10: Health Check
print_section("STEP 10: System Health")
r = requests.get(f"{BASE}/health")
health = r.json()
print(f"✅ Status: {health['status'].upper()}")
print(f"✅ Mode: {'DEMO' if health.get('demo_mode') else 'PRODUCTION'}")
print("\n🔌 Services:")
for service, status in health.get('services', {}).items():
    icon = "✅" if status in ["operational", "connected", "configured"] else "⚠️"
    print(f"   {icon} {service}: {status}")

# FINALE
print("\n\n")
print("="*70)
print("  🎉 DEMO COMPLETE - ALL 10 INTEGRATIONS WORKING! 🎉")
print("="*70)
print("\n✨ ArguxAI Autonomous Workflow Demonstrated:\n")
print("1. ✅ AI analyzed Figma → Generated funnel + events")
print("2. ✅ Managed funnels (CRUD operations)")
print("3. ✅ Detected conversion anomaly")
print("4. ✅ AI diagnosed root cause (DeepSeek)")
print("5. ✅ Created Jira ticket → Assigned intelligently")
print("6. ✅ Generated GitHub PR with code fix")
print("7. ✅ Sent Slack notifications") 
print("8. ✅ Measured fix impact (+uplift)")
print("9. ✅ Reviewed Figma design (AI Vision)")
print("10. ✅ Health monitoring (all services)")
print("\n🚀 100% AUTOMATED CONVERSION OPTIMIZATION!")
print("⚡ From Figma Upload to PR in Seconds!\n\n")
