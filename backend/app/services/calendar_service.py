import os
import json
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from app.core.config import settings
from supabase import create_client, Client

# In-memory store for PKCE verifiers (keyed by specialist_id)
_pkce_store = {}

class CalendarService:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        self.client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

    def get_supabase(self) -> Client:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def get_auth_url(self, specialist_id: str):
        # Generate PKCE code verifier and challenge
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).rstrip(b'=').decode('utf-8')

        # Store verifier in memory
        _pkce_store[specialist_id] = code_verifier

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=specialist_id,
            prompt='consent',
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )
        return auth_url

    async def exchange_code_for_tokens(self, code: str, specialist_id: str):
        # Get stored code verifier
        code_verifier = _pkce_store.pop(specialist_id, None)

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        import os
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        
        if code_verifier:
            flow.fetch_token(code=code, code_verifier=code_verifier)
        else:
            flow.fetch_token(code=code)

        credentials = flow.credentials

        # Store tokens in Supabase
        supabase = self.get_supabase()
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": list(credentials.scopes) if credentials.scopes else []
        }

        # Look up the specialist's client_id from users table
        user_res = supabase.table("users").select("client_id").eq("id", specialist_id).execute()
        if user_res.data:
            client_id = user_res.data[0]["client_id"]
        else:
            client_id = specialist_id
        
        # Check if already exists and update, otherwise insert
        existing = supabase.table("integrations").select("id").eq("client_id", client_id).eq("crm_type", "google_calendar").execute()
        if existing.data:
            supabase.table("integrations").update({
                "auth_token_encrypted": json.dumps(token_data),
                "is_active": True,
                "mcp_server_url": specialist_id  # Store specialist_id here for reference
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("integrations").insert({
                "client_id": client_id,
                "crm_type": "google_calendar",
                "auth_token_encrypted": json.dumps(token_data),
                "mcp_server_url": specialist_id,
                "is_active": True
            }).execute()

    def _get_credentials(self, specialist_id: str):
        supabase = self.get_supabase()
        res = supabase.table("integrations").select("*").eq("mcp_server_url", specialist_id).eq("crm_type", "google_calendar").execute()
        if not res.data:
            res = supabase.table("integrations").select("*").eq("client_id", specialist_id).eq("crm_type", "google_calendar").execute()
            
        if not res.data:
            raise Exception("No Google Calendar credentials found")

        db_row = res.data[0]
        token_data = json.loads(db_row["auth_token_encrypted"])
        credentials = google.oauth2.credentials.Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes")
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Update stored token
            token_data["token"] = credentials.token
            supabase.table("integrations").update({
                "auth_token_encrypted": json.dumps(token_data)
            }).eq("id", db_row["id"]).execute()

        return credentials

    async def get_available_slots(self, specialist_id: str):
        try:
            credentials = self._get_credentials(specialist_id)
            service = build('calendar', 'v3', credentials=credentials)

            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=7)).isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            busy_times = [(e['start'].get('dateTime', ''), e['end'].get('dateTime', ''))
                         for e in events_result.get('items', [])]

            slots = []
            current = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            end_date = now + timedelta(days=7)

            while current < end_date:
                if current.weekday() < 5 and 9 <= current.hour < 18:
                    slot_end = current + timedelta(minutes=30)
                    slot_start_str = current.isoformat() + 'Z'
                    slot_end_str = slot_end.isoformat() + 'Z'

                    is_busy = any(
                        busy_start <= slot_start_str < busy_end
                        for busy_start, busy_end in busy_times
                        if busy_start and busy_end
                    )

                    if not is_busy:
                        slots.append({
                            "start": slot_start_str,
                            "end": slot_end_str,
                            "specialist_id": specialist_id
                        })

                current += timedelta(minutes=30)

            return slots[:20]
        except Exception as e:
            print(f"Get slots error: {e}")
            return []

    async def book_appointment(self, specialist_id: str, slot_start: str, slot_end: str,
                               user_name: str, user_email: str, issue_summary: str):
        try:
            credentials = self._get_credentials(specialist_id)
            service = build('calendar', 'v3', credentials=credentials)

            event = {
                'summary': f'Support Call - {user_name}',
                'description': f'Issue: {issue_summary}\nCustomer: {user_email}',
                'start': {'dateTime': slot_start, 'timeZone': 'Asia/Kolkata'},
                'end': {'dateTime': slot_end, 'timeZone': 'Asia/Kolkata'},
                'attendees': [{'email': user_email}],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'voicera-{specialist_id[:8]}-{int(__import__("time").time())}',
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }

            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            meet_link = None
            if 'conferenceData' in created_event:
                entry_points = created_event['conferenceData'].get('entryPoints', [])
                for ep in entry_points:
                    if ep.get('entryPointType') == 'video':
                        meet_link = ep.get('uri')
                        break

            return {
                'event_id': created_event.get('id'),
                'meet_link': meet_link,
                'event_link': created_event.get('htmlLink')
            }
        except Exception as e:
            print(f"Book appointment error: {e}")
            raise

calendar_service = CalendarService()
