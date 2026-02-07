"""
Quick system test to verify everything is working
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data['name']} v{data['version']}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_dashboard():
    """Test dashboard metrics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/metrics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard metrics: {len(data.get('funnel_steps', []))} funnel steps")
            return True
        else:
            print(f"❌ Dashboard metrics failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard metrics failed: {e}")
        return False

def test_frontend():
    """Test frontend is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/frontend/")
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend failed: {e}")
        return False

def main():
    print("="*50)
    print("ArguxAI System Test")
    print("="*50)
    print()
    
    print("Testing backend...")
    results = []
    results.append(test_health())
    results.append(test_root())
    results.append(test_dashboard())
    results.append(test_frontend())
    
    print()
    print("="*50)
    if all(results):
        print("✅ All tests passed!")
        print("="*50)
        print()
        print("System is ready!")
        print(f"Frontend: {BASE_URL}/frontend/")
        print(f"API Docs: {BASE_URL}/docs")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        print("="*50)
        print()
        print("Troubleshooting:")
        print("1. Make sure the server is running (start.bat)")
        print("2. Check if port 8000 is available")
        print("3. Review server logs for errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
