from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Event, EventCreate, EventUpdate
from database import db_client
from typing import List

app = FastAPI(title="Events API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    try:
        created_event = db_client.create_event(event.model_dump())
        return created_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events", response_model=List[Event])
def list_events():
    try:
        events = db_client.list_events()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    try:
        event = db_client.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    try:
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        update_data = {k: v for k, v in event_update.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_event = db_client.update_event(event_id, update_data)
        return updated_event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: str):
    try:
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        db_client.delete_event(event_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
