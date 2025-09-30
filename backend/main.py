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
  client_secret_path: str = "client_secret.json"
  token_path: str = "token.json"


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
async def unread_with_attachments(label: str = "Schedule Intake", client_secret_path: str = "client_secret.json", token_path: str = "token.json"):
  try:
    creds = get_credentials(client_secret_path=client_secret_path, token_path=token_path)
    service = build_gmail_service(creds)
    items = list_unread_with_attachments(service, label_name=label)
    return {"success": True, "count": len(items), "items": items}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-latest-schedule")
async def parse_latest_schedule(label: str = "Schedule Intake", client_secret_path: str = "client_secret.json", token_path: str = "token.json"):
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
    items = get_events()
    return {"success": True, "items": items}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


# To run locally: uvicorn main:app --reload --host 0.0.0.0 --port 8000

if __name__ == "__main__":
  import uvicorn
  import os as _os
  _port = int(_os.getenv("PORT", "8000"))
  uvicorn.run("main:app", host="0.0.0.0", port=_port)
