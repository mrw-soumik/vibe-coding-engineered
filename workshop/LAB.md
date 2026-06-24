# Workshop Lab: Build Your MVP Plan (hands-on)

**Goal:** turn *your own* messy startup notes into a scoped MVP plan and a Jira-ready backlog - then **direct an AI agent** to turn one of those tickets into **tested, reviewed code in a real repo** (not a black-box app). You do not write code; you describe what you want and review what the AI produces.

> You won't walk out with a finished app. You'll walk out with a **validated plan, a backlog, your first feature built properly (code + a test + a reviewed PR), and a launch page** - plus the method to do it again for any idea.

This is **spec-driven development** - the same discipline behind tools like GitHub Spec Kit and AWS Kiro, made founder-friendly: the plan *is* the spec, and the spec drives the build. (Why this is the industry's "advanced" approach, with sources: [RESEARCH.md](RESEARCH.md).)

> **The real skill is asking the right question, not just taking the answer.** AI will answer almost anything; a clear spec *is* that question, and the build is only as good as the spec behind it. (Like the famous answer "42", an AI's output is useless until you know the real question you're asking.)

---

## Before you start

Do this quick pre-work (about 15 minutes) so we start building, not installing. Everyone works in **GitHub Codespaces** (VS Code in your browser, zero install, both parts in one place):

1. **A free GitHub account** - sign up at <https://github.com>. This is what runs your Codespace.
2. **Open the Codespace once** - click **[Open in GitHub Codespaces](https://codespaces.new/mrw-soumik/vibe-coding-engineered?quickstart=1)** and let it finish loading, so you are not doing it live. It comes with Python, the dependencies, and the `gh` CLI ready. If you plan to **write and push code in Part 2**, first **fork the repo** to your own account (the **Fork** button, top-right) and open your Codespace from *your fork*, so `git push` works. *(No GitHub account, or it will not open? Use the Colab fallback in Path B.)*
3. **A free Groq API key** - sign up at <https://console.groq.com> (free tier, no card). Keep it handy to paste in.
4. **Your messy notes** - a few lines on a real problem and who has it. Customer calls, mentor feedback, or just a paragraph. Messy is fine.

No coding experience needed. Non-technical founders still walk out with a full plan and a launch page; in the build part you direct the AI and review, rather than writing code.

---

## Pick one path

**Everyone uses GitHub Codespaces (Path A)** - it runs both Part 1 (plan) and Part 2 (build) in one browser window, no install. **Colab (Path B)** is a no-account fallback for Part 1 only. **Path C** needs nothing but a chat AI.

### Where your notes go (you never edit the code)

You don't change any code. You just hand the tool your notes as **input**, run one step, and read what comes out.

- **Codespaces (Path A):** open the file **`my_notes.txt`**, replace the sample text with your notes, then run the command in the terminal (below). Part 2's build happens in the same Codespace.
- **Colab fallback (Path B):** paste your notes into the cell titled **"3) Paste your own founder notes"** and set your `domain`, then run the **"4) Run the workflow"** cell.
- **No-code (Path C):** paste your notes straight into Claude.ai or ChatGPT with the template prompts.

**What you get back:** `my_plan.md` (your problem, MVP scope, and a backlog of tickets), `my_landing.html` (a shareable launch page), and a **`tickets/` folder** with each ticket as its own ready-to-build file plus a starter `AGENTS.md`.

**When:** this is **Part 1** (about 0:30 to 1:00 on the agenda). In **Part 2**, the tickets in that plan become the spec you build one feature from.

### Path A - Codespaces (recommended: everyone, both parts)
VS Code in your browser, nothing to install. You opened it during pre-work.

Open the repo in **[GitHub Codespaces](https://codespaces.new/mrw-soumik/vibe-coding-engineered?quickstart=1)**, wait for it to load, put your notes in **`my_notes.txt`** (open the file and replace the sample), then in the terminal run:

```bash
cd mvpflow-ai
export USE_LLM=true
export GROQ_API_KEY=gsk_...          # your free key
export GROQ_MODEL=llama-3.1-8b-instant
python -m app.cli --input my_notes.txt --domain my-domain \
  --output my_plan.md --landing my_landing.html --tickets-dir tickets
```

Open `my_plan.md` (your plan + backlog) and `my_landing.html` (launch page); your `tickets/` folder now holds one file per ticket (with acceptance criteria) plus `AGENTS.md`, ready for Part 2. **Part 2's build happens in this same Codespace.** *(Prefer local? The same steps work on your machine with git + Python 3.10+.)*

### Path B - Colab (fallback: no GitHub account, Part 1 only)
Nothing to install, works on any laptop, but it does not do the Part 2 build.

1. Open the notebook: **[Run in Colab](https://colab.research.google.com/github/mrw-soumik/vibe-coding-engineered/blob/main/workshop/mvpflow_colab.ipynb)**
2. Run the cells top to bottom (▶): add your free Groq key (cell 2), **paste your notes into cell 3** ("Paste your own founder notes") and set your domain, then run cell 4.
3. Cells 5 and 6 show your plan and launch page right in the notebook.

### Path C - No code at all (any chat AI)
Open **[FOUNDER_TEMPLATE.md](../FOUNDER_TEMPLATE.md)** and walk its 10 steps with Claude.ai or ChatGPT, pasting your notes and following each prompt. You'll produce the same plan by hand - no key, no install.

---

## The exercise + checkpoints

Work through these. The checkpoints tell you when you're done with each part.

1. **Write your notes.** One paragraph of the real problem, who has it, and what's painful.
2. **Run it** (Path A/B) or **walk the template** (Path C).
   - ✅ *Checkpoint:* you have a Problem, a Target user, and 3+ pain points that actually match your idea.
3. **Read your MVP scope.** Look at in-scope vs out-of-scope.
   - ✅ *Checkpoint:* the "out of scope" list contains something you were tempted to build but don't need yet.
4. **Read your backlog.** You should have ~6 tickets with acceptance criteria.
   - ✅ *Checkpoint:* you could hand ticket #1 to a developer (or an AI agent) and they'd know what to build.
5. **Open your launch page.**
   - ✅ *Checkpoint:* would you actually share this link to collect signups? If not, refine your notes and re-run.
6. **Now build it properly.** Those tickets are your spec - continue to **Part 2** to turn one into tested, reviewed code, the way a real engineer does.

### Optional: push your backlog to your own Jira

Your plan already lists the backlog as text. If you want those tickets on a real board you can work from, push them to **your own** Jira. This is optional and easy to do after the session too.

**Set up (one time):** create a free Jira site and project at <https://www.atlassian.com/software/jira/free> (note your project key, e.g. `MVP`), then create an API token at <https://id.atlassian.com/manage-profile/security/api-tokens>. Add these to your `.env`:

```
JIRA_BASE_URL=https://YOURSITE.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your_token
JIRA_PROJECT_KEY=MVP
```

**Push:** preview first, then create the issues for real:

```bash
python -m app.cli --input idea1.txt --domain saas --output plan1.md --push-jira             # dry run, creates nothing
python -m app.cli --input idea1.txt --domain saas --output plan1.md --push-jira --jira-live  # creates the issues on your board
```

Use **your own** Jira credentials only, never someone else's. Nothing is created unless you add `--jira-live`.

---

## Part 2: Build one feature by directing an AI (vibe coding, engineered)

A prompt-to-app tool (Lovable, AI Studio, Bolt) gives you a black box that *looks* done, but you can't test it, review it, extend it, or ship it safely. This is the engineered alternative, and **you do not write code**: your MVPFlow tickets (with acceptance criteria) are the spec, and you direct an AI agent to turn **one** of them into working, tested code you actually understand.

### Connections you need (and which are automatic)

- **GitHub + VS Code:**
  - **Part 1 (planning):** just open a Codespace on the repo and run it. Nothing to connect.
  - **Part 2 (building, and optionally opening a PR):** first **fork the repo to your own GitHub account** (the **Fork** button, top-right of the repo page), then open a Codespace **on your fork** (green **Code** button → **Codespaces** → **Create**). Because the fork is yours, `git` and the `gh` CLI are already signed in as you, so the optional "ship it" step (`git push`, `gh pr create`) just works. *(If you started in the original repo and then try to push, GitHub will offer to create your fork automatically.)*
  - *(Local VS Code instead? Sign in once via the **Accounts** icon → "Sign in with GitHub", then clone **your fork**.)*
- **Your AI coding agent (this is the heart of Part 2):** you direct an AI to write everything. Easiest in your Codespace is **Copilot** - enable **Copilot Free** at <https://github.com/settings/copilot>, sign in when Chat prompts (otherwise it shows *"You need to set up GitHub Copilot and be signed in to use Chat"*), then switch Copilot Chat from **Ask** to **Agent** mode so it can create files and run commands for you. Prefer **Claude Code** (terminal, Anthropic login) or **Cursor** (desktop app, its own account)? Both are already agents and need no Copilot.
- **Jira (optional, off by default):** to push your backlog to **your own** Jira board, set the four `JIRA_*` values in `.env` (steps in "Optional: push your backlog to your own Jira" above), then add `--push-jira`. Nothing goes to Jira unless you do this.

**Step 0 - watch once.** First, watch one whole feature built live by directing an AI: describe it in plain English, the agent writes the code, then *"write a test and prove it works,"* then review what it built. No hand-typing of code. Then you do the same.

### First: turn on Agent mode
This is vibe coding, so **you will not write code.** You describe what you want, an AI agent writes all of it (the code, the tests, and runs it), and your job is to direct and review.

- **Copilot (easiest in your Codespace):** in the Chat panel, switch the mode dropdown from **Ask** to **Agent**, so it can create files and run commands itself. (Ask mode only suggests snippets you would have to paste - not what we want.)
- **Claude Code** (terminal) or **Cursor** (desktop app) are already agents. Any of the three is fine.

### Then: pick one ticket and just talk
1. Pick the **simplest ticket** from your `tickets/` folder (for example `tickets/MVP-001.md`).
2. Give your product a fresh space (this is *your* app, not MVPFlow). In the terminal run `mkdir my-app && cd my-app && code .`, or simply ask the agent to set it up.
3. Now **just talk.** Say these one at a time, and read what comes back:
   - **Build it (hand over the ticket):** *"Implement the ticket in `mvpflow-ai/tickets/MVP-001.md`, building the app here in `my-app`. Follow the conventions in `mvpflow-ai/tickets/AGENTS.md`: write a test for each acceptance criterion first, then build until they pass. Then give me the run command and the URL."*
   - **Run it:** *"Run it and give me the link so I can try it myself."*
   - **Prove it works:** *"Show me the tests passing for each acceptance criterion."*
   - **Review it:** *"Explain in plain English what you built, and what is missing or risky before a real user."*
   - **Change it:** *"[one plain-English change]"* - to feel how fast you can iterate by talking.
   - **Ship it (optional):** *"Commit this and open a draft pull request so a human can review it before it goes live."*

> **Why the build prompt is so short:** the ticket already carries the user story and acceptance criteria, and `AGENTS.md` carries your build rules. That is spec-driven development - write the spec once, then just say "implement this ticket." No long prompt needed.

### Your job is to review, not to code
You are the manager. Judge what the agent hands back:

- Can you actually **use it** (add something, see it work)?
- Is there a **test**, and does it **pass**?
- Does it meet the ticket's **acceptance criteria**?
- What did the agent say is **missing or risky**? Would you ship it?

> ✅ *Done when:* you directed the AI to build one real, working thing with a passing test, and you can say what is still missing - all without writing a line of code yourself.

**Security (do not skip, even when vibe coding):** verify any package the agent adds actually exists (AI invents roughly 1 in 5, "slopsquatting"); never turn on auto-approve / "YOLO" mode; check input validation and secrets. Around **45% of AI-generated code ships with a known vulnerability**, so your review IS the safety gate.

**The one habit that makes it *engineered*:** always ask the agent to (a) **prove it with a test** and (b) **tell you what is missing or risky**, then review before you ship. That is the whole difference between engineered vibe coding and a black box you cannot trust. You can see the same discipline in this repo: tickets with acceptance criteria, `tests/` and CI gating every change, and draft PRs that never auto-merge.

> **Production-grade isn't day one.** "Properly" doesn't mean build auth + Docker + monitoring immediately. The repo shows the full path; add each piece **when it earns its place**.

---

## If something goes wrong

- **Groq is slow / "429" messages:** that's the free-tier rate limit; the tool retries automatically. Use `llama-3.1-8b-instant` (already set in the notebook) for the fastest path.
- **No key / key not working:** run without it - you'll get the built-in restaurant demo so you can still follow along - then switch to **Path C** to do *your* idea by hand.
- **Local install fails (Path B):** don't fight it live - switch to **Path A (Colab)**.
- **Output feels generic:** add more detail to your notes (the channels, the exact pains, the risks). Better input, better plan.
- **Agent stuck in a fix-loop (the "doom loop"):** usually a bug spanning data + logic + UI. Stop coding - tell it *"just diagnose and report back, don't change any code,"* then start a **fresh conversation** with that diagnosis. Looping inside one long thread makes it worse.
- **Agent fabricates (fake data, or claims "it works" when it doesn't):** agents goal-seek to look successful. Demand real integration and proof you can see; while diagnosing, prompt *"NO CHANGES, NO CODE - just discussion."*
