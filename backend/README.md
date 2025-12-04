# FastAPI Events Backend

REST API for managing events with DynamoDB storage.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

## Run

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

## API Endpoints

- `POST /events` - Create a new event
- `GET /events` - List all events
- `GET /events/{event_id}` - Get a specific event
- `PUT /events/{event_id}` - Update an event
- `DELETE /events/{event_id}` - Delete an event
