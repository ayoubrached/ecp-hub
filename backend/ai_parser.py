import io
import json
import os
from typing import List, Dict

from vertexai import init as vertexai_init
from vertexai.generative_models import GenerativeModel

import fitz  # PyMuPDF
from docx import Document  # python-docx
from google.cloud import aiplatform
from google.genai import types as genai_types
from google.genai import Client as GenAIClient


SYSTEM_PROMPT = (
  "You are a meticulous data-entry assistant. Extract all valet events from the provided text. "
  "Return ONLY a JSON array (no prose) with objects of this shape: "
  "[{\"event_date\": \"YYYY-MM-DD\", \"start_time\": \"HH:MM AM/PM\", \"end_time\": \"HH:MM AM/PM\", \"event_name\": \"...\", \"guest_count\": \"...\", \"valets_needed\": \"...\"}] . "
  "If a field is missing in the text, put an empty string. Ensure valid JSON."
)


def _extract_text_from_pdf(data: bytes) -> str:
  with fitz.open(stream=data, filetype='pdf') as doc:
    return "\n".join(page.get_text() for page in doc)


def _extract_text_from_docx(data: bytes) -> str:
  bio = io.BytesIO(data)
  d = Document(bio)
  return "\n".join(p.text for p in d.paragraphs)


def _extract_text(data: bytes, filename: str) -> str:
  lower = filename.lower()
  if lower.endswith('.pdf'):
    return _extract_text_from_pdf(data)
  if lower.endswith('.docx'):
    return _extract_text_from_docx(data)
  # Fallback: treat as utf-8 text
  try:
    return data.decode('utf-8', errors='ignore')
  except Exception:
    return ''


def parse_schedule_document(file_bytes: bytes, filename: str) -> List[Dict]:
  """Extract text then call Vertex AI Gemini to parse events, returning JSON list."""
  text = _extract_text(file_bytes, filename)

  project_id = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GCLOUD_PROJECT')
  location = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
  if not project_id:
    raise RuntimeError('GOOGLE_CLOUD_PROJECT is not set in environment')

  # Initialize Vertex AI for the project and region
  aiplatform.init(project=project_id, location=location)
  vertexai_init(project=project_id, location='us-central1')

  # Use google-generativeai GenerativeModel
  model = GenerativeModel('gemini-2.5-pro')

  prompt = (
    f"{SYSTEM_PROMPT}\n\n"
    f"===== SOURCE TEXT START =====\n{text}\n===== SOURCE TEXT END =====\n"
  )

  resp = model.generate_content(prompt)
  raw_text = getattr(resp, 'text', None) or ''
  try:
    data = json.loads(raw_text)
    if not isinstance(data, list):
      raise ValueError('Model did not return a JSON array')
    return data
  except Exception:
    # Best effort: extract JSON substring
    start = raw_text.find('[')
    end = raw_text.rfind(']')
    if start != -1 and end != -1 and end > start:
      try:
        return json.loads(raw_text[start:end+1])
      except Exception:
        pass
    raise RuntimeError('Failed to parse model JSON response')
