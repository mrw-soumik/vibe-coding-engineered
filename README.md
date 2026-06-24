# Vibe Coding, Engineered

An AI-assisted, **spec-driven** MVP workflow for founders, and the 2-hour hands-on workshop that teaches it.

[![CI](https://github.com/mrw-soumik/vibe-coding-engineered/actions/workflows/ci.yml/badge.svg)](https://github.com/mrw-soumik/vibe-coding-engineered/actions/workflows/ci.yml)
![Version 1.0.0](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](mvpflow-ai/LICENSE)

This is not prompt-to-app. It teaches founders to build the way a real engineer does: a clear spec drives the work, an AI coding agent does the typing, every change lands as a tested and human-reviewed pull request, and CI keeps it honest.

## Start here

| If you are... | Go to |
|---|---|
| **Attending? Get ready (15 min)** | [`workshop/PREWORK.md`](workshop/PREWORK.md) - the quick, no-code pre-work to do before the session |
| **Attending the workshop** | [`workshop/LAB.md`](workshop/LAB.md) - the hands-on lab you follow during the session |
| **Just want to try the system** | [`mvpflow-ai/README.md`](mvpflow-ai/README.md) - 60-second quick start, no API key needed |
| **Applying it to your own startup** | [`FOUNDER_TEMPLATE.md`](FOUNDER_TEMPLATE.md) - the reusable take-home template |

## What MVPFlow AI does

Paste in messy founder notes and it produces a structured, buildable execution package:

```text
Founder notes  ->  requirements  ->  MVP scope  ->  architecture
            ->  Jira backlog  ->  reviewed PR  ->  evaluation  ->  founder-ready summary
```

By default it runs fully offline (deterministic, ideal for a live demo). Set a Claude or Groq key and it generates the whole pipeline live from your own problem, in any domain. In industry terms this is **spec-driven development**: the pattern behind GitHub Spec Kit and AWS Kiro, made founder-friendly.

## What's in this repo

```text
mvpflow-ai/                        The codebase (FastAPI, 41 tests, CI, pinned deps)
workshop/
  LAB.md                           The 2-hour hands-on lab
  RESEARCH.md                      Sourced industry findings behind the approach
  mvpflow_colab.ipynb              Zero-install browser runtime
.devcontainer/                     One-click GitHub Codespaces environment
FOUNDER_TEMPLATE.md                The reusable founder template
Founder_AI_Workflow_Template.pdf   Printable version of the template
```

## Quick start

```bash
git clone https://github.com/mrw-soumik/vibe-coding-engineered.git
cd vibe-coding-engineered/mvpflow-ai
pip install -r requirements.txt
pytest -q

python -m app.cli \
  --input examples/restaurant_founder_notes.txt \
  --output out.md --landing landing.html --domain restaurant
```

Open `out.md` for the plan and `landing.html` in any browser. Prefer the API? Run `uvicorn app.main:app --reload` and open `http://localhost:8000/docs`.

Zero local setup: open the repo in [GitHub Codespaces](https://codespaces.new/mrw-soumik/vibe-coding-engineered?quickstart=1) or run the [Colab notebook](https://colab.research.google.com/github/mrw-soumik/vibe-coding-engineered/blob/main/workshop/mvpflow_colab.ipynb).

## License

MIT. See [`mvpflow-ai/LICENSE`](mvpflow-ai/LICENSE).
