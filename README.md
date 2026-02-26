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
2. Run with Docker:
   ```bash
   docker-compose up --build
   ```
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000

Or run backend and frontend separately (see [SETUP.md](docs/SETUP.md)).

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

## CI/CD

- **CI** (`.github/workflows/ci.yml`): On every push/PR, runs backend pytest + ruff, frontend build + lint.
- **CD** (`.github/workflows/deploy.yml`): On push to `main`, deploys backend and/or frontend if configured.

### Enabling Deployments

1. **Repository variables** (Settings → Secrets and variables → Actions → Variables):
   - `DEPLOY_BACKEND`: set to `true` to deploy backend to Render
   - `DEPLOY_FRONTEND`: set to `true` to deploy frontend to Vercel
   - `NEXT_PUBLIC_API_URL`: production API URL (set in Vercel project env vars for frontend builds)

2. **Secrets** (Settings → Secrets and variables → Actions → Secrets):
   - **Backend (Render)**: `RENDER_DEPLOY_HOOK_URL` — from Render Dashboard → Your Service → Settings → Deploy Hook
   - **Frontend (Vercel)**: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` — from [Vercel](https://vercel.com/account/tokens) and `vercel link` locally

## Documentation

- [SETUP.md](docs/SETUP.md) - Environment setup and API keys
- [PHASES.md](docs/PHASES.md) - Build order and commit checkpoints
- [TESTING.md](docs/TESTING.md) - Unit tests; run before each phase commit
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical design

## License

Built for HappyCo hiring assessment.
