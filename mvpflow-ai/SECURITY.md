# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately (e.g. a GitHub Security
Advisory on this repo, or by emailing the maintainer) rather than opening a
public issue. Include reproduction steps and affected versions. We aim to
acknowledge within a few business days.

## Automated scanning (advisory)

CI runs two scans on every push/PR (see `.github/workflows/ci.yml`, `security`
job). They are **advisory**, they surface findings for review but do not block
the build, because a reference repo's transitive dependencies will occasionally
carry advisories that aren't exploitable in this context.

- **`pip-audit`**, checks dependencies against the Python advisory database.
- **`bandit`**, static analysis of `app/` for common security issues
  (config in `pyproject.toml` → `[tool.bandit]`).

Run them locally:

```bash
pip install pip-audit bandit
pip-audit -r requirements.txt
bandit -c pyproject.toml -r app -ll
```

## Secrets handling

- All credentials (API keys, Jira tokens, `SECRET_KEY`, database passwords) are
  read from environment variables / a local `.env`, **never** hardcoded.
- `.env` is git-ignored; do not commit real secrets. Use `.env.example` as the
  template.
- Generate a strong `SECRET_KEY` for production:
  `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- Production config (`APP_ENV=production`) validates that `SECRET_KEY` and
  `DATABASE_URL` are set to non-default values (`app/config.py`).

## Built-in protections

Input validation + sanitization (XSS/script rejection in `app/models.py`),
bcrypt password hashing, JWT auth, rate limiting, security headers (CSP,
X-Frame-Options, nosniff), SQL-injection-safe ORM access, and HTTPS enforcement
(configurable). See the Security section of `README.md` for the production
checklist.

## Scope / status

This is a workshop reference system with a production-shaped scaffold. It has
**not** had a formal third-party security review or penetration test. Harden and
review before handling real user data.
