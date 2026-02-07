"""Debug what events are in sessions"""
import sqlite3
import json

conn = sqlite3.connect("arguxai.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all events for login_button_click step
cursor.execute("""
    SELECT session_id, event_type, funnel_step, timestamp
    FROM events
    WHERE funnel_step = 'login_button_click'
    ORDER BY session_id, timestamp
    LIMIT 50
""")

events = [dict(row) for row in cursor.fetchall()]

# Group by session
from collections import defaultdict
sessions = defaultdict(list)
for e in events:
    sessions[e['session_id']].append(e)

print("Sample sessions for login_button_click funnel step:")
print("="*70)

for i, (session_id, session_events) in enumerate(list(sessions.items())[:5]):
    print(f"\nSession {i+1}: {session_id}")
    print(f"  Events in this session:")
    for e in session_events:
        print(f"    - {e['event_type']:20} | funnel_step: {e['funnel_step']}")
    
    # Check if completed
    has_complete = any(
        e['event_type'] in ['login_complete', 'custom'] or
        e['funnel_step'] == 'login_complete'
        for e in session_events
    )
    print(f"  → Completed: {has_complete}")

conn.close()
