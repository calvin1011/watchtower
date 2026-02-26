# Watchtower

HappyCo Competitive Intelligence Agent. Monitors AppFolio, Buildium, SmartRent, and Entrata so leadership wakes up every Monday with a competitive edge.

## The Pitch

HappyCo's Joy AI looks inward at work orders, technicians, and inspections. Watchtower looks outward at competitors, tracking product launches, hiring signals, and customer sentiment. Built in a weekend. Ready to run forever.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Runtime | Python 3.12 |
| Web Framework | FastAPI |
| AI | Claude API (claude-sonnet-4-20250514) |
| Scraping | Playwright (headless) |
| Reviews/Jobs | SerpAPI |
| Scheduling | APScheduler |
| Database | PostgreSQL + pgvector (Supabase) |
| ORM | SQLAlchemy 2.0 (async) |
| Frontend | Next.js 14 (App Router) |
| Styling | Tailwind CSS + shadcn/ui |
| Email | Resend API |
| Containerization | Docker + Docker Compose |

## Quick Start

1. Copy `.env.example` to `.env` and fill in your API keys (see [SETUP.md](docs/SETUP.md))
2. Run database migrations in Supabase (SQL provided in setup guide)
3. `docker-compose up` or run backend/frontend separately

## Project Structure

```
watchtower/
├── backend/           # FastAPI, scrapers, agent, scheduler
├── frontend/          # Next.js 14 dashboard
├── docs/              # Setup, architecture, phases
├── docker-compose.yml
└── .env.example
```

## Competitors Tracked

- AppFolio
- Buildium
- SmartRent
- Entrata

## Documentation

- [SETUP.md](docs/SETUP.md) - Environment setup and API keys
- [PHASES.md](docs/PHASES.md) - Build order and commit checkpoints
- [TESTING.md](docs/TESTING.md) - Unit tests; run before each phase commit
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical design

## License

Private. Built for HappyCo hiring assessment.
