"""Check if events are actually in SQLite"""
import sqlite3

conn = sqlite3.connect("arguxai.db")
cursor = conn.cursor()

# Count total events
cursor.execute("SELECT COUNT(*) FROM events")
total_events = cursor.fetchone()[0]
print(f"Total events in database: {total_events}")

# Count by funnel step
cursor.execute("SELECT funnel_step, COUNT(*) FROM events GROUP BY funnel_step")
funnel_counts = cursor.fetchall()
print("\nEvents by funnel step:")
for step, count in funnel_counts:
    print(f"  {step}: {count}")

#  Get earliest and latest timestamps
cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM events")
min_ts, max_ts = cursor.fetchone()
print(f"\nTimestamp range:")
print(f"  Earliest: {min_ts}")
print(f"  Latest: {max_ts}")

#  Sample of first few events
cursor.execute("SELECT event_type, funnel_step, timestamp, device_type FROM events LIMIT 5")
print("\nSample events:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
