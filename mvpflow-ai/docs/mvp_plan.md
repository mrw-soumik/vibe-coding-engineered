# MVP Plan & Backlog, Restaurant FAQ Assistant (worked example)

> The plan that follows from [`problem_statement.md`](problem_statement.md) and
> [`research.md`](research.md). This is what a *properly written* plan looks
> like: a chosen option with rationale, explicit scope boundaries, success
> criteria, and a story-pointed backlog. It supersedes the older
> `jira_backlog_sample.md` sketch.

## 1. Solution options considered

| Option | Description | Effort | Decision |
|---|---|---|---|
| A. Owner-reviewed FAQ assistant | Owner enters info; system drafts editable answers; risky questions flagged | Small | **Chosen** |
| B. Multi-channel auto-responder | Connect Instagram/FB/Google and auto-reply | Large | Deferred, over-automation risk, integration cost |
| C. Full customer-service platform | CRM + reservations + ordering + FAQ | X-Large | Out of scope, not the validated problem |

**Recommended: Option A**, the smallest version that delivers real value while
keeping a human in the loop for safety-critical answers.

## 2. In scope (build now)

- Enter / paste restaurant information (hours, menu, policies).
- Generate **editable** FAQ answers grounded in that information.
- Answer sample questions in a test console.
- **Flag** allergen, dietary, and missing-information questions for owner review.
- Produce evaluation test cases for common and risky questions.

## 3. Out of scope (deliberately deferred)

- Live Instagram / Facebook / Google / POS / delivery integrations.
- Fully automated public replies without owner approval.
- Payments, reservations engine, full CRM.
- Voice / phone agent.

## 4. Success criteria

- An owner can enter info and receive clear, editable FAQ drafts in minutes.
- Common questions get useful, consistent answers.
- Risky allergen / missing-info cases are **flagged, not guessed**.
- The workflow produces actionable tickets and an evaluation result.

## 5. Architecture (MVP shape)

`Owner input → grounded answer drafting → risk/▢missing-info flagging → owner
review → published FAQ`, with an evaluation harness over common + risky
questions. Human-in-the-loop is the core safety control. Production layers
(auth, storage, channel integrations, monitoring) are explicitly later.

## 6. Backlog

Story points on a Fibonacci scale (1, 2, 3, 5, 8). Total ≈ 21 points.

| Key | Title | Pts | Acceptance criteria (summary) |
|---|---|---|---|
| MVP-001 | Restaurant info input | 3 | Accept pasted/structured info; validate empty/oversized input |
| MVP-002 | Grounded answer drafting | 5 | Draft answers only from entered info; show source field; editable |
| MVP-003 | Allergen / missing-info flagging | 5 | Detect allergen/dietary/missing-info questions; flag for review, never guess |
| MVP-004 | Test console | 3 | Ask sample questions; see draft + flags side by side |
| MVP-005 | Evaluation test cases | 3 | Common + risky question set; pass/fail + flag-rate metric |
| MVP-006 | Owner review & publish | 2 | Owner edits/approves before any answer is marked ready |

> Each ticket should carry, in Jira: a user story (`As an owner, I want …`),
> full acceptance criteria, a definition of done, a suggested branch
> (`feature/mvp-00x-…`), and the story points above. The pipeline generates
> these automatically from the scope; this table is the human-readable summary.

## 7. Evaluation focus (definition of "good")

- **Content quality:** answers are useful, consistent, grounded.
- **Domain fit:** allergen/missing-info questions are flagged (the key safety
  metric); no fabricated answers.
- **System reliability:** required fields present, structured output valid,
  tests pass, edge cases (empty/short/risky input) handled.

## 8. Sequencing: core first, production layers when they earn their place

The MVP **core** above (sections 2–6) is what you build first; it delivers the
value and runs with almost no infrastructure. The **production layer** is added
deliberately, each piece triggered by a real need rather than up front. This
proportionality *is* the advanced-vibe-coding lesson: command the full toolkit,
then apply judgment about what to use when.

| Add this... | ...when this becomes true (the trigger) |
|---|---|
| Persistence (DB) | You need to remember runs / multiple owners use it |
| Authentication | You expose the assistant beyond a single trusted user |
| The highest-volume channel integration | Research shows where the question volume actually is |
| Monitoring / alerting | You're operating it for real users |
| Prompt-regression eval set | Before enabling any public auto-reply (safety gate) |
| Docker / managed Postgres | You deploy beyond a laptop |

Anti-goal: building all of the above on day one. Each layer has a cost and a
maintenance burden; add it when the trigger fires, not because it's available.
