# Before the Workshop (about 15 minutes)

This is a 2-hour hands-on session. A few minutes of prep means we start building, not fighting setup. **No coding experience needed.**

We will all work in **GitHub Codespaces** - a full workshop environment that runs in your browser, with nothing to install. Please do these 4 things beforehand.

## Your checklist

**1. A free GitHub account (about 3 minutes)**
Sign up at <https://github.com> if you do not already have one. This is what runs your Codespace.

**2. Open the Codespace once and confirm it loads (about 5 minutes)**
Click **[Open in GitHub Codespaces](https://codespaces.new/mrw-soumik/vibe-coding-engineered?quickstart=1)** and wait for it to finish loading. If it opens, you are set; you can close it again until the session. If you think you will **push your Part 2 build to GitHub**, first click **Fork** (top-right of the repo page) to make your own copy, then open your Codespace from *your fork* so `git push` works. For Part 2 you will also set up your AI assistant (see below) so Chat works. *(Trouble opening it? No problem, use the Colab fallback below and we will sort it out live.)*

**3. A free Groq API key (about 5 minutes)**
Sign up at <https://console.groq.com> and create an API key. It is free and needs no credit card. Keep it handy to paste in during the session.

**4. Bring your idea (about 5 minutes)**
Jot down a few messy notes about a real problem you want to solve: who has it and what is painful. Messy is perfect; that is the raw material we turn into a plan.

## That is it

You do not need anything else. If you have never written code, that is fine; you will still walk out with a real MVP plan, a backlog, and a launch page, and you can go as deep as you want. In Part 2, everyone directs the AI and reviews, rather than writing code.

## Turn on your AI coding assistant (for Part 2)

In Part 2 you build a feature by **directing an AI** - you do not write code yourself. Set your agent up ahead of time so it works the moment you need it. (Planning to only watch Part 2? You can skip this.)

- **Easiest, works right in your Codespace: GitHub Copilot Free.** Enable it once on your account at <https://github.com/settings/copilot> (free, no credit card; about 2,000 completions and 50 chat messages a month). Then in your Codespace open the **Chat** panel, click **Set up Copilot / Sign in**, and switch the mode from **Ask** to **Agent** so it can create files and run commands for you. If you skip this, Chat will say *"You need to set up GitHub Copilot and be signed in to use Chat."*
- **Prefer Claude Code or Cursor?** Claude Code runs in the Codespace terminal (needs an Anthropic login); Cursor is a desktop editor on your own laptop (needs a Cursor account, not Copilot). Both are already agents; you do not need Copilot for these.

## Optional: your own Jira board (do it later)

Want your generated tickets to land on a real Jira board? This is optional and a bit more setup, so feel free to skip it or do it after the session. If you want it:
1. Create a free Jira site and project at <https://www.atlassian.com/software/jira/free>.
2. Create an API token at <https://id.atlassian.com/manage-profile/security/api-tokens>.

Bring those two and we will show you how to push your backlog. Use your **own** Jira only, never anyone else's credentials.

**No-install fallback:** if GitHub or Codespaces gives you trouble, you can do the planning part in the browser with **[Colab](https://colab.research.google.com/github/mrw-soumik/vibe-coding-engineered/blob/main/workshop/mvpflow_colab.ipynb)** instead (no account needed).

Optional peek at everything: the repo is at <https://github.com/mrw-soumik/vibe-coding-engineered> (start at [`LAB.md`](LAB.md)).
