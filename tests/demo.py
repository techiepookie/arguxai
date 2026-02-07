#!/usr/bin/env python3
"""
ArguxAI Live Demo - Complete End-to-End Workflow
Demonstrates: Detection → Diagnosis → Jira → GitHub PR → Slack → Measurement
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "dev_key_change_in_production"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ANSI color codes for terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.YELLOW}{text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_detail(text: str):
    print(f"  {text}")

def run_demo():
    """Run the complete ArguxAI workflow demo"""
    
    print_header("🎬 ArguxAI LIVE DEMO - Complete Workflow")
    print("=" * 50)
    
    try:
        # Step 1: Detect Anomaly
        print_info("\nStep 1: 🔍 Detecting Conversion Anomalies...")
        response = requests.post(f"{BASE_URL}/api/issues/detect", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Detected {data['issues_detected']} issue(s)")
        
        if data['issues_detected'] == 0:
            print_error("No issues detected. Make sure DEMO_MODE=true in .env")
            return
        
        issue = data['issues'][0]
        issue_id = issue['id']
        
        print(f"\n{Colors.MAGENTA}📊 Issue Details:{Colors.END}")
        print_detail(f"ID: {issue_id}")
        print_detail(f"Funnel: {issue['anomaly']['funnel_step']}")
        print_detail(f"Drop: {issue['anomaly']['drop_percentage']}%")
        print_detail(f"Severity: {issue['severity']}")
        
        time.sleep(1)
        
        # Step 2: AI Diagnosis
        print_info("\nStep 2: 🤖 Running AI Diagnosis...")
        response = requests.post(
            f"{BASE_URL}/api/issues/{issue_id}/diagnose",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()
        
        diagnosis = data['diagnosis']
        print_success(f"Diagnosis Complete (Confidence: {diagnosis['confidence']}%)")
        print_detail(f"Root Cause: {diagnosis['root_cause']}")
        
        time.sleep(1)
        
        # Step 3: Create Jira Ticket
        print_info("\nStep 3: 🎟️  Creating Jira Ticket...")
        response = requests.post(
            f"{BASE_URL}/api/jira/create-ticket/{issue_id}",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()
        
        jira_issue = data['jira_issue']
        jira_key = jira_issue['key']
        print_success(f"Jira Created: {jira_key}")
        print_detail(f"URL: {jira_issue['url']}")
        print_detail(f"Assignee: {jira_issue['assignee']}")
        
        time.sleep(1)
        
        # Step 4: Generate GitHub PR
        print_info("\nStep 4: 🔧 Generating GitHub PR with AI Code Fix...")
        response = requests.post(
            f"{BASE_URL}/api/github/generate-pr-simple",
            headers=HEADERS,
            params={"issue_id": issue_id}
        )
        response.raise_for_status()
        data = response.json()
        
        print_success(f"PR Generated: #{data['pr_number']}")
        print_detail(f"URL: {data['pr_url']}")
        print_detail(f"Files Changed: {data['files_changed']}")
        pr_url = data['pr_url']
        
        time.sleep(1)
        
        # Step 5: Link PR to Jira
        print_info("\nStep 5: 🔗 Linking PR to Jira...")
        response = requests.post(
            f"{BASE_URL}/api/jira/link-pr/{jira_key}",
            headers=HEADERS,
            params={"pr_url": pr_url}
        )
        response.raise_for_status()
        print_success("PR Linked to Jira")
        
        time.sleep(1)
        
        # Step 6: Send Slack Notification
        print_info("\nStep 6: 📢 Sending Slack Notification...")
        response = requests.post(
            f"{BASE_URL}/api/slack/notify-anomaly/{issue_id}",
            headers=HEADERS
        )
        response.raise_for_status()
        print_success("Slack Alert Sent")
        
        time.sleep(1)
        
        # Step 7: Measure Impact
        print_info("\nStep 7: 📊 Measuring Impact (simulated 24h later)...")
        response = requests.post(
            f"{BASE_URL}/api/issues/{issue_id}/measure",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()
        
        uplift = data['uplift_percentage']
        print_success(f"Impact Measured: +{uplift}% uplift")
        print_detail(f"Post-Fix Rate: {data['post_fix_metrics']['conversion_rate']}%")
        
        time.sleep(1)
        
        # Step 8: Mark Jira Resolved
        print_info("\nStep 8: ✅ Marking Jira as Resolved...")
        response = requests.post(
            f"{BASE_URL}/api/jira/resolve/{jira_key}",
            headers=HEADERS,
            params={"uplift_percentage": uplift}
        )
        response.raise_for_status()
        print_success("Jira Ticket Resolved")
        
        time.sleep(1)
        
        # Step 9: Success Notification
        print_info("\nStep 9: 🎉 Sending Success Notification...")
        response = requests.post(
            f"{BASE_URL}/api/slack/notify-verified/{issue_id}",
            headers=HEADERS
        )
        response.raise_for_status()
        print_success("Success Notification Sent")
        
        # Summary
        print(f"\n{Colors.CYAN}{'=' * 50}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}🎊 DEMO COMPLETE!{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        
        print(f"\n{Colors.MAGENTA}📈 WORKFLOW SUMMARY:{Colors.END}")
        print_detail(f"• Detected: {issue['anomaly']['funnel_step']} drop of {issue['anomaly']['drop_percentage']}%")
        print_detail(f"• Diagnosed: AI Root Cause ({diagnosis['confidence']}% confidence)")
        print_detail(f"• Created: Jira {jira_key} → {jira_issue['assignee']}")
        print_detail(f"• Generated: GitHub PR #{data['pr_number']}")
        print_detail(f"• Measured: +{uplift}% conversion uplift")
        print_detail(f"• Notified: 2 Slack messages sent")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}⚡ 9 STEPS - ALL AUTOMATED!{Colors.END}")
        print(f"{Colors.YELLOW}   Time: ~10 seconds (vs 3-5 days manual){Colors.END}\n")
        
    except requests.exceptions.ConnectionError:
        print_error("Connection failed! Make sure the server is running:")
        print("  python -m uvicorn app.main:app --reload")
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP Error: {e}")
        print(f"  Response: {e.response.text}")
    except Exception as e:
        print_error(f"Error: {str(e)}")


if __name__ == "__main__":
    run_demo()
