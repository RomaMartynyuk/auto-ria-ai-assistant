# AI Car Finder

Backend service for searching cars from AUTO.RIA with AI-powered recommendations.

## 🚀 Features

- Search cars by query (e.g. "BMW under $8000")
- Parse data from AUTO.RIA
- Store search history
- AI-based recommendations
- Background processing with Celery

## 🛠️ Tech Stack

- Python
- Django & Django REST Framework
- PostgreSQL
- Redis
- Celery
- Playwright
- LLM (AI integration)

## 🧠 How it works

1. User sends a search query
2. Backend checks cache (Redis)
3. If not cached → Celery task is triggered
4. Playwright parses AUTO.RIA
5. Data is stored in PostgreSQL
6. AI analyzes results and suggests the best option

## ⚙️ Project Setup Guide

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional, for containerized run)

### Installation

```bash
git clone https://github.com/<your-org>/auto-ria-ai-assistant.git
cd auto-ria-ai-assistant
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
POSTGRES_DB=auto_ria
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
BOT_TOKEN=your_telegram_bot_token
```

Notes:
- For Docker Compose, use `POSTGRES_HOST=db`.
- `OPENAI_API_KEY` and `OPENROUTER_API_KEY` are used for AI recommendations.
- `BOT_TOKEN` is required only if you run the Telegram bot.

### Run Locally (without Docker)

Run migrations and start the API:

```bash
python manage.py migrate
python manage.py runserver
```

Start Celery worker in a separate terminal:

```bash
celery -A config worker --loglevel=info
```

Run Telegram bot (optional):

```bash
python bot/main.py
```

### Run with Docker Compose

```bash
docker compose up --build
```

This starts:
- Django API (`web`) on `http://localhost:8000`
- PostgreSQL (`db`)
- Redis (`redis`)
- Celery worker (`celery`)
- Telegram bot (`bot`)

### Build & Test

Basic project check:

```bash
python manage.py check
```

Run Django tests:

```bash
python manage.py test
```

### Troubleshooting

- Database connection errors: verify `POSTGRES_*` values and that PostgreSQL is running.
- Redis/Celery issues: ensure Redis is available on port `6379`.
- Bot does not start: check `BOT_TOKEN`.
- AI calls fail: confirm valid `OPENAI_API_KEY` or `OPENROUTER_API_KEY`.
