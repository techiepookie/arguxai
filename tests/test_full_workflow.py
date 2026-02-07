"""
Test the complete ArguxAI workflow with the demo login app
"""

import asyncio
import httpx
import time

API_URL = "http://localhost:8000"
API_KEY = "demo"

async def test_complete_workflow():
    print("\n" + "="*70)
    print("🧪 TESTING COMPLETE ARGUXAI WORKFLOW")
    print("="*70 + "\n")
    
    client = httpx.AsyncClient(timeout=30.0)
    
    # Step 1: Simulate user events (as if users are using the demo app)
    print("STEP 1: Simulating user events from demo-login-app...")
    print("-" * 70)
    
    events = []
    
    # Simulate 100 users visiting login page
    for i in range(100):
        user_id = f"user_{i}"
        session_id = f"session_{int(time.time())}_{i}"
        
        # Page view
        events.append({
            "event_name": "login_page_viewed",
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": int(time.time() * 1000),
            "properties": {
                "funnel_step": "login_form",
                "device_type": "mobile" if i % 3 == 0 else "desktop"
            }
        })
        
        # Only 60% can click button (bug: button positioning)
        if i < 60:
            events.append({
                "event_name": "login_button_click",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": int(time.time() * 1000) + 2000,
                "properties": {
                    "funnel_step": "login_button_click"
                }
            })
            
            # Only 30% succeed (bug: API timeout)
            if i < 30:
                events.append({
                    "event_name": "conversion",
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": int(time.time() * 1000) + 5000,
                    "properties": {
                        "funnel_step": "login_complete",
                        "conversion_event": "login_success"
                    }
                })
            else:
                # Log error for failed login
                events.append({
                    "event_name": "error",
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": int(time.time() * 1000) + 5000,
                    "properties": {
                        "funnel_step": "login_error",
                        "error_message": "Login timed out. Please try again.",
                        "error_type": "TimeoutError"
                    }
                })
    
    # Send events to ArguxAI
    try:
        response = await client.post(
            f"{API_URL}/api/events/ingest",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"events": events}
        )
        
        if response.status_code == 200:
            print(f"✅ Sent {len(events)} events to ArguxAI")
            print(f"   - 100 page views")
            print(f"   - 60 button clicks (40% can't click due to positioning bug)")
            print(f"   - 30 successful logins")
            print(f"   - 30 timeout errors\n")
        else:
            print(f"❌ Failed to send events: {response.status_code}")
            print(f"   {response.text}\n")
            
    except Exception as e:
        print(f"❌ Error sending events: {e}\n")
    
    # Step 2: Trigger anomaly detection
    print("STEP 2: Triggering anomaly detection...")
    print("-" * 70)
    
    try:
        response = await client.post(
            f"{API_URL}/api/issues/detect",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            issues_count = data.get("issues_detected", 0)
            issues = data.get("issues", [])
            
            print(f"✅ Detection complete: {issues_count} issue(s) found\n")
            
            for issue in issues:
                print(f"🚨 ISSUE: {issue['id']}")
                print(f"   Step: {issue['anomaly']['funnel_step']}")
                print(f"   Drop: {issue['anomaly']['drop_percentage']}%")
                print(f"   Severity: {issue['severity']}\n")
                
                issue_id = issue['id']
                
                # Step 3: AI Diagnosis
                print("STEP 3: Running AI diagnosis...")
                print("-" * 70)
                
                diag_response = await client.post(
                    f"{API_URL}/api/issues/{issue_id}/diagnose",
                    headers={"Authorization": f"Bearer {API_KEY}"}
                )
                
                if diag_response.status_code == 200:
                    diagnosis = diag_response.json()
                    print(f"✅ AI Diagnosis complete")
                    print(f"   Root Cause: {diagnosis.get('diagnosis', {}).get('root_cause', 'N/A')[:100]}...")
                    print(f"   Confidence: {diagnosis.get('diagnosis', {}).get('confidence', 0)}%\n")
                
                # Step 4: Create Jira Ticket
                print("STEP 4: Creating Jira ticket...")
                print("-" * 70)
                
                jira_response = await client.post(
                    f"{API_URL}/api/jira/create-ticket/{issue_id}",
                    headers={"Authorization": f"Bearer {API_KEY}"}
                )
                
                if jira_response.status_code == 200:
                    jira_data = jira_response.json()
                    print(f"✅ Jira ticket created: {jira_data.get('jira_ticket', {}).get('key', 'N/A')}")
                    print(f"   URL: {jira_data.get('jira_ticket', {}).get('url', 'N/A')}\n")
                
                # Step 5: Generate GitHub PR
                print("STEP 5: Generating GitHub PR...")
                print("-" * 70)
                
                pr_response = await client.post(
                    f"{API_URL}/api/github/generate-pr-simple",
                    params={"issue_id": issue_id},
                    headers={"Authorization": f"Bearer {API_KEY}"}
                )
                
                if pr_response.status_code == 200:
                    pr_data = pr_response.json()
                    print(f"✅ GitHub PR created!")
                    print(f"   PR: {pr_data.get('pr_number', 'N/A')}")
                    print(f"   URL: {pr_data.get('pr_url', 'N/A')}\n")
                else:
                    print(f"❌ PR creation failed: {pr_response.status_code}")
                    print(f"   {pr_response.text[:200]}\n")
        else:
            print(f"❌ Detection failed: {response.status_code}")
            print(f"   {response.text}\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    print("="*70)
    print("🎉 WORKFLOW TEST COMPLETE!")
    print("="*70 + "\n")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
