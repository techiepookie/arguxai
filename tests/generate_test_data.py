"""
Generate realistic event data with conversion drop
This simulates users interacting with the demo app over time
"""

import httpx
import asyncio
import time
import random

API_URL = "http://localhost:8000"
API_KEY = "demo"

async def generate_events():
    client = httpx.AsyncClient(timeout=30.0)
    
    print("\n" + "="*70)
    print("GENERATING REALISTIC EVENT DATA")
    print("="*70 + "\n")
    
    print("Simulating user behavior:")
    print("  - Days 1-7 (Baseline): 90% conversion rate")
    print("  - Days 8-14 (Problem): 45% conversion rate (BUTTON BUG + API TIMEOUT)")
    print("\n")
    
    all_events = []
    
    # Simulate 14 days of data
    base_timestamp = int(time.time() * 1000) - (14 * 24 * 60 * 60 * 1000)  # 14 days ago
    
    for day in range(14):
        print(f"Day {day + 1}: ", end="")
        
        # Days 1-7: Normal (90% conversion)
        #  Days 8-14: Bug introduced (45% conversion)
        is_buggy_period = day >= 7
        
        # Generate 50 user sessions per day
        for session_num in range(50):
            user_id = f"user_day{day}_{session_num}"
            session_id = f"session_{base_timestamp + (day * 24 * 60 * 60 * 1000)}_{session_num}"
            session_timestamp = base_timestamp + (day * 24 * 60 * 60 * 1000) + (session_num * 1000)
            
            device_type = "mobile" if session_num % 3 == 0 else "desktop"
            
            # Event 1: Page view (100% of users)
            all_events.append({
                "event_type": "page_view",
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": session_timestamp,
                "funnel_step": "login_page",
                "device_type": device_type,
                "country": "US",
                "app_version": "1.0.0",
                "properties": {}
            })
            
            # Event 2: Form viewed (95% progress through)
            if random.random() < 0.95:
                all_events.append({
                    "event_type": "login_form_viewed",
                    "session_id": session_id,
                    "user_id": user_id,
                    "timestamp": session_timestamp + 1000,
                    "funnel_step": "login_form",
                    "device_type": device_type,
                    "country": "US",
                    "app_version": "1.0.0",
                    "properties": {}
                })
                
                # Event 3: Button click
                # Normal period: 95% can click
                # Bug period: 50% can click (button positioning bug on mobile, 60% mobile traffic)
                click_rate = 0.50 if is_buggy_period else 0.95
                
                if random.random() < click_rate:
                    all_events.append({
                        "event_type": "button_click",
                        "session_id": session_id,
                        "user_id": user_id,
                        "timestamp": session_timestamp + 2000,
                        "funnel_step": "login_button_click",
                        "device_type": device_type,
                        "country": "US",
                        "app_version": "1.0.0",
                        "properties": {"button_name": "login_button"}
                    })
                    
                    # Event 4: Login success/error
                    # Normal period: 95% succeed
                    # Bug period: 45% succeed (API timeout)
                    success_rate = 0.45 if is_buggy_period else 0.95
                    
                    if random.random() < success_rate:
                        # Success!
                        all_events.append({
                            "event_type": "custom",
                            "session_id": session_id,
                            "user_id": user_id,
                            "timestamp": session_timestamp + 5000,
                            "funnel_step": "login_complete",
                            "device_type": device_type,
                            "country": "US",
                            "app_version": "1.0.0",
                            "properties": {"conversion_event": "login_success"}
                        })
                    else:
                        # Timeout error!
                        all_events.append({
                            "event_type": "error",
                            "session_id": session_id,
                            "user_id": user_id,
                            "timestamp": session_timestamp + 5000,
                            "funnel_step": "login_error",
                            "device_type": device_type,
                            "country": "US",
                            "app_version": "1.0.0",
                            "properties": {
                                "error_message": "Login timed out. Please try again.",
                                "error_type": "TimeoutError"
                            }
                        })
        
        print(f"{len([e for e in all_events if base_timestamp + (day * 24 * 60 * 60 * 1000) <= e['timestamp'] < base_timestamp + ((day + 1) * 24 * 60 * 60 * 1000)])} events")
    
    # Send all events to API
    print(f"\nSending {len(all_events)} events to ArguxAI...")
    
    # Send in batches of 100
    for i in range(0, len(all_events), 100):
        batch = all_events[i:i+100]
        
        try:
            response = await client.post(
                f"{API_URL}/api/events/ingest",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"events": batch}
            )
            
            if response.status_code == 200:
                print(f"  Batch {i//100 + 1}: Sent {len(batch)} events")
            else:
                print(f"  Batch {i//100 + 1}: ERROR {response.status_code}")
        
        except Exception as e:
            print(f"  Batch {i//100 + 1}: ERROR {e}")
    
    print(f"\nSUCCESS: {len(all_events)} events generated and sent!")
    print("\nNow run: python trigger_workflow.py")
    print("="*70 + "\n")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(generate_events())
