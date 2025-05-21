FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && pip install poetry \
  && poetry config virtualenvs.create false \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app
COPY poetry.lock* /app/
RUN poetry install --no-root

COPY .env /app/.env
COPY . /app

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --reload --host 0.0.0.0 --port 80"]

