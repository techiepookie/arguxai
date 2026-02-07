"""Manually initialize SQLite and test"""
from app.integrations.sqlite_client import SQLiteClient

# Create new client (this should call init_database)
client = SQLiteClient()

# Now test
import sqlite3
conn = sqlite3.connect("arguxai.db")
cursor = conn.cursor()

cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]

print(f"Tables in database: {table_count}")

if table_count > 0:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Table names:", [t[0] for t in tables])

conn.close()
print("✓ SQLite client initialized successfully!")
