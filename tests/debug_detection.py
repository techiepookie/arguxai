"""
Debug script to check if events are in Convex and what the anomaly detector sees
"""

import asyncio
from app.services.event_ingestion import event_ingestion_service
from app.services.anomaly_detector import anomaly_detector

async def debug():
    print("\n=== DEBUGGING ANOMALY DETECTION ===\n")
    
    # Check what events exist
    print("1. Checking funnel steps in events...")
    
    funnel_steps = [
        "login_page",
        "login_form",
        "login_button_click",
        "login_complete"
    ]
    
    for step in funnel_steps:
        print(f"\nScanning step: {step}")
        
        try:
            result = await anomaly_detector.scan_funnel_step(step)
            
            if result:
                print(f"  ANOMALY DETECTED!")
                print(f"    Baseline: {result.baseline_rate}%")
                print(f"    Current: {result.current_rate}%")
                print(f"    Drop: {result.drop_percentage}%")
            else:
                print(f"  No anomaly detected")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n=== END DEBUG ===\n")

if __name__ == "__main__":
    asyncio.run(debug())
