"""Metrics API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.metrics import FunnelMetrics, ComparisonMetrics, MetricPeriod
from app.services.metrics_calculator import metrics_calculator
from app.core.dependencies import APIKeyDep
from app.core.logging import logger

router = APIRouter()


@router.get("/{funnel_step}", response_model=FunnelMetrics)
async def get_funnel_metrics(
    funnel_step: str,
    period: MetricPeriod = Query(
        MetricPeriod.LAST_24_HOURS,
        description="Time period for metrics calculation"
    ),
    api_key: APIKeyDep = None
) -> FunnelMetrics:
    """
    Get conversion metrics for a specific funnel step
    
    **Parameters**:
    - `funnel_step`: Name of the funnel step (e.g., 'signup_form', 'otp_verification')
    - `period`: Time period (last_hour, last_24_hours, last_7_days, last_30_days)
    
    **Returns**: Funnel metrics including:
    - Total and completed sessions
    - Conversion and drop-off rates
    - Segmentation by country and device
    - Time spent on step statistics
    
    **Example**:
    ```
    GET /api/metrics/otp_verification?period=last_24_hours
    ```
    """
    try:
        logger.info(
            "Metrics request",
            funnel_step=funnel_step,
            period=period
        )
        
        metrics = await metrics_calculator.calculate_funnel_metrics(
            funnel_step=funnel_step,
            period=period
        )
        
        return metrics
        
    except Exception as e:
        logger.error("Failed to get funnel metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate metrics: {str(e)}"
        )


@router.get("/{funnel_step}/compare", response_model=ComparisonMetrics)
async def compare_funnel_metrics(
    funnel_step: str,
    current_period: MetricPeriod = Query(
        MetricPeriod.LAST_HOUR,
        description="Current period to analyze"
    ),
    baseline_period: MetricPeriod = Query(
        MetricPeriod.LAST_24_HOURS,
        description="Baseline period for comparison"
    ),
    api_key: APIKeyDep = None
) -> ComparisonMetrics:
    """
    Compare current funnel metrics with baseline to detect anomalies
    
    **Parameters**:
    - `funnel_step`: Funnel step to analyze
    - `current_period`: Recent period (default: last_hour)
    - `baseline_period`: Baseline for comparison (default: last_24_hours)
    
    **Returns**: Comparison including:
    - Current and baseline metrics
    - Conversion rate delta
    - Drop detection flag
    - Drop percentage if detected
    
    **Use Case**: Anomaly detection and alerting
    
    **Example**:
    ```
    GET /api/metrics/otp_verification/compare?current_period=last_hour&baseline_period=last_24_hours
    ```
    """
    try:
        logger.info(
            "Metrics comparison request",
            funnel_step=funnel_step,
            current_period=current_period,
            baseline_period=baseline_period
        )
        
        comparison = await metrics_calculator.compare_with_baseline(
            funnel_step=funnel_step,
            current_period=current_period,
            baseline_period=baseline_period
        )
        
        if comparison.drop_detected:
            logger.warning(
                "Drop detected in comparison",
                funnel_step=funnel_step,
                drop_percentage=comparison.drop_percentage
            )
        
        return comparison
        
    except Exception as e:
        logger.error("Failed to compare metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare metrics: {str(e)}"
        )
