"""Debug script to test anomaly detection directly"""
import asyncio
from app.services.metrics_calculator import metrics_calculator
from app.models.metrics import MetricPeriod

async def test_metrics():
    print("\n=== Testing Metrics Calculator with Real DB Data ===\n")
    
    # Test baseline period (days 1-7, should be ~90% conversion)
    print("📊 Querying BASELINE period (days 1-7):")
    baseline = await metrics_calculator.calculate_funnel_metrics(
        funnel_step="login_button_click",
        period=MetricPeriod.LAST_7_DAYS,
        use_db_range=True
    )
    print(f"  Total sessions: {baseline.total_sessions}")
    print(f"  Completed: {baseline.completed_sessions}")
    print(f"  Conversion rate: {baseline.conversion_rate}%")
    print(f"  Time range: {baseline.timestamp_start} - {baseline.timestamp_end}\n")
    
    # Test current period (days 8-14, should be ~45% conversion - THE BUG!)
    print("📊 Querying CURRENT period (days 8-14 - BUG PERIOD):")
    current = await metrics_calculator.calculate_funnel_metrics(
        funnel_step="login_button_click",
        period=MetricPeriod.LAST_24_HOURS,  # Will map to second half
        use_db_range=True
    )
    print(f"  Total sessions: {current.total_sessions}")
    print(f"  Completed: {current.completed_sessions}")
    print(f"  Conversion rate: {current.conversion_rate}%")
    print(f"  Time range: {current.timestamp_start} - {current.timestamp_end}\n")
    
    # Calculate drop
    if baseline.conversion_rate > 0 and current.conversion_rate > 0:
        drop = baseline.conversion_rate - current.conversion_rate
        print(f"🚨 CONVERSION DROP DETECTED: {drop:.1f} percentage points!")
        print(f"   From {baseline.conversion_rate}% → {current.conversion_rate}%")
    else:
        print("⚠️  No data found or zero conversion rates")

if __name__ == "__main__":
    asyncio.run(test_metrics())
