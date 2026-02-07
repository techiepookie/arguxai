"""
Helper to get actual time range from database
Used by anomaly detector and metrics calculator
"""

import sqlite3
from pathlib import Path


def get_database_time_range():
    """Get the actual min/max timestamp from stored events"""
    db_path = Path("arguxai.db")
    
    if not db_path.exists():
        return None, None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM events")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] and result[1]:
            return result[0], result[1]
    except:
        pass
    
    return None, None


def get_baseline_and_current_ranges():
    """
    Get time ranges for baseline (days 1-7) and current (days 8-14)
    based on actual data in the database
    """
    min_ts, max_ts = get_database_time_range()
    
    if not min_ts or not max_ts:
        return None, None, None, None
    
    # Total span
    total_span = max_ts - min_ts
    midpoint = min_ts + (total_span // 2)
    
    # Baseline: first half (days 1-7, 90% conversion)
    baseline_start = min_ts
    baseline_end = midpoint
    
    # Current: second half (days 8-14, 45% conversion - THE BUG PERIOD)
    current_start = midpoint
    current_end = max_ts
    
    return baseline_start, baseline_end, current_start, current_end
