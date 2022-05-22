import pathlib

from pydantic import AnyHttpUrl, BaseSettings, RedisDsn


class Settings(BaseSettings):
    root_url: AnyHttpUrl
    google_credentials_path: pathlib.Path
    mattermost_token: str
    redis_url: RedisDsn


settings = Settings()
