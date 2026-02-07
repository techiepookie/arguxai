"""
Funnel storage service using SQLite
Manages funnel CRUD operations
"""

import sqlite3
import json
import uuid
import time
from typing import List, Optional
from pathlib import Path
from app.models.funnels import Funnel, FunnelCreate, FunnelUpdate, FunnelStep
from app.core.logging import logger


class FunnelStorage:
    """SQLite-based funnel storage"""
    
    def __init__(self, db_path: str = "arguxai.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize funnels table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_funnel_created ON funnels(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_funnel_name ON funnels(name)")
        
        conn.commit()
        conn.close()
        
        logger.info("Funnel storage initialized", db_path=str(self.db_path))
    
    def create_funnel(self, funnel_data: FunnelCreate) -> Funnel:
        """Create a new funnel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        funnel_id = str(uuid.uuid4())
        now = int(time.time() * 1000)
        
        # Serialize steps to JSON
        steps_json = json.dumps([step.dict() for step in funnel_data.steps])
        
        cursor.execute("""
            INSERT INTO funnels (
                id, name, description, steps,
                created_by_ai, ai_prompt, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            funnel_id,
            funnel_data.name,
            funnel_data.description,
            steps_json,
            1 if funnel_data.created_by_ai else 0,
            funnel_data.ai_prompt,
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Funnel created", funnel_id=funnel_id, name=funnel_data.name)
        
        return Funnel(
            id=funnel_id,
            name=funnel_data.name,
            description=funnel_data.description,
            steps=funnel_data.steps,
            created_by_ai=funnel_data.created_by_ai,
            ai_prompt=funnel_data.ai_prompt,
            created_at=now,
            updated_at=now
        )
    
    def get_funnel(self, funnel_id: str) -> Optional[Funnel]:
        """Get funnel by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM funnels WHERE id = ?", (funnel_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_funnel(row)
    
    def list_funnels(self) -> List[Funnel]:
        """List all funnels"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM funnels ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_funnel(row) for row in rows]
    
    def update_funnel(self, funnel_id: str, updates: FunnelUpdate) -> Optional[Funnel]:
        """Update funnel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        
        if updates.name is not None:
            fields.append("name = ?")
            values.append(updates.name)
        
        if updates.description is not None:
            fields.append("description = ?")
            values.append(updates.description)
        
        if updates.steps is not None:
            fields.append("steps = ?")
            values.append(json.dumps([step.dict() for step in updates.steps]))
        
        if not fields:
            return self.get_funnel(funnel_id)
        
        fields.append("updated_at = ?")
        values.append(int(time.time() * 1000))
        values.append(funnel_id)
        
        query = f"UPDATE funnels SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        logger.info("Funnel updated", funnel_id=funnel_id)
        return self.get_funnel(funnel_id)
    
    def delete_funnel(self, funnel_id: str) -> bool:
        """Delete funnel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM funnels WHERE id = ?", (funnel_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info("Funnel deleted", funnel_id=funnel_id)
        
        return deleted
    
    def _row_to_funnel(self, row) -> Funnel:
        """Convert SQLite row to Funnel model"""
        steps_data = json.loads(row['steps'])
        steps = [FunnelStep(**step) for step in steps_data]
        
        return Funnel(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            steps=steps,
            created_by_ai=bool(row['created_by_ai']),
            ai_prompt=row['ai_prompt'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )


# Global instance
funnel_storage = FunnelStorage()
