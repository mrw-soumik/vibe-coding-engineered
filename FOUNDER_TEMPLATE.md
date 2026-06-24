# Founder AI Workflow Template

A reusable, AI-assisted process for turning messy founder notes into a scoped,
ticketed MVP plan. Copy this template, swap in your own startup and domain, and
work top to bottom. It is the same workflow MVPFlow AI runs end to end.

> The point is not to copy the restaurant example. It is to copy the **execution
> system**: validate, scope, plan, build, test, and explain, before you have a
> full team.

---

## 1. Paste your notes

Paste customer calls, founder notes, mentor feedback, support messages, survey
results, or product ideas. Raw and messy is fine.

## 2. Extract the problem

Ask:

- What is the real problem?
- Who has it?
- How do they solve it today?
- What is painful, repetitive, expensive, confusing, or risky?

## 3. Compare solution options

List three options, then pick the smallest one that is still useful:

1. Small MVP
2. More advanced workflow
3. Full product vision

> Choose the **smallest useful MVP**. You can always expand later.

## 4. Define scope

| In scope (build now) | Out of scope (later) |
|---|---|
| Feature 1 | Complex feature for later |
| Feature 2 | Integration not needed yet |
| Feature 3 | Anything risky without human review |

## 5. Create architecture

```text
User Input -> AI Processing -> Validation -> Human Review -> Output -> Evaluation
```

Keep it simple for an MVP. Show the structure, then note the production layers
(auth, data, CI, monitoring) you would add later, when they earn their place.

## 6. Create tickets

Each ticket should include:

- Title
- User story
- Description
- Acceptance criteria
- Priority
- Definition of done
- Suggested branch name
- Test / evaluation requirement

## 7. Build through GitHub

```text
Jira Ticket -> Branch -> Code -> Test -> Pull Request -> Review -> Jira Update
```

Keep AI-written changes human-gated: draft PRs are reviewed by a person, never
auto-merged.

## 8. Evaluate

Score the output across three layers (simple 1 to 5 scale):

- **Content quality** is the output useful and complete?
- **Domain fit** does it fit your business context and risks?
- **System reliability** does it behave consistently and pass tests?

Overall score = the average of the three.

## 9. Final summary

Summarize for a non-technical reader:

- Problem solved
- MVP selected
- What was built
- What was tested
- What failed
- What improves next

## 10. Launch page

Turn the scope into a simple launch or waitlist page so you can start validating
demand before you finish building.

---

## Run it with MVPFlow AI

The reference system can generate most of the above from a notes file, including
a self-contained launch page:

```bash
# Deterministic demo (no API key needed)
python -m app.cli \
  --input examples/restaurant_founder_notes.txt \
  --output docs/output.md \
  --landing landing.html \
  --domain restaurant

# Tailored to your own problem (any domain): set a provider key + USE_LLM=true
export ANTHROPIC_API_KEY=sk-ant-...   # or GROQ_API_KEY=gsk_...
export USE_LLM=true
python -m app.cli --input my_notes.txt --output my_plan.md --domain <your-domain> \
  --landing my_landing.html --tickets-dir tickets
```

## What else you get (the kit)

- **`prompts/`** the six LLM prompt templates, one per step (requirements,
  scope, architecture, Jira tickets, evaluation, summary).
- **`SKILL.md` / `AGENTS.md`** instruction templates for steering Claude or
  Codex to follow this workflow instead of changing code at random.
- **`docs/`** worked examples (`problem_statement.md`, `research.md`,
  `mvp_plan.md`, `jira_backlog_sample.md`) showing what good output looks like.
