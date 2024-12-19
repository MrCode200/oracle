FROM python:3.13

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

WORKDIR /app/backend

COPY backend/pyproject.toml backend/poetry.lock* ./

# Install dependencies via Poetry
RUN poetry install --no-interaction --without dev --no-root && rm -rf $POETRY_CACHE_DIR

WORKDIR /app

COPY ./backend ./backend
COPY ./frontend ./frontend
COPY ./logs ./logs

WORKDIR /app/backend

RUN poetry install --no-dev