from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gmail_listener import get_credentials, build_gmail_service, list_unread_with_attachments, poll_schedule_intake, fetch_first_unread_attachment_bytes
from ai_parser import parse_schedule_document
from database import save_events, get_events

app = FastAPI(title="ECP Hub Backend", version="0.1.0")


class AuthRequest(BaseModel):
  client_secret_path: str = "/secrets/client_secret_json"
  token_path: str = "/secrets/token_json"


@app.get("/")
async def root():
  return {"status": "ok"}


@app.post("/auth")
async def auth(req: AuthRequest):
  try:
    creds = get_credentials(client_secret_path=req.client_secret_path, token_path=req.token_path)
    service = build_gmail_service(creds)
    # quick sanity call
    profile = service.users().getProfile(userId="me").execute()
    return {"success": True, "emailAddress": profile.get("emailAddress")}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/emails/unread-with-attachments")
async def unread_with_attachments(label: str = "Schedule Intake", client_secret_path: str = "/secrets/client_secret_json", token_path: str = "/secrets/token_json"):
  try:
    creds = get_credentials(client_secret_path=client_secret_path, token_path=token_path)
    service = build_gmail_service(creds)
    items = list_unread_with_attachments(service, label_name=label)
    return {"success": True, "count": len(items), "items": items}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-latest-schedule")
async def parse_latest_schedule(label: str = "Schedule Intake", client_secret_path: str = "/secrets/client_secret_json", token_path: str = "/secrets/token_json"):
  try:
    creds = get_credentials(client_secret_path=client_secret_path, token_path=token_path)
    service = build_gmail_service(creds)
    attachment = fetch_first_unread_attachment_bytes(service, label_name=label)
    data = parse_schedule_document(attachment["bytes"], attachment["filename"])
    saved = save_events(data)
    return {"success": True, "items": data, "saved": saved}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
# Public API to fetch stored events
@app.get("/events")
async def list_events():
  try:
    raw = get_events()
    items = []
    for d in raw:
      items.append({
        "id": d.get("id"),
        "locationId": d.get("location_id"),
        "name": d.get("event_name", ""),
        "date": d.get("event_date", ""),
        "startTime": d.get("start_time", ""),
        "endTime": d.get("end_time", ""),
        "notes": d.get("notes", ""),
      })
    return {"success": True, "items": items}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


class CreateEventRequest(BaseModel):
  locationId: int
  eventName: str
  date: str
  startTime: str
  endTime: str
  notes: str = ""


@app.post("/events")
async def create_event(body: CreateEventRequest):
  try:
    # Normalize to storage shape used by save_events
    payload = [{
      'location_id': body.locationId,
      'event_name': body.eventName,
      'event_date': body.date,
      'start_time': body.startTime,
      'end_time': body.endTime,
      'notes': body.notes,
    }]
    saved = save_events(payload)
    return {"success": True, "saved": saved}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


# To run locally: uvicorn main:app --reload --host 0.0.0.0 --port 8000
