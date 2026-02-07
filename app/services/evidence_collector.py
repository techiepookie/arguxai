"""Evidence collection service for AI diagnosis"""

from typing import Dict, Any, List
from collections import defaultdict
from app.models.issues import DiagnosisEvidence
from app.models.events import EventType
from app.integrations.sqlite_client import sqlite_client  # Changed from convex_client
from app.core.logging import logger
from app.config import settings
import random


class EvidenceCollector:
    """
    Collect evidence about conversion issues for AI diagnosis
    
    Gathers:
    - Error patterns and frequencies
    - User behavior changes
    - Segment analysis
    - Session samples
    """
    
    async def collect_evidence(
        self,
        funnel_step: str,
        start_time: int,
        end_time: int
    ) -> DiagnosisEvidence:
        """
        Collect comprehensive evidence for a funnel step issue
        
        Args:
            funnel_step: Funnel step with the issue
            start_time: Start of analysis period (Unix ms)
            end_time: End of analysis period (Unix ms)
            
        Returns:
            Evidence object with all collected data
        """
        try:
            logger.info(
                "Collecting evidence",
                funnel_step=funnel_step,
                time_range_hours=(end_time - start_time) / (1000 * 60 * 60)
            )
            
            # Query events from SQLite
            events = await sqlite_client.query_events(
                start_time=start_time,
                end_time=end_time,
                funnel_step=funnel_step
            )
            
            # In demo mode or no events, generate realistic evidence
            if settings.demo_mode or len(events) == 0:
                return self._generate_demo_evidence(funnel_step)
            
            # Analyze real events
            return self._analyze_events(events)
            
        except Exception as e:
            logger.error("Evidence collection failed", error=str(e))
            return DiagnosisEvidence()
    
    def _generate_demo_evidence(self, funnel_step: str) -> DiagnosisEvidence:
        """Generate realistic demo evidence for testing"""
        
        # Different evidence patterns per funnel step
        evidence_templates = {
            "otp_verification": {
                "error_types": {
                    "network_timeout": 45,
                    "invalid_otp": 23,
                    "rate_limit_exceeded": 12,
                    "provider_error": 8
                },
                "top_errors": [
                    "Connection timeout after 30s waiting for Twilio response",
                    "Invalid OTP code entered (3+ attempts)",
                    "Rate limit exceeded: too many OTP requests from same number",
                    "Twilio API error: 429 Too Many Requests"
                ],
                "avg_retry_count": 2.3,
                "time_to_completion_change": 45.5,
                "affected_countries": ["IN", "PH", "BD"],
                "affected_devices": ["mobile"],
                "affected_versions": ["2.1.0", "2.1.1"],
                "struggling_session_ids": [
                    f"sess_demo_{i}" for i in range(5)
                ]
            },
            "signup_form": {
                "error_types": {
                    "validation_error": 34,
                    "network_error": 18,
                    "session_expired": 12
                },
                "top_errors": [
                    "Email validation failed: invalid format",
                    "Network request failed after 3 retries",
                    "Session expired - please refresh page"
                ],
                "avg_retry_count": 1.8,
                "time_to_completion_change": 22.3,
                "affected_countries": ["US", "UK"],
                "affected_devices": ["desktop"],
                "affected_versions": ["2.0.5"],
                "struggling_session_ids": [f"sess_demo_{i}" for i in range(3)]
            },
            "profile_creation": {
                "error_types": {
                    "image_upload_failed": 28,
                    "profile_save_error": 15,
                    "validation_failed": 10
                },
                "top_errors": [
                    "Image upload failed: file size exceeded 5MB",
                    "Failed to save profile: database timeout",
                    "Invalid phone number format for region"
                ],
                "avg_retry_count": 2.1,
                "time_to_completion_change": 38.7,
                "affected_countries": ["IN", "US"],
                "affected_devices": ["mobile", "desktop"],
                "affected_versions": ["2.1.0"],
                "struggling_session_ids": [f"sess_demo_{i}" for i in range(4)]
            }
        }
        
        # Get template or use default
        template = evidence_templates.get(funnel_step, evidence_templates["otp_verification"])
        
        return DiagnosisEvidence(**template)
    
    def _analyze_events(self, events: List[Dict[str, Any]]) -> DiagnosisEvidence:
        """Analyze real event data to collect evidence"""
        
        error_types = defaultdict(int)
        top_errors = []
        retry_counts = []
        
        countries = defaultdict(int)
        devices = defaultdict(int)
        versions = defaultdict(int)
        struggling_sessions = set()
        
        # Group by session
        sessions = defaultdict(list)
        for event in events:
            sessions[event['session_id']].append(event)
        
        # Analyze each session
        for session_id, session_events in sessions.items():
            has_error = False
            retry_count = 0
            
            for event in session_events:
                # Track errors
                if event.get('event_type') == EventType.ERROR:
                    error_type = event.get('error_type', 'unknown')
                    error_types[error_type] += 1
                    
                    error_msg = event.get('error_message', '')
                    if error_msg and error_msg not in top_errors:
                        top_errors.append(error_msg)
                    
                    has_error = True
                
                # Track retries
                if event.get('event_type') == EventType.RESEND_CLICK:
                    retry_count += 1
                
                # Track segments
                countries[event.get('country', 'unknown')] += 1
                devices[event.get('device_type', 'unknown')] += 1
                versions[event.get('app_version', 'unknown')] += 1
            
            if retry_count > 0:
                retry_counts.append(retry_count)
            
            if has_error or retry_count >= 2:
                struggling_sessions.add(session_id)
        
        # Calculate averages
        avg_retry = sum(retry_counts) / len(retry_counts) if retry_counts else 0
        
        # Get top affected segments
        affected_countries = [c for c, _ in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:3]]
        affected_devices = [d for d, _ in sorted(devices.items(), key=lambda x: x[1], reverse=True)[:2]]
        affected_versions = [v for v, _ in sorted(versions.items(), key=lambda x: x[1], reverse=True)[:3]]
        
        return DiagnosisEvidence(
            error_types=dict(error_types),
            top_errors=top_errors[:5],
            avg_retry_count=round(avg_retry, 1) if avg_retry > 0 else None,
            affected_countries=affected_countries,
            affected_devices=affected_devices,
            affected_versions=affected_versions,
            struggling_session_ids=list(struggling_sessions)[:10]
        )


# Global evidence collector instance
evidence_collector = EvidenceCollector()
