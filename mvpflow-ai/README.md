# MVPFlow AI

**Turn messy founder notes into a clear, buildable MVP plan.** Paste in raw customer notes and MVPFlow AI produces a structured execution package: requirements → MVP scope → architecture → Jira backlog → a three-layer quality evaluation → a founder-ready summary (and, optionally, a launch page to start validating demand).

> **What this is, honestly.** It started as a *workshop reference system*: a deterministic Python pipeline, so a live demo never depends on an API staying up. It now also has an **optional, real LLM integration** (Claude or Groq). Set a provider key and the whole pipeline runs live on *your* problem, in any domain. Leave it off and it uses the built-in templates (the ones the tests and the offline demo run on). The API, database, and auth code around it is real and useful, but treat the production parts as a *starting point*, not a finished product. The [Status](#status) table shows exactly what is verified.

![Version 1.0.0](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What it does

```text
Founder Notes / Customer Feedback
        ↓
AI-Assisted Research & Requirement Extraction
        ↓
MVP Scope Definition (in-scope / out-of-scope)
        ↓
Solution Architecture (components & data flow)
        ↓
Jira Backlog & Acceptance Criteria
        ↓
GitHub Branch / PR Implementation (human-gated draft PRs)
        ↓
Three-Layer Evaluation (quality / fit / reliability)
        ↓
Founder-Ready Delivery Summary
```

You hand it the messy input; it hands you back a plan you can act on the same day. In industry terms this is **spec-driven development** (the pattern behind GitHub Spec Kit and AWS Kiro), made founder-friendly: the plan is the spec that drives the build.

## Try it in 60 seconds (no API key needed)

The default mode is fully deterministic, so it runs offline with nothing but Python - ideal for a first look or a live demo.

```bash
git clone https://github.com/mrw-soumik/vibe-coding-engineered.git
cd vibe-coding-engineered/mvpflow-ai
pip install -r requirements.txt

# run the test suite (all green)
pytest -q

# generate a full MVP package from the sample notes, plus a launch page
python -m app.cli \
  --input examples/restaurant_founder_notes.txt \
  --output out.md --landing landing.html --domain restaurant
```

Open `out.md` for the plan and `landing.html` in any browser. Prefer the API? Run `uvicorn app.main:app --reload` and open `http://localhost:8000/docs`.

### Use it on your own startup

Swap in your own notes and domain:

```bash
python -m app.cli --input my_notes.txt --output my_plan.md --domain healthcare \
  --tickets-dir tickets
```

`--tickets-dir` writes each ticket as its own agent-ready Markdown file (user story + acceptance criteria + definition of done) plus a starter `AGENTS.md`, so you can hand a ticket straight to an AI coding agent. That is **spec-driven development**: write the spec once, then just tell the agent "implement `tickets/MVP-001.md`."

For the reusable, step-by-step process to apply this to any startup, see the take-home **[Founder Template](../FOUNDER_TEMPLATE.md)**.

Want to **build** it the way a real engineer does - tested, reviewed code in a real repo, not a black-box app? Hand a ticket to an AI coding agent (guided by `SKILL.md` / `AGENTS.md`), implement it with a test, and open a human-reviewed PR. The repo's **Workflow Automation** section scaffolds exactly that, and the **[hands-on lab](../workshop/LAB.md)** walks through plan → engineered build.

## Two layers: build the core first, add production when it earns its place

This repo deliberately shows **both halves of "advanced vibe coding"** - the workflow itself, and how a team would ship it - and keeps them distinct on purpose.

| Layer | What it is | Where it lives |
|---|---|---|
| **MVP core** (the workflow) | Turn a problem into a researched, scoped, ticketed plan | `app/core/`, `app/llm/`, `app/integrations/`, `app/utils/`, `app/models.py`, `app/constants.py` |
| **Production layer** (how to ship it) | The service + operational scaffolding around the core | `app/main.py` (API), `app/database.py`, `app/security.py`, `app/middleware.py`, `app/observability.py`, plus `tests/`, CI, `Dockerfile`, `alembic/` |
| **Interfaces** | Ways to drive the core | `app/cli.py`, `app/automation.py`, the API |

The MVP core runs with zero infrastructure (`python -m app.cli …`). Reach for a production piece only when a real need shows up: persistence when you must remember runs, auth when you expose the API, Docker/Postgres when you deploy, monitoring when you operate it. The repo shows you *how* each piece looks so adding it later is cheap - it does **not** mean every project needs all of it on day one.

## Using real AI (Claude or Groq)

By default the pipeline uses built-in templates, so it always runs offline. Turn on live generation and **every step is produced from your actual problem, in any domain**:

```bash
export USE_LLM=true
export ANTHROPIC_API_KEY=sk-ant-...     # preferred
# or - used automatically when no Anthropic key is set:
export GROQ_API_KEY=gsk_...
```

| Step | LLM-driven when enabled? |
|---|---|
| Requirements extraction | ✅ |
| Domain / market research | ✅ (LLM-only - skipped offline) |
| Solution options (3 → recommend the smallest useful MVP) | ✅ (LLM-only - skipped offline) |
| MVP scope · architecture · Jira tickets · evaluation | ✅ |

With the key **off**, research and solution options are skipped. The other steps fall back to the deterministic restaurant-demo templates (what the tests and offline demo use).

Provider notes:

- **Anthropic** adds adaptive thinking and web-search-backed research.
- **Groq** (OpenAI-compatible) returns structured JSON with no web search. Its free tier rate-limits hard, so the client retries with backoff and a full run can be slow.

Defaults: `LLM_MODEL=claude-opus-4-8`, `GROQ_MODEL=llama-3.3-70b-versatile`. Evaluation scores are calculated per layer, then averaged in code.

## Push to Jira and GitHub (optional, human-gated)

**Jira** - turn the generated backlog into real issues via the Jira Cloud REST API. Credentials are read from the environment only; never commit a token.

```bash
export JIRA_BASE_URL=https://yoursite.atlassian.net
export JIRA_EMAIL=you@example.com
export JIRA_API_TOKEN=...           # keep out of source control
export JIRA_PROJECT_KEY=WOR

python -m app.cli --input ... --output out.md --push-jira              # dry run (default - no writes)
python -m app.cli --input ... --output out.md --push-jira --jira-live  # creates Story issues for real
```

Tickets are created as `Story` issues with story points (field auto-discovered) and priority encoded as a label, to stay portable across Jira schemes.

**GitHub automation** - [`app/automation.py`](app/automation.py) runs the Jira→GitHub execution leg. For each ticket it finds the Jira issue, creates a branch named with the issue key, opens a **draft** PR pre-filled from the ticket, and moves the issue to *In Progress*. It **never merges** - a human reviews and merges every draft.

```bash
python -m app.automation --limit 1           # dry run (default): prints the plan, no changes
python -m app.automation --limit 1 --live    # needs `gh auth login` + the JIRA_* env above
```

## How output is evaluated

Every run is scored on three layers, each on a 1–5 scale, then averaged into an overall score:

| Layer | Question it answers |
|---|---|
| **Content quality** | Is the output useful and complete? |
| **Domain fit** | Does it fit the business context and its risks? |
| **System reliability** | Does the workflow behave consistently? |

The eval harness grades output against a golden rubric:

```bash
python eval/run_eval.py        # deterministic by default; set a key to grade live output
```

## API

Run `uvicorn app.main:app --reload`, then open the auto-generated Swagger UI at `/docs`.

| Method & path | Purpose |
|---|---|
| `POST /api/v1/workflow` | Run the workflow (body: `notes` + `domain`) |
| `GET /api/v1/executions` | List execution history |
| `GET /health` | Health check, incl. database connectivity |

JWT bearer auth, per-IP rate limiting (100 req / 60 s, configurable), and audit logging are built in.

```bash
curl -X POST http://localhost:8000/api/v1/workflow \
  -H "Content-Type: application/json" \
  -d '{"notes": "Restaurant owners waste time answering repeated questions...", "domain": "restaurant"}'
```

## Project layout

```text
mvpflow-ai/
├── app/
│   ├── core/            # The workflow pipeline (domain logic)
│   │   ├── workflow.py            # orchestrator
│   │   ├── requirements_extractor.py
│   │   ├── research.py            # domain/market research (LLM-only)
│   │   ├── solutions.py           # 3 options → recommend smallest MVP (LLM-only)
│   │   ├── mvp_scope.py · architecture.py · jira_ticket_generator.py
│   │   ├── evaluation.py · summary.py
│   │   └── landing.py             # self-contained launch page
│   ├── llm/             # Provider abstraction (Anthropic + Groq), AI code-draft
│   ├── integrations/    # jira.py (Jira Cloud REST), github.py (branch + draft PR)
│   ├── main.py          # FastAPI app (entrypoint: app.main:app)
│   ├── cli.py           # Command-line interface
│   ├── automation.py    # Jira → branch → draft PR → Jira orchestrator
│   ├── models.py · config.py · constants.py
│   └── database.py · security.py · middleware.py · observability.py
├── alembic/             # Database migrations
├── tests/               # 41 tests: workflow, API, auth, DB, LLM, Jira, landing, tickets
├── docs/                # CODEMAP + worked example
├── examples/ · prompts/ · scripts/
├── Dockerfile · docker-compose.yml · requirements.txt · .env.example
└── README.md · SKILL.md · AGENTS.md · SECURITY.md
```

A full file-by-file guide lives in **[docs/CODEMAP.md](docs/CODEMAP.md)**.

## Configuration

Everything is environment-driven - use a `.env` file in development (see **[.env.example](.env.example)** for the full template). The essentials:

| Variable(s) | Purpose |
|---|---|
| `USE_LLM`, `ANTHROPIC_API_KEY` / `GROQ_API_KEY` | Enable and route live AI generation |
| `DATABASE_URL` | SQLite by default; a PostgreSQL URL for production |
| `SECRET_KEY`, `ENABLE_JWT_AUTH` | API auth (set a strong `SECRET_KEY` in production) |
| `RATE_LIMIT_*`, `ALLOWED_ORIGINS` | Rate limiting and CORS allow-list |
| `JIRA_*` | Jira integration credentials |
| `APP_ENV`, `REQUIRE_HTTPS`, `SENTRY_DSN` | Environment mode, HTTPS enforcement, optional error tracking |

## Deploy

```bash
docker build -t mvpflow-ai:latest .
docker run -p 8000:8000 --env-file .env mvpflow-ai:latest
# …or the full local stack (app + Postgres):
docker-compose up -d
```

For production: set `APP_ENV=production`, a strong `SECRET_KEY`, `ENABLE_JWT_AUTH=true`, `REQUIRE_HTTPS=true`, and a PostgreSQL `DATABASE_URL`, then run `alembic upgrade head`. It runs on any container host (AWS ECS/Fargate, Google Cloud Run, Heroku, Azure, DigitalOcean) with a managed Postgres.

Hardening is built in: input sanitization, bcrypt password hashing, JWT auth, per-IP rate limiting, a CORS allow-list, security headers, and SQLAlchemy (no raw SQL).

## Status

What's actually verified today:

| Component | Status | Notes |
|-----------|--------|-------|
| Core workflow (deterministic) | ✅ Working | Template-based; covered by tests |
| Generic LLM pipeline (any domain) | ✅ Working (needs key) | Research → solution options → requirements → scope → architecture → tickets-from-your-scope → evaluation, via Claude/Groq when `USE_LLM=true`. Falls back to templates when off. Provider routing + fallback are tested (mocked); live model output is not asserted. |
| API server | ✅ Working & tested | FastAPI; `/health`, `/workflow`, `/executions`, validation, headers covered by `tests/test_api.py` |
| Database | ✅ Working & tested | SQLAlchemy (SQLite default, PostgreSQL supported); initial Alembic migration present |
| Authentication | ✅ Working & tested | JWT + bcrypt; `tests/test_security.py` |
| Rate limiting | ✅ Working | slowapi + 429 handler |
| Audit logging | ⚠️ Implemented | Writes to DB per request; exercised indirectly, no dedicated test |
| Docker | ✅ Built in CI | `docker-build` job builds the image on every push |
| Migrations on PostgreSQL | ✅ Verified in CI | `migrations-postgres` job runs `alembic upgrade head` against Postgres |
| Security scanning | ✅ Working (advisory) | `pip-audit` + `bandit` in CI; policy in [SECURITY.md](SECURITY.md) |
| Evaluation harness | ✅ Working | `eval/` golden cases + rubric runner |
| Monitoring | ✅ Optional hook | Logging + request-id/timing headers + health check; optional Sentry via `SENTRY_DSN` |
| Landing page generator | ✅ Working & tested | `app/core/landing.py` + `--landing`; self-contained HTML, `tests/test_landing.py` |
| Jira integration | ✅ Working | `--push-jira`; creates Story issues via Jira Cloud REST. Verified live against project `WOR` |
| Workflow automation | ✅ Working (human-gated) | `app/automation.py`: ticket → branch → draft PR → Jira *In Progress*. Never auto-merges |
| CI | ✅ Working | `.github/workflows/ci.yml` runs on every push/PR (`USE_LLM=false`) |
| Jira / GitHub via MCP connector | 🔄 By design, not shipped | Direct API + `gh` CLI is the default; MCP is for interactive use |

## Tests & CI

`pytest -q` runs the **41-test** suite (workflow, API, auth, database, LLM-routing, Jira, landing, tickets). CI runs four jobs on every push/PR with `USE_LLM=false`, so it never makes live model calls: **pytest**, **docker-build**, **migrations-postgres** (against a real PostgreSQL service), and **security** (advisory `pip-audit` + `bandit`).

## Documentation

- **[docs/CODEMAP.md](docs/CODEMAP.md)** - file-by-file guide to the codebase
- **[SKILL.md](SKILL.md)** / **[AGENTS.md](AGENTS.md)** - how to steer Claude / coding agents through the workflow
- **[SECURITY.md](SECURITY.md)** - security policy & scanning
- **[eval/README.md](eval/README.md)** - the evaluation harness
- **Worked example:** [problem statement](docs/problem_statement.md) · [research](docs/research.md) · [MVP plan](docs/mvp_plan.md) · [Jira backlog](docs/jira_backlog_sample.md) · [demo summary](docs/generated_demo_summary.md) · [prompts/](prompts/)
- **[Founder Template](../FOUNDER_TEMPLATE.md)** - the reusable take-home method
- **[Hands-on lab](../workshop/LAB.md)** - run it on your own idea (in a browser via Codespaces or Colab, or locally)

## Roadmap

Genuinely not done yet: an MCP-connector variant of the Jira/GitHub integration (a deliberate non-default), a prompt-regression test set with golden datasets, real APM/dashboards, and grading live model output quality at scale.

---

*MIT licensed. Built for the AI Garage workshop - and for founders: start with the MVP core, and add each production layer when it earns its place.*
