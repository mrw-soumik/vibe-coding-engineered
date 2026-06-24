# Advanced Vibe Coding: What the Field Is Doing (2025–2026)

The research backing this workshop's approach. The short version: the industry converged on a disciplined, **spec-driven** way of building with AI agents, and MVPFlow is a founder-friendly version of exactly that pattern. Sources are linked inline with dates; a few figures are flagged as single-source.

---

## 1. "Vibe coding" → "agentic engineering": the dividing line

Andrej Karpathy coined **vibe coding** in Feb 2025 for *throwaway* projects ("forget that the code even exists"). He has since reframed serious work as **"agentic engineering"** - you orchestrate agents and act as oversight, and there is "an art & science and expertise to it." ([Karpathy, Feb 2 2025](https://x.com/karpathy/status/1886192184808149383))

The expert consensus draws one line: **it's not who wrote the code, it's whether a human understands, reviews, and is accountable for it.**

- **Simon Willison:** vibe coding = "building software with an LLM without reviewing the code." His rule: "I won't commit any code I couldn't explain to somebody else." Fine for low-stakes/throwaway; switch modes the moment data, money, safety, or secrets are involved. ([Mar 19 2025](https://simonwillison.net/2025/Mar/19/vibe-coding/))
- **Addy Osmani** (*Beyond Vibe Coding*): "AI tools are copilots, not autopilots." The human owns architecture and reviews every line. ([Nov 30 2025](https://medium.com/@addyosmani/vibe-coding-is-not-the-same-as-ai-assisted-engineering-3f81088d5b98))
- **Kent Beck:** distinguishes "augmented coding" - you still care about the code, complexity, tests, and coverage. Agents will "cheat" by disabling/deleting tests to go green. ([Jun 25 2025](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes))
- **GitHub:** scopes vibe coding to "proof-of-concept work and personal projects, not production code." ([GitHub Docs](https://docs.github.com/en/copilot/tutorials/vibe-coding))

### Principles experts agree on
1. Understand and be able to explain every change you ship.
2. Review every diff against the original intent.
3. Spec / plan before prompting; separate planning from implementation.
4. Tests are the verification backbone - and guard them (agents fake green).
5. Own the architecture; AI is a copilot, not an autopilot.
6. Enforce security with controls, not prompts.
7. Build a harness: rules/instructions (feedforward) + tests/CI/evidence (feedback).
8. Expect the "70% problem" - the last 30% (edge cases, security, integration) is real engineering.
9. Match the mode to the stakes.
10. You stay accountable as the orchestrator. "A computer can never be held accountable." (Willison, [Dec 18 2025](https://simonwillison.net/2025/Dec/18/code-proven-to-work/))

---

## 2. The dominant "advanced" pattern: Spec-Driven Development (SDD)

The whole field converged on *spec/plan before code*, with tooling to enforce it. **MVPFlow's pipeline - notes → requirements → scope → architecture → tickets-with-acceptance-criteria - is spec-driven development, made for founders.**

- **GitHub Spec Kit** (Sep 2 2025): `Specify → Clarify → Plan → Tasks → Implement`; `/speckit.taskstoissues` turns tasks into GitHub issues. "Intent is the source of truth." ([blog](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/), [repo](https://github.com/github/spec-kit))
- **AWS Kiro** (Jul 14 2025): generates `requirements.md` → `design.md` → `tasks.md`, with **EARS** notation for testable acceptance criteria ("WHEN <trigger> THE SYSTEM SHALL <response>"). ([kiro.dev](https://kiro.dev/docs/specs/), [EARS](https://alistairmavin.com/ears/))
- **Anthropic** `SPEC.md`, **OpenAI** `PLANS.md`, **Cursor** Plan Mode - same idea.
- Honest tension (Martin Fowler / Thoughtworks, Oct–Dec 2025): a maturity spectrum from *spec-first → spec-anchored → spec-as-source*; beware review burden and the "control illusion" (agents ignore detailed specs). ([Fowler/Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

---

## 3. Tools & conventions

- **Agents:** Claude Code, Cursor, OpenAI Codex (CLI + cloud), Aider, Devin/Windsurf.
- **Convention files:** **AGENTS.md** is now a standard (stewarded under the Linux Foundation; ~22 tools support it), alongside `CLAUDE.md` and `.cursor/rules`. ([agents.md](https://agents.md/))
- **Best practices** ([GitHub study of 2,500+ repos, Nov 19 2025](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)): commands first; cover commands, testing, structure, code style, git workflow, boundaries; a **three-tier always / ask-first / never** boundary block; keep it lean (Claude target **<200 lines** - bloated files get ignored).
- This repo ships `SKILL.md` (Claude) and `AGENTS.md` (coding agents) for exactly this.

---

## 4. The discipline practitioners follow

- **Plan-then-act.** Anthropic: "letting Claude jump straight to coding can produce code that solves the wrong problem." ([best practices](https://code.claude.com/docs/en/best-practices))
- **TDD where it matters - you own the tests.** Human owns the spec/tests; the AI makes them pass. Watch for the agent deleting/weakening failing tests to fake green (Beck).
- **Small, reviewable PRs; commit often as save points.** AI PRs trend larger and are *harder* to review, so incrementalism is a control. (Osmani, Jan 2026)
- **Human-in-the-loop; never auto-merge.** Prove it works (you saw it run + an automated test that fails if reverted). (Willison, Dec 2025)
- **Adversarial review in a fresh context** - a second agent/subagent reviews the diff against the spec (Writer/Reviewer pattern). (Anthropic workshops)
- **Non-bypassable CI gates + evals** (programmatic + LLM-as-judge). (Thoughtworks review-gates, 2026)

---

## 5. Failure modes + mitigations

- **Security:** ~**45%** of AI-generated code contained a known vulnerability, and newer models weren't safer ([Veracode 2025](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)). AI-assisted devs wrote *less* secure code but felt *more* confident ([Stanford CCS'23](https://arxiv.org/abs/2211.03622)). → Challenge the AI on input validation/secrets; never enable auto-approve/"YOLO" mode; treat repo content as untrusted (prompt-injection: CVE-2025-53773).
- **Slopsquatting:** ~20% of AI-suggested packages don't exist and recur predictably; attackers pre-register them. → Verify every dependency before install; lockfiles + frozen CI.
- **Automation bias:** Thoughtworks put "complacency with AI-generated code" on **HOLD** (Nov 2025). → small diffs, lean on tests/static analysis over gut feel.
- **The 70% problem** (Osmani): AI nails ~70%; the last 30% is the hard engineering.
- **Fabrication / "doom loop":** agents goal-seek to *look* successful (fake data/results) and loop on cross-layer (data/logic/UI) bugs. → "Just diagnose and report back, don't change code," and start a fresh conversation. (Torres, [producttalk.org](https://www.producttalk.org/vibe-coding-best-practices/); Lemkin, [saastr.com](https://www.saastr.com/the-complete-guide-to-vibe-coding-hard-won-lessons-for-building-your-first-commercial-app/))
- **Reality check:** a [METR RCT (Jul 2025)](https://arxiv.org/abs/2507.09089) found experienced devs ~19% *slower* with AI while believing they were faster. Discipline matters.

*Single-source / flagged:* CodeRabbit's "1.7×/2.74×" issue figures and GitClear's vulnerability multiplier are vendor analyses, not independently confirmed; the robust security numbers are Veracode's 45% and Stanford CCS'23.

---

## 6. Running the session: lessons from real workshops

- **Setup friction is the #1 killer.** Use **Codespaces / devcontainers** so attendees open a ready environment in the browser - no local install. a16z names "setup" the first barrier ([Feb 3 2026](https://a16z.com/most-people-cant-vibe-code-heres-how-we-fix-that/)). This repo ships a `.devcontainer/` for that.
- **Spec-first, pair-with-an-agent + adversarial review, eval-driven exercises, mixed-skill pairing.** Anthropic open-sourced its conference labs ([anthropics/cwc-workshops](https://github.com/anthropics/cwc-workshops), ~45 min each, escalating to production + evals).
- **a16z's four barriers** (a useful checklist): setup, security, **imagination** (people don't know what's buildable - bring templates), deployment.
- **Honest scoping:** little AI-generated code reaches production today, so frame a hands-on session as "the right workflow on a real slice," not "a production app in 2 hours."

---

## How MVPFlow maps to all this

| Field practice | In this repo |
|---|---|
| Spec-Driven Development | The whole pipeline: notes → requirements → scope → architecture → tickets |
| Acceptance criteria / EARS-style | `jira_ticket_generator.py` tickets carry acceptance criteria + definition of done |
| Tickets → issues (Spec Kit `taskstoissues`) | `--push-jira` creates real Jira Story issues |
| Plan-then-act, human-in-the-loop | `app/automation.py`: ticket → branch → **draft PR** → review; never auto-merges |
| Convention files | `SKILL.md` (Claude) + `AGENTS.md` (coding agents) |
| CI gates + evals | `.github/workflows/ci.yml` (pytest, docker, migrations, security) + `eval/` |
| Add production when it earns its place | The "two layers" model in the README |

The gaps this workshop closes vs. the field are the *teaching* of TDD-ownership, fresh-context review, security verification, and the doom-loop reset - see [LAB.md](LAB.md).
