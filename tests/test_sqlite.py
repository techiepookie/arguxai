"""Test SQLite setup"""
import sqlite3

conn = sqlite3.connect("arguxai.db")
cursor = conn.cursor()

cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]

print(f"Tables in database: {table_count}")

if table_count > 0:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Table names:", tables)
    
    # Check events table
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]
    print(f"Events in database: {event_count}")

conn.close()
