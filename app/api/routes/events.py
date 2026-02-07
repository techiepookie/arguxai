"""Event ingestion API endpoints"""

from fastapi import APIRouter, HTTPException, status
from app.models.events import EventBatch, Event, EventIngestResponse
from app.core.dependencies import APIKeyDep
from app.services.event_ingestion import event_ingestion_service
from app.core.logging import logger

router = APIRouter()


@router.post("/ingest", response_model=EventIngestResponse)
async def ingest_events(
    batch: EventBatch,
    api_key: APIKeyDep
) -> EventIngestResponse:
    """
    Ingest a batch of user events
    
    Events are validated, deduplicated, and stored in Convex database.
    
    **Authentication**: Requires API key in Authorization header
    
    **Rate Limit**: 1000 events per batch
    
    **Example Request**:
    ```json
    {
      "events": [
        {
          "event_type": "page_view",
          "session_id": "sess_abc123",
          "timestamp": 1675890123456,
          "funnel_step": "signup_form",
          "device_type": "mobile",
          "country": "US",
          "app_version": "2.0.0"
        }
      ]
    }
    ```
    
    **Example Response**:
    ```json
    {
      "success": true,
      "events_ingested": 1,
      "events_rejected": 0,
      "message": "Successfully ingested 1 events, rejected 0 duplicates"
    }
    ```
    """
    try:
        logger.info(
            "Event ingestion request received",
            event_count=len(batch.events)
        )
        
        response = await event_ingestion_service.ingest_events(batch)
        
        if not response.success:
            logger.warning(
                "Event ingestion completed with errors",
                ingested=response.events_ingested,
                rejected=response.events_rejected
            )
        
        return response
        
    except Exception as e:
        logger.error("Event ingestion endpoint error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest events: {str(e)}"
        )


@router.post("/ingest/single", response_model=EventIngestResponse)
async def ingest_single_event(
    event: Event,
    api_key: APIKeyDep
) -> EventIngestResponse:
    """
    Ingest a single event
    
    Convenience endpoint for single event ingestion.
    For better performance, use batch endpoint.
    
    **Authentication**: Requires API key
    """
    try:
        logger.info(
            "Single event ingestion",
            event_type=event.event_type,
            session_id=event.session_id
        )
        
        response = await event_ingestion_service.ingest_single_event(event)
        return response
        
    except Exception as e:
        logger.error("Single event ingestion error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest event: {str(e)}"
        )
