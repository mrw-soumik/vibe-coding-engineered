# Codebase Map

A file-by-file guide to what each part of MVPFlow AI does. Pairs with the
repository-structure tree in [`../README.md`](../README.md#repository-structure).

## Pipeline overview

```
notes → requirements → research → solution options → MVP scope →
architecture → Jira tickets → evaluation → delivery summary
```

When an LLM provider is configured (`USE_LLM=true` + Anthropic or Groq key) each
step is generated from the actual input; otherwise the steps fall back to the
deterministic templates in `app/constants.py` (used by tests and the offline demo).

## The two layers

The codebase has two parts (see the README's "Two layers" section). Build the
core first; add a production-layer piece when it earns its place.

- **MVP core (the workflow):** `app/core/`, `app/llm/`, `app/integrations/`,
  `app/utils/`, `app/models.py`, `app/constants.py`. Runs with zero infra.
- **Production layer (how to ship it):** `app/main.py`, `app/database.py`,
  `app/security.py`, `app/middleware.py`, `app/observability.py`, plus `tests/`,
  `alembic/`, `Dockerfile`, CI, and security scanning.
- **Interfaces:** `app/cli.py`, `app/automation.py`, the FastAPI API.

## `app/`, application root

| File | Responsibility |
|---|---|
| `main.py` | FastAPI app + endpoints (`/health`, `/api/v1/workflow`, `/api/v1/executions`), startup DB init, audit logging. Entrypoint `app.main:app`. |
| `cli.py` | Command-line runner: notes → Markdown/JSON; optional `--landing` (HTML page) and `--push-jira`. |
| `automation.py` | Orchestrates Jira → branch → draft PR → Jira "In Progress" (dry-run default; never auto-merges). |
| `config.py` | Env-based settings (DB, secrets, LLM/Groq, Jira, feature flags). |
| `constants.py` | Deterministic domain templates + story points (offline fallback data). |
| `models.py` | All Pydantic models (request + every pipeline output type). |
| `database.py` | SQLAlchemy ORM (`WorkflowExecution`, `APIUser`, `APIKey`, `AuditLog`) + `DatabaseManager`. |
| `security.py` | JWT create/verify, bcrypt hashing, required + optional auth dependencies. |
| `middleware.py` | Request-ID, timing, security headers, CORS, rate limiter, logging setup. |

## `app/core/`, workflow pipeline (domain logic)

| File | Responsibility |
|---|---|
| `workflow.py` | Orchestrates the steps; returns the full `WorkflowResponse`. |
| `requirements_extractor.py` | Notes → problem / user / pain points / risks / assumptions. |
| `research.py` | Domain/market research (LLM only; web search on Anthropic). |
| `solutions.py` | Three solution options → recommend the smallest useful MVP (LLM only). |
| `mvp_scope.py` | Requirements → in-scope / out-of-scope / success criteria. |
| `architecture.py` | Scope → components, data flow, next production layers. |
| `jira_ticket_generator.py` | Scope → backlog (LLM-generated from scope, or template). |
| `evaluation.py` | Three-layer scoring (content quality / domain fit / system reliability). |
| `summary.py` | Assembles the founder-ready Markdown delivery summary. |
| `landing.py` | Requirements + scope → self-contained HTML launch/waitlist landing page (optional output; LLM-tailored copy or deterministic). |

## `app/llm/`, LLM provider abstraction

| File | Responsibility |
|---|---|
| `client.py` | Provider routing (Anthropic preferred, Groq fallback), `generate_structured` (structured output), `web_search`, the deterministic-fallback gate. |
| `codegen.py` | AI code-draft (full-file changes) for the automation pipeline. |

## `app/integrations/`, external systems

| File | Responsibility |
|---|---|
| `jira.py` | Jira Cloud REST: create issues (ADF + story points), transitions, comments, dry-run; story-points field discovery. |
| `github.py` | Branch creation + draft PR via the `gh` CLI. |

## `app/utils/`

| File | Responsibility |
|---|---|
| `text_utils.py` | Text normalization helpers. |

## `tests/`

| File | Covers |
|---|---|
| `conftest.py` | Hermetic fixtures (temp DB, neutralized creds, TestClient). |
| `test_workflow.py` | The deterministic pipeline. |
| `test_api.py` | Endpoints, input validation, response headers. |
| `test_security.py` | Password hashing, JWT round-trip, optional-auth. |
| `test_database.py` | ORM persistence + per-row timestamp defaults. |
| `test_llm.py` | Provider routing + fallback (mocked, no network). |
| `test_jira.py` | ADF/payload building, dry-run (no network). |
| `test_landing.py` | Landing-page generator: well-formed/self-contained HTML, plan content, escaping. |

## Supporting

| Path | Responsibility |
|---|---|
| `alembic/` + `alembic.ini` | DB migrations (`env.py`, `script.py.mako`, `versions/…_initial_schema.py`). |
| `docs/` | `problem_statement.md`, `research.md`, `mvp_plan.md` (worked example), `jira_backlog_sample.md`, `generated_demo_summary.md`, this `CODEMAP.md`. |
| `prompts/` | Prompt templates for each LLM step. |
| `examples/` | `restaurant_founder_notes.txt`, `sample_workflow_output.json`, `sample_landing.html`. |
| `scripts/` | `setup-production.sh`, `build_pdf.sh`. |
| build/config | `Dockerfile`, `docker-compose.yml`, `Makefile`, `pyproject.toml`, `requirements.txt`, `.env.example`. |
| meta docs | `README.md`, `SECURITY.md`, `SKILL.md`, `AGENTS.md`. |

The take-home method is in `../../FOUNDER_TEMPLATE.md`, and the hands-on lab is in
`../../workshop/LAB.md`.
