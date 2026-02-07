"""Event ingestion service with validation and deduplication"""

from typing import List, Set
from datetime import datetime, timedelta
from app.models.events import Event, EventBatch, EventIngestResponse
from app.integrations.sqlite_client import sqlite_client  # Changed from convex_client
from app.core.logging import logger


class EventIngestionService:
    """
    Service for ingesting and processing events from SDK
    
    Handles:
    - Event validation
    - Deduplication
    - Batch processing
    - Storage in Convex
    """
    
    def __init__(self):
        # In-memory deduplication cache (for demo)
        # In production, use Redis or similar
        self.recent_event_hashes: Set[str] = set()
        self.cache_ttl = timedelta(minutes=5)
        self.last_cache_cleanup = datetime.utcnow()
    
    def _generate_event_hash(self, event: Event) -> str:
        """
        Generate unique hash for event deduplication
        
        Combines session_id, event_type, and timestamp
        """
        return f"{event.session_id}:{event.event_type}:{event.timestamp}"
    
    def _is_duplicate(self, event: Event) -> bool:
        """
        Check if event is a duplicate
        
        Args:
            event: Event to check
            
        Returns:
            True if duplicate, False otherwise
        """
        event_hash = self._generate_event_hash(event)
        
        if event_hash in self.recent_event_hashes:
            logger.warning(
                "Duplicate event detected",
                session_id=event.session_id,
                event_type=event.event_type,
                timestamp=event.timestamp
            )
            return True
        
        # Add to cache
        self.recent_event_hashes.add(event_hash)
        return False
    
    def _cleanup_cache(self):
        """Clean up old entries from deduplication cache"""
        now = datetime.utcnow()
        
        if now - self.last_cache_cleanup > self.cache_ttl:
            # In a real implementation, we'd track timestamps
            # For demo, just clear periodically
            if len(self.recent_event_hashes) > 10000:
                self.recent_event_hashes.clear()
                logger.info("Deduplication cache cleared")
            
            self.last_cache_cleanup = now
    
    async def ingest_events(self, batch: EventBatch) -> EventIngestResponse:
        """
        Ingest a batch of events
        
        Args:
            batch: Batch of events to ingest
            
        Returns:
            Ingestion response with success/failure counts
        """
        try:
            # Clean up cache periodically
            self._cleanup_cache()
            
            ingested = 0
            rejected = 0
            errors = []
            
            # Filter out duplicates
            unique_events = []
            for event in batch.events:
                if self._is_duplicate(event):
                    rejected += 1
                    errors.append(f"Duplicate event: {event.session_id}:{event.event_type}")
                else:
                    unique_events.append(event)
            
            # Convert to dict for Convex
            event_dicts = [event.model_dump() for event in unique_events]
            
            # Batch insert to SQLite
            if event_dicts:
                event_ids = await sqlite_client.batch_insert_events(event_dicts)
                ingested = len(event_ids)
                
                logger.info(
                    "Events ingested successfully",
                    ingested=ingested,
                    rejected=rejected,
                    total=len(batch.events)
                )
            
            return EventIngestResponse(
                success=True,
                events_ingested=ingested,
                events_rejected=rejected,
                message=f"Successfully ingested {ingested} events, rejected {rejected} duplicates",
                errors=errors if rejected > 0 else []
            )
            
        except Exception as e:
            logger.error("Event ingestion failed", error=str(e))
            return EventIngestResponse(
                success=False,
                events_ingested=0,
                events_rejected=len(batch.events),
                message=f"Ingestion failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def ingest_single_event(self, event: Event) -> EventIngestResponse:
        """
        Ingest a single event
        
        Args:
            event: Event to ingest
            
        Returns:
            Ingestion response
        """
        batch = EventBatch(events=[event])
        return await self.ingest_events(batch)


# Global service instance
event_ingestion_service = EventIngestionService()
