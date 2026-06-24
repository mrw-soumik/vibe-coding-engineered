# Research, Restaurant FAQ Assistant (worked example)

> Domain research that grounds the MVP scope. This is the kind of artifact the
> pipeline's research step ([`app/core/research.py`](../app/core/research.py))
> produces when an LLM provider is enabled. The notes below are an honest
> domain analysis, **not** a market report, placeholders mark where real,
> sourced data should be gathered before a build decision.

## 1. How the problem is solved today

| Approach | What it is | Limitations |
|---|---|---|
| Manual replies | Owner answers DMs/calls/reviews by hand | Time-consuming, inconsistent, easy to miss |
| Static FAQ page | Fixed Q&A on the website | Goes stale; doesn't cover channel-specific questions |
| Generic chatbots | Off-the-shelf website chat widgets | Not grounded in the specific menu; risk wrong allergen info |
| Reservation/ordering platforms | Tools like booking/delivery apps | Solve booking/ordering, not the repeated Q&A across channels |

## 2. Existing tools / alternatives (landscape)

- **Website chat widgets** (generic Q&A bots): broad, not menu-aware, weak on
  safety-critical answers.
- **Social inbox aggregators**: unify channels but don't draft answers.
- **Reservation/ordering SaaS**: adjacent; owns booking/payments, not FAQ.
- **DIY (ChatGPT copy/paste)**: flexible but ungrounded and inconsistent, with
  no allergen safeguards.

> The MVP's wedge: *menu-grounded, owner-reviewed answer drafting*, the gap
> these alternatives leave open.

## 3. Domain-specific risks

- **Allergen / dietary safety (highest):** an incorrect allergen answer can
  cause real harm and liability. The system must flag, never guess.
- **Staleness:** menus, hours, and delivery zones change; stale answers mislead.
- **Over-automation:** publishing automated replies before owner trust is built
  risks brand damage; keep human-in-the-loop first.
- **Privacy:** if customer messages are stored, handle personal data per
  applicable regulation (e.g. GDPR/CCPA).

## 4. Industry best practices to follow

- **Human-in-the-loop for safety-critical output**, draft, don't publish.
- **Ground answers in a single source of truth** (the owner's entered info);
  cite which field an answer came from so it's auditable.
- **Fail safe:** when information is missing, say so and escalate to the owner
  rather than fabricating.
- **Keep the MVP small** and validate the core loop before adding integrations.
- **Evaluate before shipping:** test common and risky questions; track an
  allergen/missing-info "flag rate" as a safety metric.

## 5. Open questions to validate (placeholders for real data)

- Which channels drive the most repeated questions? *(measure)*
- How many repeated questions per week per restaurant? *(measure → time saved)*
- What share of questions touch allergens/dietary needs? *(safety sizing)*
- Will owners trust and actually edit AI drafts? *(usability test)*

## 6. Implications for the MVP

1. The first version is **owner-facing draft generation**, not a public bot.
2. A **risk-flagging** path for allergen/missing-info questions is mandatory,
   not optional.
3. Integrations (Instagram/POS/delivery) are **out of scope** until the core
   draft-and-review loop is validated.

See [`mvp_plan.md`](mvp_plan.md) for how this research shapes the scope and
backlog.
