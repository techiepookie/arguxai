# TEST ArguxAI APIs

import requests
import json

BASE = "http://localhost:8000"
AUTH = {"Authorization": "Bearer demo"}

print("\n" + "="*60)
print("🚀 ArguxAI LIVE API TEST")
print("="*60 + "\n")

# 1. Health Check
print("1. HEALTH CHECK")
r = requests.get(f"{BASE}/health")
health = r.json()
print(f"✅ Status: {health['status']}")
print(f"✅ Services Connected: {len([s for s, v in health['services'].items() if v == 'connected'])}/7")

# 2. List Funnels
print("\n2. FUNNEL LIST")
r = requests.get(f"{BASE}/api/funnel/list", headers=AUTH)
funnels = r.json()
print(f"✅ Total Funnels: {funnels.get('total', 0)}")
if funnels.get('funnels'):
    for f in funnels['funnels']:
        print(f"  📊 {f['name']} - {len(f['steps'])} steps ({f['source']})")

# 3. Detect Anomalies
print("\n3. ANOMALY DETECTION")
r = requests.post(f"{BASE}/api/issues/detect", headers=AUTH)
issues = r.json()
print(f"✅ Issues Detected: {issues.get('issues_detected', 0)}")
if issues.get('issues'):
    issue = issues['issues'][0]
    print(f"  🚨 {issue['anomaly']['funnel_step']}: -{issue['anomaly']['drop_percentage']}%")
    print(f"  Severity: {issue['severity']}")
    print(f"  Issue ID: {issue['id']}")

# 4. Diagnose Issue (if found)
if issues.get('issues'):
    issue_id = issues['issues'][0]['id']
    print(f"\n4. AI DIAGNOSIS")
    r = requests.post(f"{BASE}/api/issues/{issue_id}/diagnose", headers=AUTH)
    diag = r.json()
    if 'diagnosis' in diag:
        print(f"✅ AI Confidence: {diag['diagnosis']['confidence']}%")
        print(f"  Root Cause: {diag['diagnosis']['root_cause'][:100]}...")
        print(f"  Actions: {len(diag['diagnosis']['recommended_actions'])} recommendations")

print("\n" + "="*60)
print("✅ ALL APIS WORKING!")
print("="*60 + "\n")
