# Watchtower Architecture

## Overview

Watchtower is a competitive intelligence agent that collects data from AppFolio, Buildium, SmartRent, and Entrata, analyzes it with Claude, and produces actionable intel. HappyCo's 5.5M unit operational data shapes what the agent watches for.

## Data Flow

```
Competitor Sites / G2 / Jobs
        |
        v
   [Scrapers] --> Raw content
        |
        v
   [Claude Agent] --> Structured Intel (JSON)
        |
        v
   [PostgreSQL + pgvector] --> Stored Intel
        |
        +--> [Resend] --> Monday Email Digest
        |
        +--> [FastAPI] --> Dashboard API
        |
        v
   [Next.js Dashboard] --> UI
```

## Components

### Backend (Python 3.12, FastAPI)

| Component | Responsibility |
|-----------|----------------|
| `main.py` | FastAPI app, CORS, router registration |
| `agent.py` | Claude API integration, system prompt, JSON parsing |
| `scrapers/` | Blog, review, jobs, website scrapers |
| `scheduler.py` | APScheduler, Monday 7:00 AM cron |
| `digest.py` | Assemble digest, Resend API |
| `models.py` | SQLAlchemy models |
| `database.py` | Async engine, session, pgvector |
| `routes/` | intel, digest, health endpoints |
| `config.py` | Pydantic settings from env |

### Frontend (Next.js 14)

| Component | Responsibility |
|-----------|----------------|
| `app/page.tsx` | Dashboard home, intel feed |
| `app/competitors/[slug]/page.tsx` | Per-competitor view |
| `app/digest/page.tsx` | Digest history |
| `components/` | IntelFeed, ThreatBadge, CompetitorCard, DigestPreview |

### Database (Supabase / PostgreSQL + pgvector)

| Table | Purpose |
|-------|---------|
| `intel_items` | Single pieces of competitive intel with embeddings |
| `digests` | Sent Monday digests (week, content, recipient) |

**SQL convention:** Every schema change or migration must include RLS (Row Level Security) and policies. Enable RLS on new tables and define policies that grant appropriate access (e.g. service role for backend).

## Security

- All secrets in environment variables, never in code
- `.env` gitignored; `.env.example` documents required keys
- API keys validated at startup; fail fast if missing
- No hardcoded credentials
- CORS configured for frontend origin only

## Competitor Config

```python
COMPETITORS = [
    {"name": "AppFolio", "website": "...", "blog": "...", "g2_slug": "...", ...},
    {"name": "Buildium", ...},
    {"name": "SmartRent", ...},
    {"name": "Entrata", ...},
]
```

## API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /intel | All intel, sorted |
| GET | /intel/{competitor} | Intel for one competitor |
| GET | /intel/signals/{type} | Filter by signal type |
| POST | /digest/send | Trigger digest send |
| GET | /digest/history | Past digests |

## Signal Types

- PRODUCT_LAUNCH
- PRICING_CHANGE
- MARKETING_SHIFT
- HIRING_SIGNAL
- CUSTOMER_COMPLAINT
- PARTNERSHIP

## Threat Levels

- **HIGH:** Direct attack on HappyCo core differentiators
- **MEDIUM:** Adjacent move affecting market position
- **LOW:** General news, not directly threatening
