"""Direct test of anomaly detector"""
import asyncio
from app.services.anomaly_detector import anomaly_detector
from app.models.metrics import MetricPeriod

async def test():
    print("\n=== Testing Anomaly Detector Directly ===\n")
    
    anomaly = await anomaly_detector.detect_anomaly(
        funnel_step="login_button_click",
        current_period=MetricPeriod.LAST_24_HOURS,
        baseline_period=MetricPeriod.LAST_7_DAYS
    )
    
    if anomaly:
        print(f"✅ ANOMALY DETECTED!")
        print(f"   Drop: {anomaly.drop_percentage}%")
        print(f"   Baseline: {anomaly.baseline_conversion_rate}%")
        print(f"   Current: {anomaly.current_conversion_rate}%")
        print(f"   Sigma: {anomaly.sigma_value}")
        print(f"   Significant: {anomaly.is_significant}")
    else:
        print("❌ No anomaly detected")

asyncio.run(test())
