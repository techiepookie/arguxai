"""
Initialize ArguxAI System
- Creates database tables
- Generates sample data
- Verifies configuration
"""

import sqlite3
import time
import random
from datetime import datetime, timedelta

def create_tables():
    """Create all necessary database tables"""
    print("Creating database tables...")
    
    conn = sqlite3.connect("arguxai.db")
    cursor = conn.cursor()
    
    # Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_id TEXT,
            timestamp INTEGER NOT NULL,
            funnel_step TEXT,
            device_type TEXT,
            country TEXT,
            app_version TEXT,
            properties TEXT
        )
    """)
    
    # Issues table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id TEXT PRIMARY KEY,
            funnel_step TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            detected_at INTEGER NOT NULL,
            current_conversion_rate REAL,
            baseline_conversion_rate REAL,
            drop_percentage REAL,
            sigma_value REAL,
            diagnosis TEXT,
            github_pr_url TEXT,
            jira_ticket_key TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)
    
    # Funnels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funnels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            steps TEXT NOT NULL,
            created_by_ai INTEGER DEFAULT 0,
            ai_prompt TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database tables created")


def generate_sample_events():
    """Generate sample events for testing"""
    print("Generating sample events...")
    
    conn = sqlite3.connect("arguxai.db")
    cursor = conn.cursor()
    
    # Check if events already exist
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] > 0:
        print("⚠️  Events already exist, skipping generation")
        conn.close()
        return
    
    event_types = [
        ("login_page_view", "login_form"),
        ("login_button_click", "login_button_click"),
        ("form_start", "form_interaction"),
        ("login_complete", "login_complete")
    ]
    
    devices = ["desktop", "mobile", "tablet"]
    countries = ["US", "UK", "CA", "AU", "DE"]
    
    # Generate events for last 7 days
    base_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
    
    events_to_insert = []
    session_count = 1000
    
    for session_num in range(session_count):
        session_id = f"session_{session_num}"
        user_id = f"user_{session_num % 500}"  # 500 unique users
        device = random.choice(devices)
        country = random.choice(countries)
        
        # Simulate funnel progression
        timestamp = base_time + (session_num * 60000)  # 1 minute apart
        
        for i, (event_type, funnel_step) in enumerate(event_types):
            # Drop-off simulation
            if i == 0 or random.random() > 0.2:  # 80% continue
                event_id = f"evt_{session_num}_{i}"
                events_to_insert.append((
                    event_id,
                    event_type,
                    session_id,
                    user_id,
                    timestamp + (i * 1000),
                    funnel_step,
                    device,
                    country,
                    "1.0.0",
                    "{}"
                ))
    
    cursor.executemany("""
        INSERT INTO events (id, event_type, session_id, user_id, timestamp, 
                          funnel_step, device_type, country, app_version, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events_to_insert)
    
    conn.commit()
    conn.close()
    print(f"✅ Generated {len(events_to_insert)} sample events")


