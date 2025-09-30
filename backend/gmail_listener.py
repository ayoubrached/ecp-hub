import os
import json
import time
from typing import Optional, List, Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

GMAIL_SCOPES = [
  "https://www.googleapis.com/auth/gmail.readonly",
]


def get_credentials(client_secret_path: str = "/secrets/client_secret_json", token_path: str = "/secrets/token_json") -> Credentials:
  """Load OAuth user credentials; run consent flow if missing/expired, then save token.json."""
  creds: Optional[Credentials] = None
  if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, scopes=GMAIL_SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes=GMAIL_SCOPES)
      creds = flow.run_local_server(port=0)
    with open(token_path, "w") as f:
      f.write(creds.to_json())

  return creds


def build_gmail_service(creds: Credentials):
  return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _find_label_id(gmail_service, label_name: str) -> Optional[str]:
  labels_resp = gmail_service.users().labels().list(userId="me").execute()
  for label in labels_resp.get("labels", []):
    if label.get("name") == label_name:
      return label.get("id")
  return None


def _extract_header(headers: List[Dict[str, str]], name: str) -> Optional[str]:
  for h in headers:
    if h.get("name") == name:
      return h.get("value")
  return None


def _count_attachments(payload: Dict) -> int:
  count = 0
  parts = payload.get("parts", []) or []
  stack = list(parts)
  while stack:
    p = stack.pop()
    if p.get("filename"):
      count += 1
    subparts = p.get("parts") or []
    stack.extend(subparts)
  return count


def _collect_attachment_parts(payload: Dict) -> List[Dict]:
  parts = payload.get("parts", []) or []
  out: List[Dict] = []
  stack = list(parts)
  while stack:
    p = stack.pop()
    if p.get("filename") and p.get("body", {}).get("attachmentId"):
      out.append(p)
    subparts = p.get("parts") or []
    stack.extend(subparts)
  return out


def list_unread_with_attachments(gmail_service, label_name: str = "Schedule Intake", max_results: int = 50) -> List[Dict]:
  label_id = _find_label_id(gmail_service, label_name)
  if not label_id:
    raise RuntimeError(f"Gmail label not found: {label_name}")

  try:
    resp = gmail_service.users().messages().list(
      userId="me",
      labelIds=[label_id],
      q="is:unread has:attachment",
      maxResults=max_results,
    ).execute()
  except HttpError as e:
    raise RuntimeError(f"Failed to list messages: {e}")

  messages = resp.get("messages", [])
  if not messages:
    return []

  results: List[Dict] = []
  for m in messages:
    mid = m.get("id")
    mfull = gmail_service.users().messages().get(
      userId="me", id=mid, format="full"
    ).execute()
    payload = mfull.get("payload", {})
    headers = payload.get("headers", [])
    results.append({
      "id": mid,
      "snippet": mfull.get("snippet"),
      "subject": _extract_header(headers, "Subject"),
      "from": _extract_header(headers, "From"),
      "date": _extract_header(headers, "Date"),
      "attachment_count": _count_attachments(payload),
    })

  return results


def fetch_first_unread_attachment_bytes(gmail_service, label_name: str = "Schedule Intake") -> Dict:
  """Return dict with filename and bytes for the first unread message's first attachment."""
  items = list_unread_with_attachments(gmail_service, label_name=label_name, max_results=1)
  if not items:
    raise RuntimeError("No unread schedule emails with attachments found")
  mid = items[0]["id"]
  mfull = gmail_service.users().messages().get(userId="me", id=mid, format="full").execute()
  payload = mfull.get("payload", {})
  attachments = _collect_attachment_parts(payload)
  if not attachments:
    raise RuntimeError("No attachments found on the latest unread schedule email")
  first = attachments[0]
  att_id = first.get("body", {}).get("attachmentId")
  fname = first.get("filename") or "attachment"
  att = gmail_service.users().messages().attachments().get(userId="me", messageId=mid, id=att_id).execute()
  import base64
  data = base64.urlsafe_b64decode(att.get("data", ""))
  return {"filename": fname, "bytes": data}


def poll_schedule_intake(interval_seconds: int = 60, max_cycles: Optional[int] = None, client_secret_path: str = "/secrets/client_secret_json", token_path: str = "/secrets/token_json"):
  """Continuously poll the 'Schedule Intake' label for unread emails with attachments.

  For local dev/testing. In production, consider a scheduler or background worker.
  """
  creds = get_credentials(client_secret_path=client_secret_path, token_path=token_path)
  service = build_gmail_service(creds)
  cycles = 0
  while True:
    items = list_unread_with_attachments(service)
    print(f"[poll] found {len(items)} unread emails with attachments")
    for it in items:
      print(f" - {it['date']} | {it['from']} | {it['subject']} (attachments: {it['attachment_count']})")
    cycles += 1
    if max_cycles is not None and cycles >= max_cycles:
      break
    time.sleep(interval_seconds)
