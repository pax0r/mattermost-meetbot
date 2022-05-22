# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install curl -y \
    && curl -sSL https://install.python-poetry.org | python - --version 1.1.13

COPY pyproject.toml poetry.lock ./

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /usr/app

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY ./mattermost_meetbot ./mattermost_meetbot

EXPOSE 8000

CMD [ "poetry", "run", "uvicorn", "mattermost_meetbot.main:app", "--host", "0.0.0.0", "--port", "80"]