def generate_sample_issues():
    """Generate sample issues for testing"""
    print("Generating sample issues...")
    
    conn = sqlite3.connect("arguxai.db")
    cursor = conn.cursor()
    
    # Check if issues already exist
    cursor.execute("SELECT COUNT(*) FROM issues")
    if cursor.fetchone()[0] > 0:
        print("⚠️  Issues already exist, skipping generation")
        conn.close()
        return
    
    current_time = int(time.time() * 1000)
    
    issues = [
        {
            "id": "issue_001",
            "funnel_step": "login_button_click",
            "severity": "critical",
            "status": "open",
            "detected_at": current_time - 3600000,  # 1 hour ago
            "current_conversion_rate": 52.0,
            "baseline_conversion_rate": 87.0,
            "drop_percentage": 40.2,
            "sigma_value": 3.8,
            "diagnosis": "Button positioning bug causing mobile users to miss the login button",
            "github_pr_url": None,
            "jira_ticket_key": None,
            "created_at": current_time - 3600000,
            "updated_at": current_time - 3600000
        },
        {
            "id": "issue_002",
            "funnel_step": "login_complete",
            "severity": "high",
            "status": "open",
            "detected_at": current_time - 7200000,  # 2 hours ago
            "current_conversion_rate": 30.0,
            "baseline_conversion_rate": 65.0,
            "drop_percentage": 53.8,
            "sigma_value": 4.2,
            "diagnosis": "API timeout too short (5s) causing login failures",
            "github_pr_url": None,
            "jira_ticket_key": None,
            "created_at": current_time - 7200000,
            "updated_at": current_time - 7200000
        }
    ]
    
    for issue in issues:
        cursor.execute("""
            INSERT INTO issues (id, funnel_step, severity, status, detected_at,
                              current_conversion_rate, baseline_conversion_rate,
                              drop_percentage, sigma_value, diagnosis,
                              github_pr_url, jira_ticket_key, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            issue["id"], issue["funnel_step"], issue["severity"], issue["status"],
            issue["detected_at"], issue["current_conversion_rate"],
            issue["baseline_conversion_rate"], issue["drop_percentage"],
            issue["sigma_value"], issue["diagnosis"], issue["github_pr_url"],
            issue["jira_ticket_key"], issue["created_at"], issue["updated_at"]
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Generated {len(issues)} sample issues")


def create_default_funnel():
    """Create a default login funnel"""
    print("Creating default funnel...")
    
    conn = sqlite3.connect("arguxai.db")
    cursor = conn.cursor()
    
    # Check if funnel already exists
    cursor.execute("SELECT COUNT(*) FROM funnels")
    if cursor.fetchone()[0] > 0:
        print("⚠️  Funnels already exist, skipping creation")
        conn.close()
        return
    
    import json
    current_time = int(time.time() * 1000)
    
    funnel = {
        "id": "funnel_login",
        "name": "Login Flow",
        "description": "User login conversion funnel",
        "steps": json.dumps([
            {"name": "Page View", "event_type": "login_page_view", "order": 1},
            {"name": "Button Click", "event_type": "login_button_click", "order": 2},
            {"name": "Form Start", "event_type": "form_start", "order": 3},
            {"name": "Login Complete", "event_type": "login_complete", "order": 4}
        ]),
        "created_by_ai": 0,
        "ai_prompt": None,
        "created_at": current_time,
        "updated_at": current_time
    }
    
    cursor.execute("""
        INSERT INTO funnels (id, name, description, steps, created_by_ai, 
                           ai_prompt, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        funnel["id"], funnel["name"], funnel["description"], funnel["steps"],
        funnel["created_by_ai"], funnel["ai_prompt"], funnel["created_at"],
        funnel["updated_at"]
    ))
    
    conn.commit()
    conn.close()
    print("✅ Created default login funnel")


def verify_setup():
    """Verify the setup is complete"""
    print("\n" + "="*50)
    print("Verifying setup...")
    print("="*50)
    
    conn = sqlite3.connect("arguxai.db")
    cursor = conn.cursor()
    
    # Check events
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]
    print(f"✅ Events: {event_count}")
    
    # Check issues
    cursor.execute("SELECT COUNT(*) FROM issues")
    issue_count = cursor.fetchone()[0]
    print(f"✅ Issues: {issue_count}")
    
    # Check funnels
    cursor.execute("SELECT COUNT(*) FROM funnels")
    funnel_count = cursor.fetchone()[0]
    print(f"✅ Funnels: {funnel_count}")
    
    conn.close()
    
    print("\n" + "="*50)
    print("✅ System initialized successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Run: start.bat")
    print("2. Open: http://localhost:8000/frontend/")
    print("3. Explore the dashboard!")


if __name__ == "__main__":
    print("="*50)
    print("ArguxAI System Initialization")
    print("="*50)
    print()
    
    create_tables()
    generate_sample_events()
    generate_sample_issues()
    create_default_funnel()
    verify_setup()
