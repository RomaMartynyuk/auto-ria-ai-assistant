# AI Car Finder

AI Car Finder is a Django REST API and optional Telegram bot that discovers current car listings, stores them in PostgreSQL, and returns up to five recommendations close to a user's budget.

The project is designed as a portfolio-ready backend example: it combines a public API, background jobs, caching, browser automation, optional LLM integration, Docker, health checks, and automated tests.

## Features

- Search AUTO.RIA listings by budget with Playwright
- Prioritize cars within 70-100% of the requested budget
- Return deterministic recommendations even when no LLM is configured
- Optional Ollama, OpenAI, or OpenRouter recommendation provider
- Process parsing jobs asynchronously with Celery and Redis
- Cache search results in Redis
- Persist listings and search history in PostgreSQL
- Optional Telegram bot interface
- Docker health checks and persistent data volumes
- GitHub Actions test workflow

## Architecture

```text
User / Telegram bot
        |
        v
    Django REST API ------> Redis cache
        |                      |
        |                      v
        +-----------------> Celery worker
                               |
                               v
                      Playwright / AUTO.RIA
                               |
                               v
                           PostgreSQL
                               |
                               v
                    Optional LLM ranking
```

Redis database `0` is used as the Celery broker and Redis database `1` is used for Django caching.

## Quick Start with Docker

Requirements:

- Docker Desktop or Docker Engine with Compose
- At least 2 GB of free memory for Chromium and the application services

Create your local environment file:

```bash
cp .env.example .env
```

Start the API, PostgreSQL, Redis, and Celery:

```bash
docker compose up --build -d
```

Check service health:

```bash
curl http://localhost:8000/api/health/
```

Request recommendations:

```bash
curl "http://localhost:8000/api/recommend/?max_price=15000"
```

The first request for a new price range may return `202 Accepted` while Playwright collects listings:

```json
{
  "status": "processing",
  "message": "Data is being parsed. Please retry in a few seconds.",
  "task_id": "...",
  "price_range": {"min": 10500, "max": 15000}
}
```

Repeat the request after a few seconds. A ready response returns `200 OK` with up to five cars.

View logs when troubleshooting:

```bash
docker compose logs -f web celery
```

Stop the project without deleting data:

```bash
docker compose down
```

Avoid `docker compose down -v` unless you intentionally want to remove PostgreSQL and Redis data.

## AI Providers

The default `AI_PROVIDER=none` requires no API keys and uses deterministic ranking by budget proximity, year, and mileage. This is the easiest mode for evaluating the project.

### Ollama

Install Ollama on the host and download Mistral:

```bash
ollama pull mistral
ollama serve
```

Configure `.env`:

```env
AI_PROVIDER=ollama
AI_MODEL=mistral
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

On Linux, Docker Compose maps `host.docker.internal` through `host-gateway` for the web service.

### OpenAI

```env
AI_PROVIDER=openai
AI_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your-key
```

### OpenRouter

```env
AI_PROVIDER=openrouter
AI_MODEL=mistralai/mistral-7b-instruct
OPENROUTER_API_KEY=your-key
```

If an AI provider is unavailable or returns invalid JSON, the API logs the error and falls back to deterministic ranking instead of returning an empty result.

## Telegram Bot

Add a token from BotFather to `.env`:

```env
BOT_TOKEN=your-telegram-bot-token
```

Start the optional bot profile alongside the core services:

```bash
docker compose --profile bot up --build -d
```

The bot accepts a positive integer budget such as `15000`. It automatically polls the API while a new search is being processed.

## API

### `GET /`

Returns basic API navigation.

### `GET /api/health/`

Checks Django, PostgreSQL, and Redis connectivity.

### `GET /api/cars/`

Lists stored cars. Supported query parameters:

- `max_price`
- `min_year`
- `max_mileage`
- `brand`
- `ordering`: `price`, `-price`, `year`, `-year`, `mileage`, or `-mileage`

Example:

```bash
curl "http://localhost:8000/api/cars/?max_price=20000&min_year=2015&ordering=-year"
```

### `GET /api/recommend/`

Requires `max_price`. Supports the same optional filters as `/api/cars/` and returns up to five recommendations.

```bash
curl "http://localhost:8000/api/recommend/?max_price=41000&max_mileage=120000"
```

By default, candidates must cost at least 70% of `max_price`. Change `RECOMMENDATION_MIN_BUDGET_RATIO` in `.env` to adjust this behavior.

## Local Development without Docker

Create a virtual environment and install dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

For a lightweight local setup, use SQLite and a locally running Redis instance:

```env
USE_SQLITE=true
CACHE_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
API_BASE_URL=http://localhost:8000/api
```

Run migrations and services in separate terminals:

```bash
python manage.py migrate
python manage.py runserver
celery -A config worker --loglevel=info --concurrency=2
```

## Tests

Tests use SQLite and do not call AUTO.RIA or an external AI provider:

```bash
USE_SQLITE=true AI_PROVIDER=none python manage.py check
USE_SQLITE=true AI_PROVIDER=none python manage.py test
```

GitHub Actions runs the same checks on pushes to `main` and pull requests.

## Environment Reference

The complete configuration is documented in `.env.example`. Important settings include:

- `DJANGO_DEBUG` and `DJANGO_SECRET_KEY`
- `POSTGRES_*`
- `CACHE_URL` and `CELERY_BROKER_URL`
- `AI_PROVIDER`, `AI_MODEL`, and provider credentials
- `RECOMMENDATION_MIN_BUDGET_RATIO`
- `PARSER_RESULT_LIMIT` and `PLAYWRIGHT_HEADLESS`
- `BOT_TOKEN` and bot polling settings

For an internet-facing deployment, set `DJANGO_DEBUG=false`, use a strong unique `DJANGO_SECRET_KEY`, restrict `ALLOWED_HOSTS`, terminate HTTPS at a reverse proxy, and configure monitoring and backups.

## Known Limitations

- AUTO.RIA markup can change, requiring parser selector updates.
- Scraping availability depends on the source site's uptime and anti-bot policies.
- Celery result storage is intentionally disabled; clients poll the recommendation endpoint.
- This project is an educational portfolio application, not financial or purchasing advice.

Before deploying or using the scraper at scale, review and comply with AUTO.RIA's terms of service, robots policy, and applicable law.
