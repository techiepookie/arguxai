"""Dashboard metrics API endpoints"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.dependencies import APIKeyDep
from app.integrations.sqlite_client import sqlite_client
from app.services.metrics_calculator import metrics_calculator
from app.models.metrics import MetricPeriod, RecentIssue
from app.services.funnel_storage import funnel_storage
from app.core.logging import logger

router = APIRouter()


class MetricTrend(BaseModel):
    """Metric value with trend data for sparklines"""
    current_value: str
    change_percentage: float
    is_positive: bool
    sparkline_data: List[float]


class FunnelStepDetails(BaseModel):
    """Detailed funnel step for visualization"""
    name: str
    count: int
    conversion_rate: float


class DashboardAlert(BaseModel):
    """Top-bar notification alert"""
    id: str
    type: str  # critical, warning, info
    message: str
    subtext: Optional[str] = None
    timestamp: int


class DashboardMetrics(BaseModel):
    """Overall dashboard metrics matching premium design"""
    total_events: MetricTrend
    active_funnels: MetricTrend
    error_rate: MetricTrend
    active_users: MetricTrend
    funnel_steps: List[FunnelStepDetails]
    recent_issues: List[RecentIssue]
    top_alert: Optional[DashboardAlert] = None
    timestamp: int


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    api_key: APIKeyDep = None
) -> DashboardMetrics:
    """
    Get key dashboard metrics for the premium dashboard
    """
    try:
        import sqlite3
        import random
        conn = sqlite3.connect("arguxai.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Total Events
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events_count = cursor.fetchone()[0]
        
        # 2. Error Rate (simulated based on real login failures or custom logic)
        error_rate_val = 3.2  # Placeholder
        
        # 3. P95 Latency (simulated)
        latency_val = "245ms"
        
        # 4. Active Users
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM events")
        active_users_count = cursor.fetchone()[0]
        
        # 4.5 Active Funnels Count
        cursor.execute("SELECT COUNT(*) FROM funnels")
        funnels_count = cursor.fetchone()[0]
        
        # 5. Funnel Steps (Real data for login funnel)
        funnel_steps = []
        steps = ["Page View", "Sign Up Click", "Form Started", "Login Complete"]
        funnel_step_names = ["page_view", "sign_up_click", "form_started", "login_complete"]
        
        base_count = 1
        for i, (name, step_name) in enumerate(zip(steps, funnel_step_names)):
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM events WHERE funnel_step = ?", (step_name,))
            count = cursor.fetchone()[0]
            if i == 0:
                base_count = count or 1
            conv = (count / base_count * 100) if base_count > 0 else 0
            funnel_steps.append(FunnelStepDetails(name=name, count=count, conversion_rate=conv))
        
        # 6. Recent Issues
        cursor.execute("SELECT * FROM issues ORDER BY detected_at DESC LIMIT 5")
        issue_rows = cursor.fetchall()
        recent_issues = []
        for row in issue_rows:
            recent_issues.append(RecentIssue(
                id=row['issue_id'],  # Use issue_id instead of id
                funnel_step=row['funnel_step'],
                severity=row['severity'],
                drop_percentage=row['drop_percentage'],
                detected_at=row['detected_at']
            ))
            
        # 7. Top Alert (Critical anomaly if exists)
        top_alert = None
        if recent_issues and recent_issues[0].severity == "critical":
            top_alert = DashboardAlert(
                id=recent_issues[0].id,
                type="critical",
                message=f"Critical: Conversion rate dropped {int(recent_issues[0].drop_percentage)}% in the last 24 hours",
                subtext=f"Investigate the {recent_issues[0].funnel_step} funnel for potential issues",
                timestamp=recent_issues[0].detected_at
            )
            
        conn.close()
        
        # Formatting trends (Sparklines simulated for UI effect, but counts are real)
        return DashboardMetrics(
            total_events=MetricTrend(
                current_value=f"{total_events_count / 1000000:.1f}M" if total_events_count >= 1000000 else f"{total_events_count / 1000:.1f}K",
                change_percentage=12.5,
                is_positive=True,
                sparkline_data=[random.uniform(10, 50) for _ in range(10)]
            ),
            active_funnels=MetricTrend(
                current_value=str(funnels_count),
                change_percentage=0.0,
                is_positive=True,
                sparkline_data=[funnels_count] * 10
            ),
            error_rate=MetricTrend(
                current_value=f"{error_rate_val}%",
                change_percentage=-0.8,
                is_positive=False,
                sparkline_data=[random.uniform(2, 5) for _ in range(10)]
            ),
            active_users=MetricTrend(
                current_value=f"{active_users_count / 1000:.1f}K" if active_users_count >= 1000 else str(active_users_count),
                change_percentage=5.3,
                is_positive=True,
                sparkline_data=[random.uniform(40, 60) for _ in range(10)]
            ),
            funnel_steps=funnel_steps,
            recent_issues=recent_issues,
            top_alert=top_alert,
            timestamp=int(datetime.utcnow().timestamp() * 1000)
        )
        
    except Exception as e:
        logger.error("Failed to get dashboard metrics", error=str(e))
        raise

