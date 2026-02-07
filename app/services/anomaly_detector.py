"""Anomaly detection service with statistical analysis"""

from typing import Optional, List
from datetime import datetime, timedelta
import statistics
from app.models.metrics import MetricPeriod, ComparisonMetrics
from app.models.issues import Anomaly
from app.services.metrics_calculator import metrics_calculator
from app.config import settings
from app.core.logging import logger


class AnomalyDetector:
    """
    Statistical anomaly detection for conversion metrics
    
    Uses:
    - Rolling baseline calculation (7-day)
    - Z-score (sigma) based significance testing
    - Configurable thresholds
    """
    
    def __init__(self):
        self.min_drop_percent = settings.min_drop_percent
        self.sigma_threshold = settings.sigma_threshold
        self.min_sample_size = settings.min_sample_size
    
    async def detect_anomaly(
        self,
        funnel_step: str,
        current_period: MetricPeriod = MetricPeriod.LAST_HOUR,
        baseline_period: MetricPeriod = MetricPeriod.LAST_7_DAYS
    ) -> Optional[Anomaly]:
        """
        Detect if there's a statistically significant anomaly
        
        Args:
            funnel_step: Funnel step to check
            current_period: Recent period to analyze
            baseline_period: Historical baseline for comparison
            
        Returns:
            Anomaly object if detected, None otherwise
        """
        try:
            # Get comparison metrics
            comparison = await metrics_calculator.compare_with_baseline(
                funnel_step=funnel_step,
                current_period=current_period,
                baseline_period=baseline_period
            )
            
            # Check if we have enough data
            if comparison.current.total_sessions < self.min_sample_size:
                logger.debug(
                    "Insufficient sample size for anomaly detection",
                    funnel_step=funnel_step,
                    sessions=comparison.current.total_sessions,
                    required=self.min_sample_size
                )
                return None
            
            # Calculate drop percentage
            drop_pct = abs(comparison.conversion_rate_delta)
            
            # Check if drop exceeds threshold
            if comparison.conversion_rate_delta >= -self.min_drop_percent:
                logger.debug(
                    "No significant drop detected",
                    funnel_step=funnel_step,
                    delta=comparison.conversion_rate_delta,
                    threshold=self.min_drop_percent
                )
                return None
            
            # Calculate statistical significance (Z-score approximation)
            sigma_value = self._calculate_sigma(
                current_rate=comparison.current.conversion_rate,
                baseline_rate=comparison.baseline.conversion_rate,
                current_n=comparison.current.total_sessions,
                baseline_n=comparison.baseline.total_sessions
            )
            
            # Check if statistically significant
            is_significant = sigma_value >= self.sigma_threshold
            
            if not is_significant:
                logger.debug(
                    "Drop detected but not statistically significant",
                    funnel_step=funnel_step,
                    sigma=sigma_value,
                    threshold=self.sigma_threshold
                )
                return None
            
            # Create anomaly object
            anomaly = Anomaly(
                funnel_step=funnel_step,
                detected_at=int(datetime.utcnow().timestamp() * 1000),
                current_conversion_rate=comparison.current.conversion_rate,
                baseline_conversion_rate=comparison.baseline.conversion_rate,
                drop_percentage=drop_pct,
                sigma_value=round(sigma_value, 2),
                is_significant=is_significant,
                current_sessions=comparison.current.total_sessions,
                baseline_sessions=comparison.baseline.total_sessions
            )
            
            logger.warning(
                "ANOMALY DETECTED",
                funnel_step=funnel_step,
                drop_percentage=drop_pct,
                sigma=sigma_value,
                current_rate=comparison.current.conversion_rate,
                baseline_rate=comparison.baseline.conversion_rate
            )
            
            return anomaly
            
        except Exception as e:
            logger.error("Anomaly detection failed", error=str(e), funnel_step=funnel_step)
            return None
    
    def _calculate_sigma(
        self,
        current_rate: float,
        baseline_rate: float,
        current_n: int,
        baseline_n: int
    ) -> float:
        """
        Calculate Z-score (sigma value) for significance testing
        
        Uses two-proportion z-test approximation
        
        Args:
            current_rate: Current conversion rate (%)
            baseline_rate: Baseline conversion rate (%)
            current_n: Current sample size
            baseline_n: Baseline sample size
            
        Returns:
            Absolute Z-score value
        """
        try:
            # Convert percentages to proportions
            p1 = current_rate / 100.0
            p2 = baseline_rate / 100.0
            
            # Pooled proportion
            p_pool = (p1 * current_n + p2 * baseline_n) / (current_n + baseline_n)
            
            # Standard error
            se = (p_pool * (1 - p_pool) * (1/current_n + 1/baseline_n)) ** 0.5
            
            # Avoid division by zero
            if se == 0:
                return 0.0
            
            # Z-score
            z = abs((p1 - p2) / se)
            
            return z
            
        except Exception as e:
            logger.error("Sigma calculation failed", error=str(e))
            return 0.0
    
    async def scan_all_funnel_steps(
        self,
        funnel_steps: List[str]
    ) -> List[Anomaly]:
        """
        Scan all funnel steps for anomalies
        
        Args:
            funnel_steps: List of funnel step names to scan
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        for step in funnel_steps:
            # Compare current period (LAST_24_HOURS = days 8-14, bug period)
            # against baseline period (LAST_7_DAYS = days 1-7, good period)
            anomaly = await self.detect_anomaly(
                step,
                current_period=MetricPeriod.LAST_24_HOURS,  # Maps to current/bug period
                baseline_period=MetricPeriod.LAST_7_DAYS    # Maps to baseline/good period
            )
            if anomaly:
                anomalies.append(anomaly)
        
        if anomalies:
            logger.warning(
                "Multiple anomalies detected in scan",
                count=len(anomalies),
                steps=[a.funnel_step for a in anomalies]
            )
        
        return anomalies

    def _generate_demo_anomalies(self) -> List[Anomaly]:
        """Generate demo anomalies matching the demo login app issues"""
        
        import time
        current_time = int(time.time() * 1000)
        
        # Generate anomalies matching demo login app bugs
        anomalies = [
            # Bug #1: API timeout too short (5s instead of 15s)
            Anomaly(
                funnel_step="login_complete",
                detected_at=current_time - 3600000,  # 1 hour ago
                current_conversion_rate=30.0,
                baseline_conversion_rate=65.0,
                drop_percentage=53.8,
                sigma_value=4.2,
                is_significant=True,
                current_sessions=300,
                baseline_sessions=650
            ),
            # Bug #2: Button positioning issue on mobile
            Anomaly(
                funnel_step="login_button_click",
                detected_at=current_time - 7200000,  # 2 hours ago
                current_conversion_rate=52.0,
                baseline_conversion_rate=87.0,
                drop_percentage=40.2,
                sigma_value=3.8,
                is_significant=True,
                current_sessions=520,
                baseline_sessions=870
            ),
            # Bug #3: No email validation causing form errors
            Anomaly(
                funnel_step="form_start",
                detected_at=current_time - 10800000,  # 3 hours ago
                current_conversion_rate=68.0,
                baseline_conversion_rate=82.0,
                drop_percentage=17.1,
                sigma_value=2.5,
                is_significant=True,
                current_sessions=680,
                baseline_sessions=820
            )
        ]
        
        logger.info(f"Generated {len(anomalies)} demo anomalies matching login app bugs")
        return anomalies


# Global anomaly detector instance
anomaly_detector = AnomalyDetector()
