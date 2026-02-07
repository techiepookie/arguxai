"""
Simple conversion funnel analyzer
Calculates conversion rates by looking at full customer journeys
"""

import sqlite3
from collections import defaultdict

def analyze_funnel_step(funnel_step, start_ts, end_ts):
    """
    Analyze conversion for a funnel step by looking at complete user journeys
    
    Args:
        funnel_step: The step to analyze (e.g., 'login_button_click')
        start_ts: Start timestamp
        end_ts: End timestamp
    
    Returns:
        dict with total_sessions, completed_sessions, conversion_rate
    """
    conn = sqlite3.connect("arguxai.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Step 1: Find all sessions that reached the funnel step in this time period
    cursor.execute("""
        SELECT DISTINCT session_id
        FROM events
        WHERE funnel_step = ? AND timestamp >= ? AND timestamp <= ?
    """, (funnel_step, start_ts, end_ts))
    
    session_ids = [row[0] for row in cursor.fetchall()]
    total_sessions = len(session_ids)
    
    if total_sessions == 0:
        conn.close()
        return {
            'total_sessions': 0,
            'completed_sessions': 0,
            'conversion_rate': 0.0
        }
    
    # Step 2: For each session, get ALL events to see if they completed
    completed_sessions = 0
    
    for session_id in session_ids:
        # Get all events for this session
        cursor.execute("""
            SELECT event_type, funnel_step
            FROM events
            WHERE session_id = ?
            ORDER BY timestamp
        """, (session_id,))
        
        session_events = [dict(row) for row in cursor.fetchall()]
        
        # Check if session reached login_complete (the success event)
        has_complete = any(
            e['funnel_step'] == 'login_complete'
            for e in session_events
        )
        
        if has_complete:
            completed_sessions += 1
    
    conn.close()
    
    conversion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
    
    return {
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'conversion_rate': round(conversion_rate, 2)
    }


if __name__ == "__main__":
    from app.utils.time_range_helper import get_baseline_and_current_ranges
    
    baseline_start, baseline_end, current_start, current_end = get_baseline_and_current_ranges()
    
    print("\n=== FUNNEL ANALYSIS: login_button_click ===\n")
    
    print("📊 BASELINE Period (Days 1-7, ~90% conversion expected):")
    baseline = analyze_funnel_step('login_button_click', baseline_start, baseline_end)
    print(f"  Total sessions: {baseline['total_sessions']}")
    print(f"  Completed: {baseline['completed_sessions']}")
    print(f"  Conversion rate: {baseline['conversion_rate']}%\n")
    
    print("📊 CURRENT Period (Days 8-14, ~45% conversion - BUG PERIOD):")
    current = analyze_funnel_step('login_button_click', current_start, current_end)
    print(f"  Total sessions: {current['total_sessions']}")
    print(f"  Completed: {current['completed_sessions']}")
    print(f"  Conversion rate: {current['conversion_rate']}%\n")
    
    if baseline['conversion_rate'] > 0 and current['conversion_rate'] > 0:
        drop = baseline['conversion_rate'] - current['conversion_rate']
        print(f"🚨 CONVERSION DROP: {drop:.1f} percentage points!")
        print(f"   From {baseline['conversion_rate']}% → {current['conversion_rate']}%")
        
        if drop >= 10:
            print(f"   ⚠️  SIGNIFICANT ANOMALY DETECTED!")
