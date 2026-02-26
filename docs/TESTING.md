# Watchtower Testing

## Convention

Every phase must include unit tests for critical features. Tests must pass before moving to the next phase.

## Running Tests

From project root:

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

## Test Structure

| Directory | Purpose |
|-----------|---------|
| `backend/tests/test_models.py` | Model structure, column checks (no DB) |
| `backend/tests/test_database.py` | DB connection, insert/query (requires DATABASE_URL) |

## Requirements

- **Unit tests (test_models):** Run without DATABASE_URL. Always executed.
- **Integration tests (test_database):** Require DATABASE_URL in `.env` and network access to Supabase. Skipped if DATABASE_URL is not set.

## Before Each Phase Commit

1. Run `pytest -v` from `backend/`
2. Ensure all tests pass (or integration tests are skipped if no DB)
3. Add tests for new critical features in the phase

## Adding Tests for New Phases

- **Phase 2 (FastAPI):** Add `test_health.py` for GET /health
- **Phase 3 (Scrapers):** Add `test_blog_scraper.py` etc. with mocked HTTP
- **Phase 4 (Agent):** Add `test_agent.py` with mocked Claude
- **Phase 5+ (Routes):** Add `test_routes_intel.py` with TestClient
