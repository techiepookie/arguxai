#!/usr/bin/env python3
"""
ArguxAI - Complete Application Launcher
Run this file to start everything: python app.py
"""

import os
import sys
import subprocess
import sqlite3
import time
import random
from datetime import datetime, timedelta

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("                    ArguxAI")
    print("        AI-Powered Conversion Optimization")
    print("="*60 + "\n")

def check_dependencies():
    """Check if dependencies are installed"""
    print("📦 Checking dependencies...")
    
    missing = []
    required = ['fastapi', 'uvicorn', 'pydantic', 'httpx', 'structlog', 'openai']
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}\n")
        print("Please install dependencies first:")
        print("  python install.py")
        print("\nOr manually:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All dependencies installed\n")
    return True

def initialize_database():
    """Initialize database with tables and sample data"""
    db_path = "arguxai.db"
    
    # Check if database already exists with data
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("SELECT COUNT(*) FROM events")
            event_count = cursor.fetchone()[0]
            conn.close()
            if event_count > 0:
                print(f"✅ Database exists with {event_count} events\n")
                return
        conn.close()
    
    print("🗄️  Initializing database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
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
    
    # Generate sample events
    event_types = [
        ("login_page_view", "login_form"),
        ("login_button_click", "login_button_click"),
        ("form_start", "form_interaction"),
        ("login_complete", "login_complete")
    ]
    
    devices = ["desktop", "mobile", "tablet"]
    countries = ["US", "UK", "CA", "AU", "DE"]
    
    base_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
    events_to_insert = []
    session_count = 1000
    
    for session_num in range(session_count):
        session_id = f"session_{session_num}"
        user_id = f"user_{session_num % 500}"
        device = random.choice(devices)
        country = random.choice(countries)
        timestamp = base_time + (session_num * 60000)
        
        for i, (event_type, funnel_step) in enumerate(event_types):
            if i == 0 or random.random() > 0.2:
                event_id = f"evt_{session_num}_{i}"
                events_to_insert.append((
                    event_id, event_type, session_id, user_id,
                    timestamp + (i * 1000), funnel_step, device,
                    country, "1.0.0", "{}"
                ))
    
    cursor.executemany("""
        INSERT INTO events (id, event_type, session_id, user_id, timestamp, 
                          funnel_step, device_type, country, app_version, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events_to_insert)
    
    # Generate sample issues
    current_time = int(time.time() * 1000)
    issues = [
        ("issue_001", "login_button_click", "critical", "open", current_time - 3600000,
         52.0, 87.0, 40.2, 3.8, "Button positioning bug causing mobile users to miss the login button",
         None, None, current_time - 3600000, current_time - 3600000),
        ("issue_002", "login_complete", "high", "open", current_time - 7200000,
         30.0, 65.0, 53.8, 4.2, "API timeout too short (5s) causing login failures",
         None, None, current_time - 7200000, current_time - 7200000)
    ]
    
    cursor.executemany("""
        INSERT INTO issues (id, funnel_step, severity, status, detected_at,
                          current_conversion_rate, baseline_conversion_rate,
                          drop_percentage, sigma_value, diagnosis,
                          github_pr_url, jira_ticket_key, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, issues)
    
    # Create default funnel
    import json
    funnel_steps = json.dumps([
        {"name": "Page View", "event_type": "login_page_view", "order": 1},
        {"name": "Button Click", "event_type": "login_button_click", "order": 2},
        {"name": "Form Start", "event_type": "form_start", "order": 3},
        {"name": "Login Complete", "event_type": "login_complete", "order": 4}
    ])
    
    cursor.execute("""
        INSERT INTO funnels (id, name, description, steps, created_by_ai, 
                           ai_prompt, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ("funnel_login", "Login Flow", "User login conversion funnel",
          funnel_steps, 0, None, current_time, current_time))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized with {len(events_to_insert)} events\n")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("⚠️  WARNING: .env file not found!")
        print("   Copy .env.example to .env and configure it")
        print("   Continuing with defaults...\n")
        return False
    print("✅ Configuration file found\n")
    return True

def start_server():
    """Start the FastAPI server and demo login app"""
    print("🚀 Starting ArguxAI server...\n")
    print("="*60)
    print("  Backend:   http://localhost:8000/frontend/")
    print("  Demo App:  http://localhost:3000")
    print("  API Docs:  http://localhost:8000/docs")
    print("  Health:    http://localhost:8000/health")
    print("="*60)
    print("\n💡 Press CTRL+C to stop all servers\n")
    
    # Start demo login app HTTP server in background
    import subprocess
    import threading
    
    def start_demo_app():
        """Start demo login app HTTP server"""
        try:
            # Change to demo-login-app directory and start HTTP server
            demo_dir = os.path.join(os.path.dirname(script_dir), 'demo-login-app')
            if os.path.exists(demo_dir):
                print("📱 Starting demo login app on port 3000...")
                subprocess.run(
                    ['python', '-m', 'http.server', '3000'],
                    cwd=demo_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        except Exception as e:
            print(f"⚠️  Demo app failed to start: {e}")
    
    # Start demo app in background thread
    demo_thread = threading.Thread(target=start_demo_app, daemon=True)
    demo_thread.start()
    
    # Give demo app a moment to start
    import time
    time.sleep(1)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n Servers stopped. Goodbye!")
    except Exception as e:
        print(f"\n Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure port 8000 and 3000 are not in use")
        print("2. Check if all dependencies are installed")
        print("3. Verify .env file is configured")
        sys.exit(1)

def main():
    """Main entry point"""
    print_banner()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Check .env file
    check_env_file()
    
    # Step 3: Initialize database
    initialize_database()
    
    # Step 4: Start server
    start_server()

if __name__ == "__main__":
    main()
