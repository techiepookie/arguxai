"""Find what Jira projects exist and create a ticket in the right one"""

import httpx
import base64
import asyncio
import json

# Your actual credentials from .env
JIRA_DOMAIN = "arguxai.atlassian.net"
JIRA_EMAIL = "24227514010314@paruluniversity.ac.in"
JIRA_API_TOKEN = "ATATT3xFfGF0dwytlkELn_sINRfJAW6bf9FCFBV0rrAkVuQ53ng9e_zjvCma-9WnTlsZoX75lllXBdKr8IDxr5732VY5CfEXgcuNKNX1-NhvIp0Gybke4b3OJOrDmu9Kk_6CCfxL0jWfReDuCHWhghDUu0shgGoAlVCaHD893LKSYFKhplByxdE=C5F29376"

async def find_projects_and_create_ticket():
    print("\n" + "="*70)
    print("🔍 FINDING JIRA PROJECTS & CREATING TICKET")
    print("="*70 + "\n")
    
    # Create auth header
    auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    auth_bytes = auth_string.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    base_url = f"https://{JIRA_DOMAIN}/rest/api/3"
    
    client = httpx.AsyncClient(
        timeout=30.0,
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    try:
        # List all projects
        print("Step 1: Listing all Jira projects...")
        projects_response = await client.get(f"{base_url}/project")
        
        if projects_response.status_code == 200:
            projects = projects_response.json()
            print(f"\n✅ Found {len(projects)} project(s):\n")
            
            for proj in projects:
               print(f"   • {proj['key']} - {proj['name']}")
                
            if not projects:
                print("\n⚠️  No projects found! Create a project in Jira first.")
                return
            
            # Use the first project
            project_key = projects[0]['key']
            project_name = projects[0]['name']
            
            print(f"\n✅ Will create ticket in: {project_key} ({project_name})\n")
            
        else:
            print(f"❌ Failed to list projects: {projects_response.status_code}")
            return
        
        # Get issue types for this project
        print(f"Step 2: Getting issue types for {project_key}...")
        create_meta_response = await client.get(
            f"{base_url}/issue/createmeta",
            params={"projectKeys": project_key, "expand": "projects.issuetypes.fields"}
        )
        
        issue_type = "Task"  # Default
        if create_meta_response.status_code == 200:
            meta = create_meta_response.json()
            if meta.get("projects"):
                issue_types = meta["projects"][0].get("issuetypes", [])
                if issue_types:
                    issue_type = issue_types[0]["name"]
                    print(f"✅ Using issue type: {issue_type}\n")
        
        # Create the ticket
        print(f"Step 3: Creating ticket...")
        
        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": "🚨 ArguxAI Test: OTP Verification - 40.2% Conversion Drop",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "🤖 AI-Detected Conversion Issue\n\nSeverity: CRITICAL\n\n📊 Metrics:\n• Funnel Step: OTP Verification\n• Current Rate: 52%\n• Baseline Rate: 87%\n• Drop: 40.2%\n• Significance: 3.8σ\n\n🔍 AI Diagnosis:\nTwilio API rate limiting causing OTP delays.\n\n✨ Created by ArguxAI autonomous system"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": issue_type
                }
            }
        }
        
        create_response = await client.post(f"{base_url}/issue", json=payload)
        
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            issue_key = data.get("key")
            issue_url = f"https://{JIRA_DOMAIN}/browse/{issue_key}"
            
            print("\n" + "="*70)
            print("🎉 SUCCESS! REAL JIRA TICKET CREATED!")
            print("="*70 + "\n")
            
            print(f"🎫 Ticket: {issue_key}")
            print(f"📦 Project: {project_key} ({project_name})")
            print(f"🔗 URL: {issue_url}")
            print(f"\n✨ GO CHECK YOUR JIRA - REFRESH THE PAGE!")
            print(f"   {issue_url}\n")
            
        else:
            print(f"\n❌ Failed: {create_response.status_code}")
            print(f"{create_response.text}\n")
                
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(find_projects_and_create_ticket())
