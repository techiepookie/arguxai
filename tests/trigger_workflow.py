"""
Simple script to trigger the complete ArguxAI workflow
"""

import httpx
import asyncio

API_URL = "http://localhost:8000"

async def run_workflow():
    client = httpx.AsyncClient(timeout=60.0)
    
    print("\n" + "="*70)
    print("TRIGGERING ARGUXAI WORKFLOW")
    print("="*70 + "\n")
    
    # Step 1: Trigger anomaly detection
    print("STEP 1: Detecting anomalies from ingested events...")
    print("-" * 70)
    
    try:
        response = await client.post(
            f"{API_URL}/api/issues/detect",
            headers={"Authorization": "Bearer demo"}  # Added auth header
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Detection complete!")
            print(f"   Issues found: {data.get('issues_detected', 0)}\n")
            
            issues = data.get('issues', [])
            
            if not issues:
                print("WARNING: No anomalies detected yet.")
                print("   Tip: Generate more events by interacting with the demo app!\n")
                await client.aclose()
                return
            
            for issue in issues:
                issue_id = issue['id']
                anomaly = issue['anomaly']
                
                print(f"\nISSUE DETECTED: {issue_id}")
                print(f"   Funnel Step: {anomaly['funnel_step']}")
                print(f"   Drop: {anomaly['drop_percentage']}%")
                print(f"   Current: {anomaly['current_rate']}% | Baseline: {anomaly['baseline_rate']}%")
                print(f"   Severity: {issue['severity']}\n")
                
                # Step 2: AI Diagnosis
                print("STEP 2: Running AI diagnosis...")
                print("-" * 70)
                
                diag_resp = await client.post(f"{API_URL}/api/issues/{issue_id}/diagnose")
                
                if diag_resp.status_code == 200:
                    diagnosis = diag_resp.json()
                    root_cause = diagnosis.get('diagnosis', {}).get('root_cause', 'N/A')
                    confidence = diagnosis.get('diagnosis', {}).get('confidence', 0)
                    
                    print(f"SUCCESS: AI Diagnosis complete!")
                    print(f"   Root Cause: {root_cause[:150]}...")
                    print(f"   Confidence: {confidence}%\n")
                
                # Step 3: Create Jira ticket
                print("STEP 3: Creating Jira ticket in KAN project...")
                print("-" * 70)
                
                jira_resp = await client.post(f"{API_URL}/api/jira/create-ticket/{issue_id}")
                
                if jira_resp.status_code == 200:
                    jira_data = jira_resp.json()
                    jira_key = jira_data.get('jira_ticket', {}).get('key', 'N/A')
                    jira_url = jira_data.get('jira_ticket', {}).get('url', 'N/A')
                    
                    print(f"SUCCESS: Jira ticket created!")
                    print(f"   Ticket: {jira_key}")
                    print(f"   URL: {jira_url}\n")
                else:
                    print(f"ERROR: Jira ticket creation failed: {jira_resp.status_code}")
                    print(f"   {jira_resp.text[:200]}\n")
                
                # Step 4: Generate GitHub PR
                print("STEP 4: Generating GitHub PR with code fix...")
                print("-" * 70)
                
                pr_resp = await client.post(
                    f"{API_URL}/api/github/generate-pr-simple",
                    params={"issue_id": issue_id}
                )
                
                if pr_resp.status_code == 200:
                    pr_data = pr_resp.json()
                    pr_url = pr_data.get('pr_url', 'N/A')
                    pr_number = pr_data.get('pr_number', 'N/A')
                    
                    print(f"SUCCESS: GitHub PR created!")
                    print(f"   PR: #{pr_number}")
                    print(f"   URL: {pr_url}\n")
                else:
                    print(f"ERROR: PR creation failed: {pr_resp.status_code}")
                    print(f"   {pr_resp.text[:200]}\n")
        
        else:
            print(f"ERROR: Detection failed: {response.status_code}")
            print(f"   {response.text}\n")
    
    except Exception as e:
        print(f"ERROR: {e}\n")
    
    print("="*70)
    print("WORKFLOW COMPLETE!")
    print("="*70 + "\n")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(run_workflow())
