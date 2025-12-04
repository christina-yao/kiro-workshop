from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from models import Event, EventCreate, EventUpdate
from database import db_client
from typing import List
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Events API",
    version="1.0.0",
    description="REST API for managing events with DynamoDB"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=3600,
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )

@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate):
    try:
        logger.info(f"Creating event: {event.title}")
        created_event = db_client.create_event(event.model_dump())
        return created_event
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create event")

@app.get("/events", response_model=List[Event])
def list_events():
    try:
        logger.info("Listing all events")
        events = db_client.list_events()
        return events
    except Exception as e:
        logger.error(f"Error listing events: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve events")

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    try:
        logger.info(f"Getting event: {event_id}")
        event = db_client.get_event(event_id)
        if not event:
            logger.warning(f"Event not found: {event_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {event_id} not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve event")

@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    try:
        logger.info(f"Updating event: {event_id}")
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            logger.warning(f"Event not found for update: {event_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {event_id} not found")
        
        update_data = {k: v for k, v in event_update.model_dump().items() if v is not None}
        if not update_data:
            logger.warning(f"No fields to update for event: {event_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        
        updated_event = db_client.update_event(event_id, update_data)
        return updated_event
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error updating event {event_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update event")

@app.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str):
    try:
        logger.info(f"Deleting event: {event_id}")
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            logger.warning(f"Event not found for deletion: {event_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {event_id} not found")
        
        db_client.delete_event(event_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete event")

# Lambda handler
handler = Mangum(app, lifespan="off")
