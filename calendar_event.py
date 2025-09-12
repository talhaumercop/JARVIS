from __future__ import print_function
import json
import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from agents import function_tool
SCOPES = ["https://www.googleapis.com/auth/calendar"]
EVENTS_FILE = "events.json"


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def save_event_id(name, event_id):
    """Save event_id under a user-friendly name in a JSON file."""
    data = {}
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            data = json.load(f)
    data[name] = event_id
    with open(EVENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_event_id(name):
    """Load event_id from JSON file."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            data = json.load(f)
        return data.get(name)
    return None


@function_tool
def manage_event(action, name=None, event_id=None, summary=None, description=None,
                 start_time=None, end_time=None, timezone="Asia/Karachi"):
    """Manage Google Calendar events: create, update, or delete."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    if action == "create":
        event = {
            "summary": summary or "New Event",
            "description": description or "",
            "start": {"dateTime": start_time, "timeZone": timezone},
            "end": {"dateTime": end_time, "timeZone": timezone},
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        print("✅ Event created:", event.get("htmlLink"))
        if name:
            save_event_id(name, event.get("id"))
            print(f"Event ID saved under '{name}'")
        return event.get("id")

    elif action == "update":
        if not event_id and name:
            event_id = load_event_id(name)
        if not event_id:
            raise ValueError("event_id or name required for update")
        event = service.events().get(calendarId="primary", eventId=event_id).execute()
        if summary: event["summary"] = summary
        if description: event["description"] = description
        if start_time: event["start"]["dateTime"] = start_time
        if end_time: event["end"]["dateTime"] = end_time
        event = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        print("✅ Event updated:", event.get("htmlLink"))
        return event.get("id")

    elif action == "delete":
        if not event_id and name:
            event_id = load_event_id(name)
        if not event_id:
            raise ValueError("event_id or name required for delete")
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        print("🗑️ Event deleted:", event_id)
        return None

    else:
        raise ValueError("Invalid action. Use 'create', 'update', or 'delete'.")

