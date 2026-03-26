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

## ⚙️ Setup

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Configure environment variables
5. Run migrations
6. Start server

## 🔧 TODO

- Add Telegram bot integration
- Improve AI recommendations
- Add filters (price, year, mileage)