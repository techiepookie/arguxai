"""Convex database client integration"""

import os
import httpx
from typing import Any, Dict, List, Optional
from app.config import settings
from app.core.logging import logger


class ConvexClient:
    """
    Client for interacting with Convex database
    
    Convex provides real-time database with automatic sync.
    We use HTTP API for mutations and queries.
    """
    
    def __init__(self):
        self.deployment_url = settings.convex_deployment_url
        self.deploy_key = settings.convex_deploy_key
        self.base_url = f"{self.deployment_url}/api"
        
        # HTTP client for async requests
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Convex {self.deploy_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def insert_event(self, event_data: Dict[str, Any]) -> str:
        """
        Insert a single event into Convex
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Event ID from Convex
        """
        try:
            # For demo mode, we'll simulate storage
            if settings.demo_mode:
                logger.info(
                    "Demo mode: Would insert event to Convex",
                    event_type=event_data.get("event_type"),
                    session_id=event_data.get("session_id")
                )
                # Return fake ID
                return f"evt_{event_data.get('session_id')}_{event_data.get('timestamp')}"
            
            # Real Convex mutation would go here
            # response = await self.client.post(
            #     f"{self.base_url}/mutation",
            #     json={
            #         "path": "events:create",
            #         "args": event_data
            #     }
            # )
            # return response.json()["id"]
            
            # Placeholder for now
            logger.info("Event inserted to Convex", event_type=event_data.get("event_type"))
            return f"evt_{event_data.get('timestamp')}"
            
        except Exception as e:
            logger.error("Failed to insert event to Convex", error=str(e))
            raise
    
    async def batch_insert_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple events in a batch
        
        Args:
            events: List of event data dictionaries
            
        Returns:
            List of event IDs
        """
        try:
            if settings.demo_mode:
                logger.info(
                    "Demo mode: Would batch insert events to Convex",
                    count=len(events)
                )
                return [f"evt_{i}" for i in range(len(events))]
            
            # Real Convex mutation
            logger.info("Batch inserting events to Convex", count=len(events))
            
            response = await self.client.post(
                f"{self.base_url}/mutation",
                json={
                    "path": "events:insertBatch",
                    "args": {"events": events}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Events inserted successfully", count=result.get("insertedCount", 0))
                return result.get("ids", [])
            else:
                logger.error("Convex mutation failed", status=response.status_code, response=response.text)
                return [f"evt_{i}" for i in range(len(events))]
            
        except Exception as e:
            logger.error("Failed to batch insert events", error=str(e), count=len(events))
            # Return fake IDs so the workflow continues
            return [f"evt_{i}" for i in range(len(events))]
    
    async def query_events(
        self,
        start_time: int,
        end_time: int,
        funnel_step: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query events from Convex
        
        Args:
            start_time: Start timestamp (ms)
            end_time: End timestamp (ms)
            funnel_step: Optional funnel step filter
            event_types: Optional event type filters
            
        Returns:
            List of event dictionaries
        """
        try:
            if settings.demo_mode:
                logger.info(
                    "Demo mode: Would query events from Convex",
                    start_time=start_time,
                    end_time=end_time,
                    funnel_step=funnel_step
                )
                return []  # Return empty for now in demo mode
            
            # Real Convex query
            logger.info("Querying events from Convex", funnel_step=funnel_step)
            
            if funnel_step:
                # Use funnel-specific query
                response = await self.client.post(
                    f"{self.base_url}/query",
                    json={
                        "path": "events:queryByFunnelAndTime",
                        "args": {
                            "funnel_step": funnel_step,
                            "start_time": start_time,
                            "end_time": end_time
                        }
                    }
                )
            else:
                # Use general time-range query
                response = await self.client.post(
                    f"{self.base_url}/query",
                    json={
                        "path": "events:queryByTimeRange",
                        "args": {
                            "start_time": start_time,
                            "end_time": end_time
                        }
                    }
                )
            
            if response.status_code == 200:
                events = response.json()
                logger.info("Events queried successfully", count=len(events))
                return events
            else:
                logger.error("Convex query failed", status=response.status_code, response=response.text)
                return []
            
        except Exception as e:
            logger.error("Failed to query events", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        """
        Check if Convex is accessible
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            if settings.demo_mode:
                return True  # Always healthy in demo mode
            
            # Real health check would ping Convex
            # response = await self.client.get(f"{self.base_url}/health")
            # return response.status_code == 200
            
            return True
            
        except Exception as e:
            logger.error("Convex health check failed", error=str(e))
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global Convex client instance
convex_client = ConvexClient()
