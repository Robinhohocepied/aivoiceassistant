# Google Calendar Setup (Phase 4)

This guide connects the app to Google Calendar using a service account. Use it for prototype/pilot; later we can add OAuth for patient attendee invites if needed.

## 1) Create a Service Account
- In Google Cloud Console, create a project (or reuse an existing one).
- Enable the Google Calendar API.
- Create a Service Account and generate a JSON key.

## 2) Share the Clinic Calendar with the Service Account
- In Google Calendar UI (for the clinic calendar), share with the service account email (e.g., `my-sa@project.iam.gserviceaccount.com`) with at least “Make changes to events”.
- Copy the calendar ID (Settings for calendars → Integrate calendar → Calendar ID).

## 3) Configure Environment
- Set the following variables (in `.env` or your environment):
```
GOOGLE_CREDS_JSON=/absolute/path/to/service_account.json  # or paste inline JSON
GOOGLE_CALENDAR_ID=primary  # or the copied calendar ID
```
- Optionally, inline JSON works too:
```
GOOGLE_CREDS_JSON={"type":"service_account",...}
```
 - Or use base64-encoded JSON to avoid escaping:
 ```
 GOOGLE_CREDS_JSON_B64=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwiUHJvamVjdCI6ICJleGFtcGxlIiB9  # base64 of the JSON
 ```

## 4) Install Dependencies
- Install the required Python packages:
```
pip install google-api-python-client google-auth
```

## 5) How it’s used in code
- Provider selection prefers Google when `GOOGLE_CREDS_JSON` and `GOOGLE_CALENDAR_ID` are set and libraries are installed, else falls back to an in-memory provider for dev.
  - Code: `connectors/calendar/provider.py`
  - Google provider: `connectors/calendar/google.py`

## 6) Quick sanity test (dev)
- Start the app and send a message that yields `name`, `reason`, and `preferred_time`.
- If Google is configured, a real event should be created in the clinic calendar; otherwise, the in-memory provider will book locally.

## Troubleshooting
- 403 errors: ensure the service account email is shared on the target calendar.
- 404 calendar: verify `GOOGLE_CALENDAR_ID`.
- Invalid credentials: re-download JSON or correct `GOOGLE_CREDS_JSON` path.
