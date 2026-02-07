"""
SQLite database client for ArguxAI
Simple, local database storage for events and issues
"""

import sqlite3
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from app.core.logging import logger
from app.config import settings


class SQLiteClient:
    """
    SQLite database client for storing events and issues
    Much simpler than Convex for local development/demo
    """
    
    def __init__(self, db_path: str = "arguxai.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_id TEXT,
                timestamp INTEGER NOT NULL,
                funnel_step TEXT,
                device_type TEXT NOT NULL,
                country TEXT NOT NULL,
                app_version TEXT NOT NULL,
                error_type TEXT,
                error_message TEXT,
                properties TEXT,
                created_at INTEGER NOT NULL
            )
        """)
        
        # Create indexes for events
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON events(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_funnel_step ON events(funnel_step)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_funnel_time ON events(funnel_step, timestamp)")
        
        # Issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id TEXT UNIQUE NOT NULL,
                funnel_step TEXT NOT NULL,
                detected_at INTEGER NOT NULL,
                current_conversion_rate REAL NOT NULL,
                baseline_conversion_rate REAL NOT NULL,
                drop_percentage REAL NOT NULL,
                sigma_value REAL NOT NULL,
                is_significant INTEGER NOT NULL,
                current_sessions INTEGER NOT NULL,
                baseline_sessions INTEGER NOT NULL,
                status TEXT NOT NULL,
                severity TEXT NOT NULL,
                diagnosis TEXT,
                jira_ticket TEXT,
                github_pr TEXT,
                updated_at INTEGER NOT NULL
            )
        """)
        
        # Create indexes for issues
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_issue_funnel_step ON issues(funnel_step)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON issues(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_detected_at ON issues(detected_at)")
        
        conn.commit()
        conn.close()
        
        logger.info("SQLite database initialized", db_path=str(self.db_path))
    
    async def batch_insert_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple events in a batch
        
        Args:
            events: List of event data dictionaries
            
        Returns:
            List of event IDs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            ids = []
            now = int(__import__('time').time() * 1000)
            
            for event in events:
                # Serialize properties to JSON
                properties_json = json.dumps(event.get('properties', {}))
                
                cursor.execute("""
                    INSERT INTO events (
                        event_type, session_id, user_id, timestamp,
                        funnel_step, device_type, country, app_version,
                        error_type, error_message, properties, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['event_type'],
                    event['session_id'],
                    event.get('user_id'),
                    event['timestamp'],
                    event.get('funnel_step'),
                    event['device_type'],
                    event['country'],
                    event['app_version'],
                    event.get('error_type'),
                    event.get('error_message'),
                    properties_json,
                    now
                ))
                
                ids.append(str(cursor.lastrowid))
            
            conn.commit()
            conn.close()
            
            logger.info("Events inserted to SQLite", count=len(ids))
            return ids
            
        except Exception as e:
            logger.error("Failed to batch insert events to SQLite", error=str(e))
            return [f"evt_{i}" for i in range(len(events))]
    
    async def query_events(
        self,
        start_time: int,
        end_time: int,
        funnel_step: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query events from SQLite
        
        Args:
            start_time: Start timestamp (ms)
            end_time: End timestamp (ms)
            funnel_step: Optional funnel step filter
            event_types: Optional event type filters
            
        Returns:
            List of event dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Returns dict-like rows
            cursor = conn.cursor()
            
            if funnel_step:
                cursor.execute("""
                    SELECT * FROM events
                    WHERE funnel_step = ? AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                """, (funnel_step, start_time, end_time))
            else:
                cursor.execute("""
                    SELECT * FROM events
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                """, (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts and parse JSON properties
            events = []
            for row in rows:
                event = dict(row)
                if event.get('properties'):
                    try:
                        event['properties'] = json.loads(event['properties'])
                    except:
                        event['properties'] = {}
                events.append(event)
            
            logger.info("Events queried from SQLite", count=len(events), funnel_step=funnel_step)
            return events
            
        except Exception as e:
            logger.error("Failed to query events from SQLite", error=str(e))
            return []
    
    async def get_distinct_event_types(self) -> List[str]:
        """
        Get list of all distinct event types recorded in the system
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT event_type FROM events ORDER BY event_type")
            rows = cursor.fetchall()
            conn.close()
            return [row[0] for row in rows]
        except Exception as e:
            logger.error("Failed to get distinct event types", error=str(e))
            return []

    async def create_issue(self, issue_data: Dict[str, Any]) -> str:
        """Create a new issue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = int(__import__('time').time() * 1000)
            
            cursor.execute("""
                INSERT INTO issues (
                    issue_id, funnel_step, detected_at,
                    current_conversion_rate, baseline_conversion_rate,
                    drop_percentage, sigma_value, is_significant,
                    current_sessions, baseline_sessions,
                    status, severity, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_data['issue_id'],
                issue_data['funnel_step'],
                issue_data['detected_at'],
                issue_data['current_conversion_rate'],
                issue_data['baseline_conversion_rate'],
                issue_data['drop_percentage'],
                issue_data['sigma_value'],
                1 if issue_data['is_significant'] else 0,
                issue_data['current_sessions'],
                issue_data['baseline_sessions'],
                issue_data['status'],
                issue_data['severity'],
                now
            ))
            
            conn.commit()
            conn.close()
            
            logger.info("Issue created in SQLite", issue_id=issue_data['issue_id'])
            return issue_data['issue_id']
            
        except Exception as e:
            logger.error("Failed to create issue in SQLite", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if SQLite database is accessible"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            logger.error("SQLite health check failed", error=str(e))
            return False
    
    async def close(self):
        """Close connections (no-op for SQLite)"""
        pass


# Global SQLite client instance
sqlite_client = SQLiteClient()
