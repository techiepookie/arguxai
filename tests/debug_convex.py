"""
Direct debug script to check what events exist in Convex
"""

import asyncio
from app.integrations.convex_client import convex_client

async def debug_convex():
    print("\n=== CHECKING CONVEX DATABASE ===\n")
    
    # Query all events
    print("Querying all events...")
    
    try:
        # Try to query events
        all_events = await convex_client.query("events:list", {})
        
        print(f"Total events in database: {len(all_events)}")
        
        if all_events:
            print("\nFirst 5 events:")
            for event in all_events[:5]:
                print(f"  - {event.get('event_type')} | {event.get('funnel_step')} | {event.get('timestamp')}")
            
            # Group by funnel step
            from collections import Counter
            funnel_steps = Counter([e.get('funnel_step') for e in all_events if e.get('funnel_step')])
            
            print("\nEvents per funnel step:")
            for step, count in funnel_steps.most_common():
                print(f"  {step}: {count} events")
        else:
            print("NO EVENTS FOUND IN DATABASE!")
            
    except Exception as e:
        print(f"ERROR querying Convex: {e}")
    
    print("\n=== END DEBUG ===\n")

if __name__ == "__main__":
    asyncio.run(debug_convex())
