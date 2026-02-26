# Watchtower Build Phases

Detailed phase document for building the HappyCo Competitive Intelligence Agent. Each phase ends with a commit checkpoint before starting the next.

## Testing Requirement

**Every phase must include unit tests for critical features. Tests must pass before moving forward.** See [TESTING.md](TESTING.md) for how to run tests and add new ones.

---

## Phase 0: Project Foundation

**Goal:** Repo structure, docs, env template, Supabase schema.

**Tasks:**
- [x] README.md
- [x] .env.example
- [x] docs/SETUP.md, docs/ARCHITECTURE.md
- [x] Supabase project created
- [x] Run SQL schema in Supabase (provided in SETUP.md; includes RLS and policies)

**Commit:** `chore: initial docs, env template, and project structure`

---

## Phase 1: Database Layer

**Goal:** PostgreSQL + pgvector models and async connection.

**Tasks:**
- [x] `backend/models.py` - IntelItem, Digest, Competitor models
- [x] All SQL migrations must include RLS and policies (see SETUP.md)
- [x] `backend/database.py` - Async SQLAlchemy + pgvector
- [x] `backend/requirements.txt` - Dependencies

**Key files:**
- `IntelItem`: competitor, signal_type, threat_level, summary, embedding (vector), etc.
- `Digest`: week_of, content (JSON), sent_at, recipient
- `Competitor`: config table for tracked competitors (optional; can be config-based)

**Tests:** `backend/tests/test_models.py`, `test_database.py` (run `pytest -v` from backend)

**Commit:** `feat: database models and async connection`

---

## Phase 2: FastAPI Shell

**Goal:** Minimal API with health check and routing structure.

**Tasks:**
- [x] `backend/main.py` - FastAPI app entry
- [x] `backend/routes/health.py` - GET /health
- [x] `backend/config.py` - Settings from env (pydantic-settings)

**Commit:** `feat: FastAPI shell and health endpoint`

---

## Phase 3: Scrapers (Simplest First)

**Goal:** Data collection from competitor sources.

**Order:**
1. `backend/scrapers/blog_scraper.py` - HTTP fetch competitor blog/news
2. `backend/scrapers/review_scraper.py` - SerpAPI G2/Capterra
3. `backend/scrapers/jobs_scraper.py` - SerpAPI Jobs
4. `backend/scrapers/website_scraper.py` - Playwright (last, most complex)

**Tasks per scraper:**
- Fetch data
- Return structured dicts (title, url, snippet, date)
- Handle rate limits and errors

**Commit after each scraper:** `feat: add {blog|review|jobs|website} scraper`

---

## Phase 4: AI Agent

**Goal:** Claude-powered analysis of scraped data into intel.

**Tasks:**
- [x] `backend/agent.py` - System prompt, Claude API call
- [x] Input: raw scraped data
- [x] Output: JSON with summary, threat_level, threat_reason, happyco_response, signal_type, confidence
- [x] Use HappyCo context: Joy AI, 5.5M units, 2.7-day turns, centralized maintenance, plugin marketplace

**Tests:** `backend/tests/test_agent.py` (run `pytest -v` from backend)

**Commit:** `feat: Claude agent for competitive intel analysis`

---

## Phase 5: Intel Pipeline

**Goal:** Scrape -> Analyze -> Store flow.

**Tasks:**
- [ ] `backend/services/intel_service.py` - Orchestrate scrape + agent + DB write
- [ ] `backend/routes/intel.py` - GET /intel, GET /intel/{competitor}, GET /intel/signals/{type}
- [ ] Optional: Generate embeddings (OpenAI) for pgvector semantic search

**Commit:** `feat: intel pipeline and API routes`

---

## Phase 6: Email Digest

**Goal:** Assemble and send Monday morning briefing via Resend.

**Tasks:**
- [ ] `backend/digest.py` - Build digest from intel, format for email
- [ ] `backend/routes/digest.py` - POST /digest/send, GET /digest/history
- [ ] Group by threat level, include happyco_response per item

**Commit:** `feat: email digest via Resend`

---

## Phase 7: Scheduler

**Goal:** Automated weekly run every Monday 7:00 AM.

**Tasks:**
- [ ] `backend/scheduler.py` - APScheduler cron job
- [ ] Job: scrape_all -> analyze -> store -> send_digest

**Commit:** `feat: weekly scheduler for Monday digest`

---

## Phase 8: Frontend - Dashboard

**Goal:** Next.js 14 dashboard with intel feed.

**Tasks:**
- [ ] `frontend/` - Next.js 14 App Router, Tailwind, shadcn/ui
- [ ] `components/IntelFeed.tsx` - Live intel cards
- [ ] `components/ThreatBadge.tsx` - HIGH / MEDIUM / LOW
- [ ] `app/page.tsx` - Dashboard home

**Commit:** `feat: dashboard with intel feed`

---

## Phase 9: Frontend - Competitor & Digest Pages

**Goal:** Per-competitor view and digest history.

**Tasks:**
- [ ] `app/competitors/[slug]/page.tsx` - Deep dive per competitor
- [ ] `app/digest/page.tsx` - Past digests
- [ ] `components/CompetitorCard.tsx`, `components/DigestPreview.tsx`

**Commit:** `feat: competitor and digest pages`

---

## Phase 10: Docker & Polish

**Goal:** One-command run, env validation, error handling.

**Tasks:**
- [ ] `docker-compose.yml` - backend, frontend, db (or Supabase external)
- [ ] `backend/Dockerfile`, `frontend/Dockerfile`
- [ ] Startup checks for required env vars
- [ ] README update with Docker instructions

**Commit:** `chore: Docker Compose and production readiness`

---

## Phase 11: End-to-End & Loom

**Goal:** Full run, Loom recording.

**Tasks:**
- [ ] End-to-end test: manual scrape -> verify intel in DB -> trigger digest
- [ ] Record 3–5 min Loom walking through product
- [ ] Email submission to jindou@happy.co

---

## HappyCo Data Signals (Agent Context)

| HappyCo Signal | Agent Behavior |
|----------------|----------------|
| Common maintenance complaint types | Monitors competitor marketing for those pain points |
| 11-pt renewal gap (resident satisfaction) | Flags competitor retention-focused content |
| 2.7–5.7 day unit turn benchmarks | Tracks competitor turn-time claims |
| Centralized maintenance differentiator | Alerts on competitor centralization messaging |
| Open API / Plugin marketplace | Monitors competitor integration announcements |

---

## Commit Checklist Summary

Before starting each new phase, ensure:

1. All phase tasks are complete
2. No lint errors
3. `.env.example` is up to date
4. `.gitignore` is updated with any new paths that shouldn't be committed
5. Run `git add -A && git status` and commit with the phase message
