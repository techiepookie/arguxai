"""Metrics calculation service for conversion funnel analysis"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.metrics import FunnelMetrics, ComparisonMetrics, MetricPeriod
from app.models.events import EventType
from app.integrations.sqlite_client import sqlite_client  # Changed from convex_client
from app.core.logging import logger
from app.config import settings
import statistics


class MetricsCalculator:
    """
    Calculate conversion metrics for funnel analysis
    
    Analyzes event data to compute:
    - Conversion rates per funnel step
    - Drop-off rates
    - Time on step
    - Segmentation by country/device
    - Anomaly detection
    """
    
    def __init__(self):
        self.cache: Dict[str, FunnelMetrics] = {}
        self.cache_ttl = timedelta(minutes=1)
    
    def _get_time_range(self, period: MetricPeriod, use_db_range: bool = False) -> tuple[int, int]:
        """
        Get timestamp range for a metric period
        
        Args:
            period: Metric period enum
            use_db_range: If True, use actual database timestamps instead of "now"
        
        Returns:
            Tuple of (start_timestamp, end_timestamp) in milliseconds
        """
        # If using database range, get actual data timestamps
        if use_db_range:
            try:
                from app.utils.time_range_helper import get_baseline_and_current_ranges
                baseline_start, baseline_end, current_start, current_end = get_baseline_and_current_ranges()
                
                if baseline_start and baseline_end and current_start and current_end:
                    # Map periods to data ranges
                    # LAST_7_DAYS → baseline period (days 1-7, ~90% conversion)
                    # LAST_24_HOURS/LAST_HOUR → current period (days 8-14, ~45% conversion - BUG PERIOD)
                    if period == MetricPeriod.LAST_7_DAYS:
                        logger.info("Using BASELINE period from database", start=baseline_start, end=baseline_end)
                        return baseline_start, baseline_end
                    else:
                        # Any other period = current/recent period
                        logger.info("Using CURRENT period from database", start=current_start, end=current_end)
                        return current_start, current_end
            except Exception as e:
                logger.warning("Failed to get database time range, falling back to relative times", error=str(e))
        
        # Fall back to relative time calculation from "now"
        now = datetime.utcnow()
        
        if period == MetricPeriod.LAST_HOUR:
            start = now - timedelta(hours=1)
        elif period == MetricPeriod.LAST_24_HOURS:
            start = now - timedelta(days=1)
        elif period == MetricPeriod.LAST_7_DAYS:
            start = now - timedelta(days=7)
        else:  # LAST_30_DAYS
            start = now - timedelta(days=30)
        
        return (
            int(start.timestamp() * 1000),
            int(now.timestamp() * 1000)
        )
    
    async def calculate_funnel_metrics(
        self,
        funnel_step: str,
        period: MetricPeriod = MetricPeriod.LAST_24_HOURS,
        use_db_range: bool = True  # NEW: default to using actual DB timestamps
    ) -> FunnelMetrics:
        """
        Calculate metrics for a specific funnel step
        
        Args:
            funnel_step: Name of the funnel step
            period: Time period for calculation
            use_db_range: Use actual database time range (True) or relative to now (False)
            
        Returns:
            Calculated funnel metrics
        """
        try:
            # Get time range (uses DB timestamps by default)
            start_ts, end_ts = self._get_time_range(period, use_db_range=use_db_range)
            
            logger.info(
                "Calculating funnel metrics",
                funnel_step=funnel_step,
                period=period,
                start_ts=start_ts,
                end_ts=end_ts,
                use_db_range=use_db_range
            )
            
            # Query events from SQLite
            # CRITICAL: We need to get FULL customer journeys, not just events at this step!
            # Step 1: Find sessions that passed through this funnel step
            import sqlite3
            conn = sqlite3.connect(self.db_path if hasattr(self, 'db_path') else "arguxai.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT session_id
                FROM events
                WHERE funnel_step = ? AND timestamp >= ? AND timestamp <= ?
            """, (funnel_step, start_ts, end_ts))
            
            session_ids = [row[0] for row in cursor.fetchall()]
            logger.info(
                "Found sessions for funnel step",
                funnel_step=funnel_step,
                session_count=len(session_ids)
            )
            
            if len(session_ids) == 0:
                conn.close()
                logger.warning(
                    "No sessions found for funnel step",
                    funnel_step=funnel_step,
                    period=period,
                    start_ts=start_ts,
                    end_ts=end_ts
                )
                # Return empty metrics
                return FunnelMetrics(
                    funnel_step=funnel_step,
                    period=period,
                    timestamp_start=start_ts,
                    timestamp_end=end_ts,
                    total_sessions=0,
                    completed_sessions=0,
                    conversion_rate=0.0,
                    drop_off_rate=100.0,
                    by_country={},
                    by_device={},
                    mean_time_on_step=None,
                    median_time_on_step=None
                )
            
            # Step 2: Get ALL events for these sessions to track full customer journey
            placeholders = ','.join('?' * len(session_ids))
            cursor.execute(f"""
                SELECT *
                FROM events
                WHERE session_id IN ({placeholders})
                ORDER BY session_id, timestamp
            """, session_ids)
            
            all_events = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(
                "Retrieved full customer journeys",
                total_events=len(all_events)
            )
            
            # Parse JSON properties
            for event in all_events:
                if event.get('properties'):
                    try:
                        import json
                        event['properties'] = json.loads(event['properties'])
                    except:
                        event['properties'] = {}
            
            # Calculate metrics from real events (full customer journeys)
            return self._calculate_from_events(all_events, funnel_step, period, start_ts, end_ts)
            
        except Exception as e:
            logger.error("Failed to calculate funnel metrics", error=str(e), funnel_step=funnel_step)
            raise
    
    def _generate_demo_metrics(
        self,
        funnel_step: str,
        period: str,
        start_ts: int,
        end_ts: int
    ) -> FunnelMetrics:
        """Generate realistic demo metrics for testing"""
        
        # Simulate different conversion rates per step
        conversion_rates = {
            "signup_form": 92.0,
            "otp_verification": 85.0,
            "profile_creation": 78.0,
            "conversion": 95.0
        }
        
        base_sessions = {
            MetricPeriod.LAST_HOUR: 100,
            MetricPeriod.LAST_24_HOURS: 1000,
            MetricPeriod.LAST_7_DAYS: 5000,
            MetricPeriod.LAST_30_DAYS: 20000
        }
        
        total = base_sessions.get(period, 1000)
        conv_rate = conversion_rates.get(funnel_step, 85.0)
        completed = int(total * conv_rate / 100)
        
        return FunnelMetrics(
            funnel_step=funnel_step,
            period=period,
            timestamp_start=start_ts,
            timestamp_end=end_ts,
            total_sessions=total,
            completed_sessions=completed,
            conversion_rate=conv_rate,
            drop_off_rate=100.0 - conv_rate,
            by_country={
                "US": int(total * 0.6),
                "IN": int(total * 0.25),
                "UK": int(total * 0.15)
            },
            by_device={
                "mobile": int(total * 0.8),
                "desktop": int(total * 0.2)
            },
            mean_time_on_step=45.5,
            median_time_on_step=38.0
        )
    
    def _calculate_from_events(
        self,
        events: List[Dict],
        funnel_step: str,
        period: str,
        start_ts: int,
        end_ts: int
    ) -> FunnelMetrics:
        """Calculate metrics from real event data"""
        
        # Group by session
        sessions = defaultdict(list)
        for event in events:
            sessions[event['session_id']].append(event)
        
        total_sessions = len(sessions)
        completed_sessions = 0
        
        # Segmentation counters
        country_counts = defaultdict(int)
        device_counts = defaultdict(int)
        time_on_step = []
        
        # Analyze each session
        for session_id, session_events in sessions.items():
            # Sort by timestamp
            session_events.sort(key=lambda e: e['timestamp'])
            
            # Check if session completed the step
            # For login flow, completion means reaching the NEXT step
            # E.g., for login_button_click → completed if there's a login_complete event
            completion_events = ['login_complete', 'custom']  # Events that indicate completion
            
            has_success = any(
                e.get('event_type') in completion_events or
                e.get('funnel_step') == 'login_complete'
                for e in session_events
            )
            
            if has_success:
                completed_sessions += 1
            
            # Track segmentation
            first_event = session_events[0]
            country_counts[first_event.get('country', 'unknown')] += 1
            device_counts[first_event.get('device_type', 'unknown')] += 1
            
            # Calculate time on step
            if len(session_events) >= 2:
                duration = (session_events[-1]['timestamp'] - session_events[0]['timestamp']) / 1000
                time_on_step.append(duration)
        
        # Calculate stats
        conversion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        mean_time = statistics.mean(time_on_step) if time_on_step else None
        median_time = statistics.median(time_on_step) if time_on_step else None
        
        return FunnelMetrics(
            funnel_step=funnel_step,
            period=period,
            timestamp_start=start_ts,
            timestamp_end=end_ts,
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            conversion_rate=round(conversion_rate, 2),
            drop_off_rate=round(100.0 - conversion_rate, 2),
            by_country=dict(country_counts),
            by_device=dict(device_counts),
            mean_time_on_step=round(mean_time, 1) if mean_time else None,
            median_time_on_step=round(median_time, 1) if median_time else None
        )
    
    async def compare_with_baseline(
        self,
        funnel_step: str,
        current_period: MetricPeriod = MetricPeriod.LAST_HOUR,
        baseline_period: MetricPeriod = MetricPeriod.LAST_24_HOURS,
        use_db_range: bool = True  # NEW: default to using actual DB timestamps
    ) -> ComparisonMetrics:
        """
        Compare current metrics with baseline to detect anomalies
        
        Args:
            funnel_step: Funnel step to analyze
            current_period: Recent period to check
            baseline_period: Baseline period for comparison
            use_db_range: Use actual database time range (True) or relative to now (False)
            
        Returns:
            Comparison metrics with anomaly detection
        """
        # Calculate both metrics (using database time ranges)
        current = await self.calculate_funnel_metrics(funnel_step, current_period, use_db_range=use_db_range)
        baseline = await self.calculate_funnel_metrics(funnel_step, baseline_period, use_db_range=use_db_range)
        
        # Calculate deltas
        conv_rate_delta = current.conversion_rate - baseline.conversion_rate
        sessions_delta = current.total_sessions - baseline.total_sessions
        
        # Detect significant drops
        drop_detected = False
        drop_percentage = None
        
        if conv_rate_delta < -settings.min_drop_percent:
            drop_detected = True
            drop_percentage = abs(conv_rate_delta)
            
            logger.warning(
                "Significant conversion drop detected",
                funnel_step=funnel_step,
                current_rate=current.conversion_rate,
                baseline_rate=baseline.conversion_rate,
                drop_percentage=drop_percentage
            )
        
        return ComparisonMetrics(
            current=current,
            baseline=baseline,
            conversion_rate_delta=round(conv_rate_delta, 2),
            sessions_delta=sessions_delta,
            drop_detected=drop_detected,
            drop_percentage=round(drop_percentage, 2) if drop_percentage else None
        )


# Global metrics calculator instance
metrics_calculator = MetricsCalculator()
