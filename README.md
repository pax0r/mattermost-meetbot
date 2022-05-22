# Mattermost Meetbot Slash Command


This bot allows to create a Google Meet conference using Mattermost slash command (of your choice, I suggest `/meet`).
As there is no Google API for Meet, it uses Google Calendar to create a fake event with the Google Meet link.

Bot uses Redis to store refresh tokens.

## Installation

Bot needs to be hosted on your own server.
The easiest way is to use included `docker-compose.yml`, but it can be hosted like any other Python ASGI app.
Requirements are handled via poetry.

## Configuration

Meetbot requires a few configuration options available through env variables.

1) `ROOT_URL` - URL on which meetbot is hosted.
2) `GOOGLE_CREDENTIALS_PATH` - path to Google OAuth Client ID (https://developers.google.com/workspace/guides/create-credentials)
3) `MATTERMOST_TOKEN` - token for Mattermost slash command. Slash command should be configured to point to the `ROOT_URL` (https://docs.mattermost.com/integrations/cloud-slash-commands.html)
4) `REDIS_URL` - URL for the Redis instance (`redis://redis/` on included `docker-compose.yml`)

## Usage

After configuring Mattermost slash command just write it in any chat.
Any user needs to authorize API usage first, so after first message they will get a link to click and authorize bot.
After successful authorization, one can use the same slash command to get a meeting link.
Link is shared in the room where the command was issued.
