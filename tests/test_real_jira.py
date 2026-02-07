"""Test REAL Jira ticket creation"""
import asyncio
from app.config import settings
from app.models.issues import Anomaly, DiagnosisEvidence, Issue, IssueStatus, IssueSeverity
from app.services.jira_ticket_service import jira_ticket_service
import time

async def test_real_jira():
    print("\n" + "="*70)
    print("TESTING REAL JIRA TICKET CREATION")
    print("="*70 + "\n")
    
    print(f"✅ DEMO_MODE: {settings.demo_mode}")
    print(f"✅ JIRA_DOMAIN: {settings.jira_domain}")
    print(f"✅ JIRA_PROJECT_KEY: {settings.jira_project_key}")
    print(f"✅ JIRA_API_TOKEN: {'Configured (' + settings.jira_api_token[:20] + '...)' if settings.jira_api_token else 'NOT SET'}")
    
    # Create a demo issue
    current_time = int(time.time() * 1000)
    
    anomaly = Anomaly(
        funnel_step="otp_verification",
        detected_at=current_time,
        current_conversion_rate=52.0,
        baseline_conversion_rate=87.0,
        drop_percentage=40.2,
        sigma_value=3.8,
        is_significant=True,
        current_sessions=450,
        baseline_sessions=1200
    )
    
    issue = Issue(
        id=f"issue_{current_time}_test",
        status=IssueStatus.DETECTED,
        severity=IssueSeverity.CRITICAL,
        anomaly=anomaly,
        evidence=DiagnosisEvidence(),
        created_at=current_time
    )
    
    print(f"\n📝 Creating Jira ticket for: {issue.id}")
    print(f"   Funnel Step: {anomaly.funnel_step}")
    print(f"   Drop: {anomaly.drop_percentage}%")
    print(f"   Severity: {issue.severity.value}\n")
    
    try:
        # This should create a REAL Jira ticket!
        jira_ticket = await jira_ticket_service.create_ticket_for_issue(issue)
        
        print("\n" + "="*70)
        print("🎉 SUCCESS! REAL JIRA TICKET CREATED!")
        print("="*70 + "\n")
        
        print(f"🎫 Ticket Key: {jira_ticket.key}")
        print(f"📊 Summary: {jira_ticket.summary}")
        print(f"👤 Assigned To: {jira_ticket.assignee}")
        print(f"🔗 URL: {jira_ticket.url}")
        print(f"📍 Status: {jira_ticket.status}")
        
        print("\n✨ Go check your Jira board! The ticket should be there!")
        print(f"   Direct link: {jira_ticket.url}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        print("Possible issues:")
        print("  1. Jira API token may be invalid")
        print("  2. Project key 'CONV' might not exist in your Jira")
        print("  3. Network/permission issues")
        raise

if __name__ == "__main__":
    asyncio.run(test_real_jira())
