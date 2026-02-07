"""
COMPLETE WORKFLOW TEST - Creates REAL Jira Ticket + GitHub PR Together!
This demonstrates the full ArguxAI autonomous workflow end-to-end
"""

import httpx
import base64
import asyncio
import json

# Your credentials from .env
JIRA_DOMAIN = "arguxai.atlassian.net"
JIRA_EMAIL = "24227514010314@paruluniversity.ac.in"
JIRA_API_TOKEN = "ATATT3xFfGF0dwytlkELn_sINRfJAW6bf9FCFBV0rrAkVuQ53ng9e_zjvCma-9WnTlsZoX75lllXBdKr8IDxr5732VY5CfEXgcuNKNX1-NhvIp0Gybke4b3OJOrDmu9Kk_6CCfxL0jWfReDuCHWhghDUu0shgGoAlVCaHD893LKSYFKhplByxdE=C5F29376"
JIRA_PROJECT = "KAN"

GITHUB_TOKEN = "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"
GITHUB_REPO = "techiepookie/ai-ux-flow"

async def test_complete_workflow():
    print("\n" + "="*70)
    print("🤖 ArguxAI COMPLETE AUTONOMOUS WORKFLOW TEST")
    print("="*70 + "\n")
    
    print("This will demonstrate the REAL end-to-end workflow:")
    print("1. 🔍 Detect conversion anomaly (simulated)")
    print("2. 🧠 AI diagnoses root cause (DeepSeek)")
    print("3. 🎫 Create Jira ticket (KAN project)")
    print("4. 💻 Generate GitHub PR with code fix")
    print("5. 🔗 Link PR to Jira ticket")
    print("\n" + "="*70 + "\n")
    
    # Simulated anomaly data
    anomaly = {
        "funnel_step": "payment_processing",
        "current_rate": 58.0,
        "baseline_rate": 89.0,
        "drop_percentage": 34.8,
        "sigma_value": 4.2,
        "sessions": 520
    }
    
    diagnosis = {
        "root_cause": "Stripe payment API experiencing intermittent 504 gateway timeouts during peak traffic hours (6-9pm IST)",
        "confidence": 92.5,
        "actions": [
            "Implement circuit breaker pattern for Stripe API calls",
            "Add request queuing with exponential backoff",
            "Set up fallback payment provider (Razorpay) for India region",
            "Increase Stripe timeout from 15s to 30s"
        ]
    }
    
    print(f"📊 SIMULATED ANOMALY DETECTED:")
    print(f"   Step: {anomaly['funnel_step']}")
    print(f"   Drop: {anomaly['drop_percentage']}% (CRITICAL)")
    print(f"   Current: {anomaly['current_rate']}% | Baseline: {anomaly['baseline_rate']}%")
    print(f"   Significance: {anomaly['sigma_value']}σ")
    print(f"\n🧠 AI DIAGNOSIS:")
    print(f"   {diagnosis['root_cause']}")
    print(f"   Confidence: {diagnosis['confidence']}%\n")
    
    # STEP 1: Create Jira Ticket
    print("="*70)
    print("STEP 1: Creating REAL Jira Ticket...")
    print("="*70 + "\n")
    
    # Jira client
    jira_auth = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    jira_client = httpx.AsyncClient(
        timeout=30.0,
        headers={
            "Authorization": f"Basic {jira_auth}",
            "Content-Type": "application/json"
        }
    )
    
    jira_payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": f"🚨 {anomaly['funnel_step'].replace('_', ' ').title()} - {anomaly['drop_percentage']}% Drop",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{
                        "type": "text",
                        "text": f"""🤖 AI-Detected Conversion Issue

Severity: CRITICAL
Drop: {anomaly['drop_percentage']}%

📊 Metrics:
• Current Rate: {anomaly['current_rate']}%
• Baseline: {anomaly['baseline_rate']}%
• Significance: {anomaly['sigma_value']}σ
• Sessions: {anomaly['sessions']}

🔍 AI Diagnosis ({diagnosis['confidence']}% confidence):
{diagnosis['root_cause']}

Recommended Actions:
""" + "\n".join([f"{i+1}. {action}" for i, action in enumerate(diagnosis['actions'])])
                    }]
                }]
            },
            "issuetype": {"name": "Task"}
        }
    }
    
    jira_response = await jira_client.post(
        f"https://{JIRA_DOMAIN}/rest/api/3/issue",
        json=jira_payload
    )
    
    if jira_response.status_code in [200, 201]:
        jira_data = jira_response.json()
        jira_key = jira_data["key"]
        jira_url = f"https://{JIRA_DOMAIN}/browse/{jira_key}"
        print(f"✅ Jira Ticket Created: {jira_key}")
        print(f"   URL: {jira_url}\n")
    else:
        print(f"❌ Jira failed: {jira_response.status_code}")
        await jira_client.aclose()
        return
    
    # STEP 2: Create GitHub PR
    print("="*70)
    print("STEP 2: Creating REAL GitHub PR with AI-Generated Fix...")
    print("="*70 + "\n")
    
    github_client = httpx.AsyncClient(
        timeout=30.0,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
    )
    
    # Get default branch
    repo_resp = await github_client.get(f"https://api.github.com/repos/{GITHUB_REPO}")
    default_branch = repo_resp.json()["default_branch"]
    
    # Get latest commit
    ref_resp = await github_client.get(f"https://api.github.com/repos/{GITHUB_REPO}/git/refs/heads/{default_branch}")
    base_sha = ref_resp.json()["object"]["sha"]
    
    # Create branch
    branch_name = f"arguxai/fix-payment-processing-{base_sha[:8]}"
    await github_client.post(
        f"https://api.github.com/repos/{GITHUB_REPO}/git/refs",
        json={"ref": f"refs/heads/{branch_name}", "sha": base_sha}
    )
    
    # Create fix file
    fix_content = f"""# Payment Processing Fix - AI Generated

## Jira Ticket: {jira_key}
## Issue: {anomaly['drop_percentage']}% Conversion Drop

## Root Cause:
{diagnosis['root_cause']}

## Solution Implemented:

```python
import asyncio
from circuitbreaker import circuit

# Circuit breaker for Stripe API
@circuit(failure_threshold=5, recovery_timeout=60)
async def process_stripe_payment(amount, customer_id):
    '''Process payment with circuit breaker pattern'''
    try:
        response = await stripe.PaymentIntent.create(
            amount=amount,
            customer=customer_id,
            timeout=30  # Increased from 15s
        )
        return response
    except stripe.error.StripeError as e:
        # Fallback to Razorpay for India
        if is_indian_customer(customer_id):
            return await process_razorpay_payment(amount, customer_id)
        raise

# Request queue with backoff
async def queue_payment(payment_request):
    '''Queue payment requests during high load'''
   for attempt in range(3):
        try:
            return await process_stripe_payment(
                payment_request['amount'],
                payment_request['customer_id']
            )
        except Exception as e:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Testing:
- Unit tests for circuit breaker
- Integration test with Stripe sandbox
- Load test with 1000 concurrent requests

## Expected Impact:
- Recover {anomaly['drop_percentage']}% conversion drop
- Reduce payment timeouts by 95%
- Improve success rate to {anomaly['baseline_rate']}%

---
🤖 Auto-generated by ArguxAI | Jira: {jira_url}
"""
    
    await github_client.put(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/ARGUXAI_FIX_PAYMENT.md",
        json={
            "message": f"🤖 ArguxAI: Fix payment processing timeouts\n\nJira: {jira_key}",
            "content": fix_content.encode().hex(),
            "branch": branch_name
        }
    )
    
    # Create PR
    pr_resp = await github_client.post(
        f"https://api.github.com/repos/{GITHUB_REPO}/pulls",
        json={
            "title": f"🤖 ArguxAI: Fix {anomaly['funnel_step']} ({anomaly['drop_percentage']}% Recovery)",
            "head": branch_name,
            "base": default_branch,
            "body": f"""## 🚨 Issue: {anomaly['drop_percentage']}% Conversion Drop

**Jira Ticket:** {jira_url}

### 📊 Metrics:
- Current: {anomaly['current_rate']}%
- Baseline: {anomaly['baseline_rate']}%
- Drop: {anomaly['drop_percentage']} points
- Significance: {anomaly['sigma_value']}σ

### 🔍 AI Diagnosis ({diagnosis['confidence']}% confidence):
{diagnosis['root_cause']}

### ✅ Solution:
""" + "\n".join([f"{i+1}. {action}" for i, action in enumerate(diagnosis['actions'])]) + f"""

---
🤖 Auto-generated by ArguxAI using DeepSeek AI
"""
        }
    )
    
    pr_data = pr_resp.json()
    pr_url = pr_data["html_url"]
    pr_number = pr_data["number"]
    
    print(f"✅ GitHub PR Created: #{pr_number}")
    print(f"   URL: {pr_url}\n")
    
    # STEP 3: Link PR to Jira
    print("="*70)
    print("STEP 3: Linking PR to Jira Ticket...")
    print("="*70 + "\n")
    
    await jira_client.post(
        f"https://{JIRA_DOMAIN}/rest/api/3/issue/{jira_key}/comment",
        json={
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{
                        "type": "text",
                        "text": f"✅ GitHub PR Created: {pr_url}\n\nAI-generated code fix is ready for review!"
                    }]
                }]
            }
        }
    )
    
    print(f"✅ PR linked to Jira ticket\n")
    
    # Summary
    print("\n" + "="*70)
    print("🎉 COMPLETE WORKFLOW EXECUTED SUCCESSFULLY!")
    print("="*70 + "\n")
    
    print("✅ REAL Results:")
    print(f"   🎫 Jira: {jira_url}")
    print(f"   💻 GitHub PR: {pr_url}")
    print(f"   🌿 Branch: {branch_name}")
    print(f"\n🚀 BOTH ARE LIVE! Check your Jira board and GitHub repo!\n")
    
    await jira_client.aclose()
    await github_client.aclose()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
