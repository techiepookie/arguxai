import requests
import json

BASE = "http://localhost:8000"
AUTH = {"Authorization": "Bearer demo"}

print("\n" + "="*60)
print("ArguxAI LIVE API TEST")  
print("="*60 + "\n")

# Health Check
print("1. HEALTH CHECK")
r = requests.get(f"{BASE}/health")
health = r.json()
print(f"Status: {health['status']}")
print(f"Services: {health['services']}\n")

# List Funnels
print("2. FUNNEL LIST")
r = requests.get(f"{BASE}/api/funnel/list", headers=AUTH)
print(json.dumps(r.json(), indent=2))

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
