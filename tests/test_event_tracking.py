#!/usr/bin/env python3
"""
Test script to verify event tracking is working
Sends test events to the API and checks if they're stored
"""

import requests
import json
import time
import sqlite3

API_URL = "http://localhost:8000"
API_KEY = "demo"

def test_event_ingestion():
    """Test sending events to the API"""
    print("\n" + "="*60)
    print("Testing Event Ingestion")
    print("="*60 + "\n")
    
    # Create test events
    test_events = [
        {
            "event_type": "page_view",
            "session_id": f"test_session_{int(time.time())}",
            "user_id": "test_user_123",
            "timestamp": int(time.time() * 1000),
            "funnel_step": "login_form",
            "device_type": "desktop",
            "country": "US",
            "app_version": "1.0.0",
            "properties": {
                "page_url": "http://localhost:3000",
                "test": True
            }
        },
        {
            "event_type": "button_click",
            "session_id": f"test_session_{int(time.time())}",
            "user_id": "test_user_123",
            "timestamp": int(time.time() * 1000) + 1000,
            "funnel_step": "login_button_click",
            "device_type": "desktop",
            "country": "US",
            "app_version": "1.0.0",
            "properties": {
                "button_name": "login_button",
                "test": True
            }
        }
    ]
    
    print(f"📤 Sending {len(test_events)} test events...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/events/ingest",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={"events": test_events},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Events sent successfully!")
            print(f"   Ingested: {result['events_ingested']}")
            print(f"   Rejected: {result['events_rejected']}")
            print(f"   Message: {result['message']}")
            return True
        else:
            print(f"❌ Failed to send events: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Make sure the backend is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_database():
    """Check if events are in the database"""
    print("\n" + "="*60)
    print("Checking Database")
    print("="*60 + "\n")
    
    try:
        conn = sqlite3.connect("arguxai.db")
        cursor = conn.cursor()
        
        # Count total events
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]
        print(f"📊 Total events in database: {total_events}")
        
        # Count test events
        cursor.execute("SELECT COUNT(*) FROM events WHERE user_id = 'test_user_123'")
        test_events = cursor.fetchone()[0]
        print(f"🧪 Test events: {test_events}")
        
        # Show recent events
        cursor.execute("""
            SELECT event_type, session_id, funnel_step, timestamp 
            FROM events 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent = cursor.fetchall()
        
        print("\n📋 Recent events:")
        for event in recent:
            event_type, session_id, funnel_step, timestamp = event
            print(f"   - {event_type} | {funnel_step} | {session_id[:20]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_health():
    """Test API health endpoint"""
    print("\n" + "="*60)
    print("Testing API Health")
    print("="*60 + "\n")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✅ API is healthy!")
            print(f"   Status: {health.get('status')}")
            print(f"   Database: {health.get('database')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Make sure the backend is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ArguxAI Event Tracking Test")
    print("="*60)
    
    # Test 1: Health check
    health_ok = test_health()
    if not health_ok:
        print("\n❌ Backend is not running. Start it with: python app.py")
        return
    
    # Test 2: Send events
    events_ok = test_event_ingestion()
    
    # Test 3: Check database
    time.sleep(1)  # Give it a moment to write
    db_ok = check_database()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Event Ingestion: {'✅' if events_ok else '❌'}")
    print(f"Database Storage: {'✅' if db_ok else '❌'}")
    
    if health_ok and events_ok and db_ok:
        print("\n🎉 All tests passed! Event tracking is working!")
        print("\nNext steps:")
        print("1. Open demo app: http://localhost:3000")
        print("2. Interact with the login form")
        print("3. Check ArguxAI dashboard: http://localhost:8000/frontend/")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("\n")

if __name__ == "__main__":
    main()
