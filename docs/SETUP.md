# Watchtower Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- Supabase account
- API keys for Anthropic, SerpAPI, Resend

---

## 1. Clone and Install

```bash
cd watchtower
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 2. Supabase Database

### Create Project

1. Go to [supabase.com](https://supabase.com) and create a project
2. Wait for the database to provision

### Run Schema

**Convention:** Every SQL migration for Watchtower must enable RLS (Row Level Security) and define policies. This applies to schema creation and any future migrations.

In Supabase Dashboard: **SQL Editor** > New query. Paste and run:

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Intel items (competitive intelligence records)
CREATE TABLE intel_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor VARCHAR(100) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    threat_level VARCHAR(20) NOT NULL CHECK (threat_level IN ('HIGH', 'MEDIUM', 'LOW')),
    threat_reason TEXT NOT NULL,
    summary TEXT NOT NULL,
    happyco_response TEXT NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    source_url TEXT,
    raw_content TEXT,
    embedding vector(1536),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for common queries
CREATE INDEX idx_intel_competitor ON intel_items(competitor);
CREATE INDEX idx_intel_threat_level ON intel_items(threat_level);
CREATE INDEX idx_intel_detected_at ON intel_items(detected_at DESC);
CREATE INDEX idx_intel_signal_type ON intel_items(signal_type);

-- Semantic search index for pgvector (optional; skip if it fails on empty table)
CREATE INDEX idx_intel_embedding ON intel_items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Digests (sent Monday emails)
CREATE TABLE digests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_of DATE NOT NULL,
    content JSONB NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recipient VARCHAR(255) NOT NULL
);

CREATE INDEX idx_digests_week ON digests(week_of DESC);

-- RLS: Enable on all tables
ALTER TABLE intel_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE digests ENABLE ROW LEVEL SECURITY;

-- Policies: Service role has full access (backend uses postgres connection which bypasses RLS; these protect Supabase client usage)
CREATE POLICY "Service role full access on intel_items" ON intel_items
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on digests" ON digests
    FOR ALL USING (auth.role() = 'service_role');
```

### Get Connection String

1. Project Settings > Database
2. Connection string: **URI** (Transaction pooler for async)
3. Replace `[YOUR-PASSWORD]` with your database password
4. Use format: `postgresql+asyncpg://postgres.[ref]:[password]@...pooler.supabase.com:6543/postgres`

---

## 3. API Keys

### Anthropic (Claude)

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. **Account** > **API Keys** > **Create Key**
4. Copy the key (starts with `sk-ant-`)
5. Put in `.env` as `ANTHROPIC_API_KEY=sk-ant-...`

### SerpAPI (Reviews & Jobs)

1. Go to [serpapi.com](https://serpapi.com/)
2. Sign up for free tier (100 searches/month)
3. Dashboard shows your API key
4. Put in `.env` as `SERPAPI_KEY=...`

### Resend (Email)

1. Go to [resend.com](https://resend.com/)
2. Sign up, verify email
3. **API Keys** > **Create API Key**
4. For testing: use `onboarding@resend.dev` as sender (pre-verified)
5. Put in `.env` as `RESEND_API_KEY=re_...`
6. Set `DIGEST_RECIPIENT=your@email.com` for testing

---

## 4. Environment File

```bash
cp .env.example .env
```

Edit `.env` and fill every value. The app will fail on startup if required keys are missing.

---

## 5. Run Tests

```bash
cd backend
pytest -v
```

Unit tests run without DATABASE_URL. Integration tests require DATABASE_URL and network access. See [TESTING.md](TESTING.md).

---

## 6. Run Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Check: `http://localhost:8000/health`

---

## 7. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Check: `http://localhost:3000`

---

## 8. Docker (Optional)

```bash
docker-compose up
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ANTHROPIC_API_KEY not set` | Add key to `.env`, restart backend |
| `asyncpg` connection refused | Check DATABASE_URL format; use port 6543 for pooler |
| SerpAPI 401 | Verify API key, check quota |
| Resend bounce | Use verified domain or `onboarding@resend.dev` |
| pgvector not found | Run `CREATE EXTENSION vector;` in Supabase SQL Editor |
| idx_intel_embedding fails | Create after inserting intel: `CREATE INDEX idx_intel_embedding ON intel_items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);` |
