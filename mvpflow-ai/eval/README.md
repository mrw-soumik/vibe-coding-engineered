# Evaluation Harness

A small, reusable template for grading the pipeline's output against a rubric , 
the discipline the workshop preaches ("a demo is not enough: score usefulness,
fit, and reliability").

## Files
- `golden_cases.json`, golden inputs (problem statement + domain) plus the
  rubric assertions each output must satisfy.
- `run_eval.py`, runs the workflow on each case and checks the assertions.

## Run

```bash
# Deterministic (no key, reproducible), grades the template/offline output:
python eval/run_eval.py

# Live, grade real generated output with the SAME rubric (catches regressions):
USE_LLM=true ANTHROPIC_API_KEY=...  python eval/run_eval.py
# or: USE_LLM=true GROQ_API_KEY=... GROQ_MODEL=llama-3.3-70b-versatile python eval/run_eval.py
```

Exits non-zero if any check fails, so you can wire it into a release gate.

## Supported rubric checks
| Check | Meaning |
|---|---|
| `min_tickets` | at least N tickets generated |
| `all_tickets_min_acceptance` | every ticket has ≥ N acceptance criteria |
| `tickets_have_story_points` | every ticket carries a story-point estimate |
| `risks_include` | the extracted risks mention a substring (e.g. `allerg`, `privac`) |
| `recommended_mvp_nonempty` | an MVP recommendation was produced |
| `summary_includes` | the delivery summary contains a required section |

## Extending
Add a case to `golden_cases.json` for your own domain, list the checks that
define "good" for it, and (optionally) add new check types in `run_eval.py`.
For subjective quality, add an LLM-as-judge check that scores the artifact
against a written rubric, keep it opt-in since it costs model calls.
