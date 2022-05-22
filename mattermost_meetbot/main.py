import fastapi
import redis as redis
from fastapi import HTTPException
from fastapi.params import Depends
from starlette.responses import RedirectResponse

from mattermost_meetbot.google_api import EventsApi, RedirectRequired
from mattermost_meetbot.settings import settings

app = fastapi.FastAPI()

redis = redis.Redis.from_url(settings.redis_url)


def mattermost_user(user_id: str, token: str) -> str:
    if token != settings.mattermost_token:
        raise HTTPException(status_code=403)
    return user_id


AUTH_REQUIRED = """
Authorization with Google required
==================================

Please click [here]({})
"""

LINK = "Here is your link: [{link}]({link})"


@app.get("/")
def root(user_id: str = Depends(mattermost_user)):
    api = EventsApi(redis)
    try:
        api.authorize(user_id)
        meet_link = api.get_meet_link()
        return {
            "response_type": "in_channel", "text": LINK.format(link=meet_link), 'username': 'Meetbot',
            'icon_url': 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Google_Meet_icon_%282020%29.svg'}
    except RedirectRequired as e:
        return {"response_type": "ephemeral", "text": AUTH_REQUIRED.format(e.redirect_url), 'username': 'Meetbot',
                'icon_url': 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Google_Meet_icon_%282020%29.svg'}


@app.get('/oauth2success')
def oauth2success():
    return "Success. You may close this window and go back to Mattermost."


@app.get('/oauth2callback')
def oauth2callback(request: fastapi.Request):
    api = EventsApi(redis)
    api.handle_redirect_response(str(request.url))
    return RedirectResponse('/oauth2success')

