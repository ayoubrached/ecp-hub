from typing import List, Dict
from google.cloud import firestore
from datetime import datetime


def _client() -> firestore.Client:
  return firestore.Client()


def save_events(events_data: List[Dict]) -> int:
  """Persist a list of event dicts to Firestore collection `events`. Returns count saved.

  Expected keys per event: event_date, start_time, end_time, event_name, notes, location_id, guest_count, valets_needed
  """
  db = _client()
  batch = db.batch()
  col = db.collection('events')
  count = 0
  for ev in events_data:
    doc = col.document()  # auto-id
    payload = {
      'event_date': ev.get('event_date', ''),
      'start_time': ev.get('start_time', ''),
      'end_time': ev.get('end_time', ''),
      'event_name': ev.get('event_name', ''),
      'notes': ev.get('notes', ''),
      'location_id': ev.get('location_id', ''),
      'guest_count': ev.get('guest_count', ''),
      'valets_needed': ev.get('valets_needed', ''),
      'createdAt': firestore.SERVER_TIMESTAMP,
    }
    batch.set(doc, payload)
    count += 1
  if count:
    batch.commit()
  return count


def get_events() -> List[Dict]:
  """Retrieve all events ordered by event_date then createdAt."""
  db = _client()
  col = db.collection('events')
  # Order by event_date as string (YYYY-MM-DD) then createdAt
  qs = col.order_by('event_date').order_by('createdAt').stream()
  items: List[Dict] = []
  for doc in qs:
    d = doc.to_dict()
    d['id'] = doc.id
    items.append(d)
  return items


