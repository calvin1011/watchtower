# Commit Checklist

Commit before starting each new phase. Ensures a clean history and safe rollback points.

## Before Each Commit

1. All phase tasks are done
2. **Run `pytest -v` from `backend/` and ensure tests pass**
3. No lint errors: `ruff check backend/` (when available)
4. `.env` is not staged (it is gitignored)
5. `.env.example` reflects any new required keys

## Phase Commit Messages

| Phase | Message |
|-------|---------|
| 0 | `chore: initial docs, env template, and project structure` |
| 1 | `feat: database models and async connection` |
| 2 | `feat: FastAPI shell and health endpoint` |
| 3a | `feat: add blog scraper` |
| 3b | `feat: add review scraper` |
| 3c | `feat: add jobs scraper` |
| 3d | `feat: add website scraper` |
| 4 | `feat: Claude agent for competitive intel analysis` |
| 5 | `feat: intel pipeline and API routes` |
| 6 | `feat: email digest via Resend` |
| 7 | `feat: weekly scheduler for Monday digest` |
| 8 | `feat: dashboard with intel feed` |
| 9 | `feat: competitor and digest pages` |
| 10 | `chore: Docker Compose and production readiness` |

## Commit Command

```bash
git add -A
git status   # verify .env is not included
git commit -m "feat: <phase message>"
```
