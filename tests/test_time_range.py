"""Test time range helper"""
from app.utils.time_range_helper import get_database_time_range, get_baseline_and_current_ranges
from datetime import datetime

min_ts, max_ts = get_database_time_range()
print(f"Database time range:")
print(f"  Min: {min_ts} ({datetime.fromtimestamp(min_ts/1000)})")
print(f"  Max: {max_ts} ({datetime.fromtimestamp(max_ts/1000)})")
print(f"  Span: {(max_ts - min_ts) / (1000 * 60 * 60 * 24):.1f} days\n")

baseline_start, baseline_end, current_start, current_end = get_baseline_and_current_ranges()
print(f"Baseline period (days 1-7, ~90% conversion):")
print(f"  Start: {baseline_start} ({datetime.fromtimestamp(baseline_start/1000)})")
print(f"  End: {baseline_end} ({datetime.fromtimestamp(baseline_end/1000)})")
print(f"  Span: {(baseline_end - baseline_start) / (1000 * 60 * 60 * 24):.1f} days\n")

print(f"Current period (days 8-14, ~45% conversion - BUG PERIOD):")
print(f"  Start: {current_start} ({datetime.fromtimestamp(current_start/1000)})")
print(f"  End: {current_end} ({datetime.fromtimestamp(current_end/1000)})")
print(f"  Span: {(current_end - current_start) / (1000 * 60 * 60 * 24):.1f} days")
