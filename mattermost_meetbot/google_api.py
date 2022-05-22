import json
import time
import urllib.parse
import uuid

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from redis.client import Redis

from mattermost_meetbot.settings import settings


class RedirectRequired(Exception):
    def __init__(self, redirect_url):
        self.redirect_url = redirect_url


class EventsApi:
    SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly"]
    TOKEN_TEMPLATE = 'mmm_google_token_{}'

    def __init__(self, redis: Redis, ):
        self.redis = redis
        self.creds = None

    def authorize(self, user_id: str):
        token = self.redis.get(self.TOKEN_TEMPLATE.format(user_id))
        creds = None
        if token:
            token = json.loads(token)
            creds = Credentials.from_authorized_user_info(token, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = self._get_flow()
                authorization_url, state = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true',
                    prompt='consent',
                    state=user_id
                )
                raise RedirectRequired(authorization_url)
        self.creds = creds

    def handle_redirect_response(self, authorization_response: str):
        flow = self._get_flow()
        flow.fetch_token(authorization_response=authorization_response)

        qs = urllib.parse.parse_qs(urllib.parse.urlparse(authorization_response).query)
        self.redis.set(self.TOKEN_TEMPLATE.format(qs['state'][0]), flow.credentials.to_json())

    def get_meet_link(self):
        if not self.creds:
            raise ValueError("Please call `self.authorize` first!")

        service = build('calendar', 'v3', credentials=self.creds)

        event = {
            'summary': 'mattermost-meetbot',
            'description': 'Event for getting the Meets Link',
            'start': {
                'dateTime': '2015-05-28T09:00:00+01:00',
                'timeZone': 'Europe/Warsaw',
            },
            'end': {
                'dateTime': '2015-05-28T09:00:00+01:00',
                'timeZone': 'Europe/Warsaw',
            },
            'conferenceData': {
                'createRequest': {'requestId': str(uuid.uuid4())}
            }
        }
        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()

        uri = None
        for entrypoint in event['conferenceData']['entryPoints']:
            if entrypoint['entryPointType'] == 'video':
                uri = entrypoint['uri']

        time.sleep(0.5)  # bad practice, better check if event is visible

        service.events().delete(calendarId='primary', eventId=event['id']).execute()

        return uri

    def _get_flow(self):
        flow = Flow.from_client_secrets_file(settings.google_credentials_path, self.SCOPES)
        flow.redirect_uri = urllib.parse.urljoin(settings.root_url, '/oauth2callback')
        return flow
