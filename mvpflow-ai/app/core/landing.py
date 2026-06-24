"""Landing-page generator for the founder's MVP.

Takes the requirements + MVP plan the pipeline already produces and renders a
**self-contained** launch/waitlist landing page (single HTML file, inline CSS,
no external assets, scripts, or build step) the founder can host anywhere. Copy
is tailored by the LLM when enabled; otherwise it's derived deterministically
from the plan.

This is an optional *output* (like ``--json``), not part of the core workflow.
The next concrete artifact a founder needs after a plan is a way to validate
demand, and this provides it.
"""
from __future__ import annotations

import html
import logging
from datetime import datetime, UTC
from typing import List

from pydantic import BaseModel

from app.models import RequirementExtraction, MVPPlan
from app.llm.client import llm_enabled, generate_structured

logger = logging.getLogger(__name__)


class ValueProp(BaseModel):
    title: str
    body: str


class LandingCopy(BaseModel):
    """Copy for the landing page (LLM-generated or derived from the plan)."""
    product_name: str
    headline: str
    subheadline: str
    value_props: List[ValueProp]   # ~3
    features: List[str]            # "what you can do"
    cta_label: str
    cta_note: str


_COPY_SYSTEM = (
    "You are a startup copywriter writing a launch/waitlist landing page for the "
    "MVP described. Be concrete, plain, and benefit-led; no buzzwords, no hype, "
    "sentence case. Headline <= 9 words. Three value props with short titles "
    "(2-4 words) and a one-sentence body each. Features are things the user can "
    "actually do. The CTA captures early interest."
)


def _copy_with_llm(req: RequirementExtraction, plan: MVPPlan, domain: str) -> LandingCopy:
    prompt = (
        f"Domain: {domain}\n"
        f"Problem: {req.problem}\n"
        f"Target user: {req.target_user}\n"
        f"Recommended MVP: {plan.recommended_mvp}\n"
        f"In scope: {plan.in_scope}\n"
        f"Success criteria: {plan.success_criteria}\n\n"
        "Write product_name, headline, subheadline, 3 value_props (title+body), "
        "features (from in-scope), cta_label, cta_note."
    )
    return generate_structured(_COPY_SYSTEM, prompt, LandingCopy)


def _copy_fallback(req: RequirementExtraction, plan: MVPPlan, domain: str) -> LandingCopy:
    """Deterministic copy derived from the plan (LLM mode produces sharper copy)."""
    # Deterministically we can't paraphrase a criterion into a punchy title, so
    # use the criterion itself as a clean statement (no truncated title fragments).
    crits = plan.success_criteria or plan.in_scope
    props = [ValueProp(title=c.rstrip(".,"), body="") for c in crits[:3]]
    return LandingCopy(
        product_name=f"{domain.strip().title()} Assistant",
        headline=plan.recommended_mvp.rstrip("."),
        subheadline=req.problem,
        value_props=props,
        features=list(plan.in_scope),
        cta_label="Join the waitlist",
        cta_note="Be first to try it. No spam, just one email when it's ready.",
    )


def create_landing_page(req: RequirementExtraction, plan: MVPPlan, domain: str = "restaurant") -> str:
    """Return a complete, self-contained HTML landing page for the MVP."""
    if llm_enabled():
        try:
            copy = _copy_with_llm(req, plan, domain)
        except Exception as e:  # fall back to deterministic copy on any failure
            logger.warning("LLM landing copy failed, using derived copy: %s", e)
            copy = _copy_fallback(req, plan, domain)
    else:
        copy = _copy_fallback(req, plan, domain)
    return _document(copy)


# --- rendering ---------------------------------------------------------------

def _esc(s: str) -> str:
    return html.escape(s, quote=True)


# Small inline line-icons (no xmlns needed for inline SVG in HTML5; stroke uses
# currentColor so they inherit the accent). Kept minimal and geometric.
_MARK = (
    '<svg class="mark" viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">'
    '<rect x="2.5" y="2.5" width="19" height="19" rx="6" fill="currentColor"></rect>'
    '<path d="M7 15c2.2 0 2.2-6 5-6s2.8 6 5 6" fill="none" stroke="#fff" '
    'stroke-width="1.8" stroke-linecap="round"></path></svg>'
)
_ICONS = [
    # spark
    '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"></path></svg>',
    # shield-check
    '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M12 3 5 6v6c0 4 3 6.6 7 9 4-2.4 7-5 7-9V6l-7-3z"></path>'
    '<path d="M9 12l2 2 4-4"></path></svg>',
    # gauge
    '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path></svg>',
]
_CHECK = (
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M5 12l4 4 10-10"></path></svg>'
)

_STYLE = """<style>
  :root {
    --bg:#fafafc; --ink:#0e1116; --muted:#5a6473; --line:rgba(14,17,22,.10);
    --card:#ffffff; --band:#f3f4f8;
    --hero:#0b0e17; --hero-ink:#e9ecf5; --hero-muted:#9aa3b8; --hero-line:rgba(255,255,255,.14);
    --accent:#5b8cff; --accent-strong:#3d6bf0; --accent-2:#38e0c0;
    --radius:16px; --maxw:1080px;
    --shadow-sm:0 1px 2px rgba(14,17,22,.06), 0 8px 24px rgba(14,17,22,.06);
    --shadow-md:0 10px 40px rgba(14,17,22,.12);
  }
  * { box-sizing:border-box; }
  body { margin:0; }
  .lp {
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color:var(--ink); background:var(--bg); line-height:1.55; -webkit-font-smoothing:antialiased;
    text-rendering:optimizeLegibility;
  }
  .lp .wrap { max-width:var(--maxw); margin:0 auto; padding:0 24px; }
  .lp a { color:inherit; text-decoration:none; }

  /* sticky glass nav */
  .lp .nav { position:sticky; top:0; z-index:10; background:rgba(11,14,23,.62);
    backdrop-filter:saturate(160%) blur(14px); -webkit-backdrop-filter:saturate(160%) blur(14px);
    border-bottom:1px solid var(--hero-line); }
  .lp .nav-inner { display:flex; align-items:center; justify-content:space-between; height:64px; }
  .lp .brand { display:inline-flex; align-items:center; gap:9px; font-weight:750;
    letter-spacing:-.02em; color:var(--hero-ink); }
  .lp .brand .mark { color:var(--accent); flex:none; }
  .lp .nav-links { display:flex; align-items:center; gap:26px; }
  .lp .nav-links a { color:var(--hero-muted); font-size:.94rem; font-weight:550; }
  .lp .nav-links a:hover { color:var(--hero-ink); }

  .lp .btn { display:inline-flex; align-items:center; justify-content:center;
    background:var(--accent); color:#fff; font-weight:650; font-size:1rem;
    padding:13px 22px; border:0; border-radius:12px; cursor:pointer;
    box-shadow:0 6px 20px rgba(91,140,255,.35);
    transition:transform .15s ease, box-shadow .15s ease, background .15s ease; }
  .lp .btn:hover { transform:translateY(-2px); background:var(--accent-strong);
    box-shadow:0 12px 30px rgba(91,140,255,.45); }
  .lp .btn:focus-visible { outline:3px solid rgba(91,140,255,.5); outline-offset:2px; }
  .lp .btn-sm { padding:9px 16px; font-size:.92rem; }

  /* hero */
  .lp .hero { position:relative; overflow:hidden; background:var(--hero); color:var(--hero-ink); }
  .lp .aurora { position:absolute; inset:-30% -10% auto -10%; height:140%; pointer-events:none;
    background:
      radial-gradient(40% 55% at 18% 18%, rgba(91,140,255,.42), transparent 70%),
      radial-gradient(42% 52% at 82% 12%, rgba(56,224,192,.30), transparent 72%),
      radial-gradient(46% 60% at 65% 80%, rgba(123,97,255,.30), transparent 74%);
    filter:blur(36px); opacity:.9; }
  .lp .hero-inner { position:relative; display:grid; grid-template-columns:1.1fr .9fr;
    gap:54px; align-items:center; padding:84px 24px 92px; }
  .lp .pill { display:inline-flex; align-items:center; gap:8px; font-size:.76rem; font-weight:650;
    letter-spacing:.1em; text-transform:uppercase; color:#cfe0ff;
    background:rgba(91,140,255,.16); border:1px solid rgba(91,140,255,.34);
    padding:7px 13px; border-radius:999px; }
  .lp .pill::before { content:""; width:7px; height:7px; border-radius:50%; background:var(--accent-2);
    box-shadow:0 0 0 4px rgba(56,224,192,.22); }
  .lp h1 { font-size:clamp(2.4rem,5.4vw,4.05rem); line-height:1.02; letter-spacing:-.04em;
    font-weight:800; margin:.46em 0 .28em; max-width:16ch; }
  .lp .sub { font-size:clamp(1.06rem,2.1vw,1.28rem); color:var(--hero-muted);
    max-width:50ch; margin:0 0 30px; }

  /* waitlist form (used on dark backgrounds) */
  .lp .waitlist { display:flex; gap:10px; flex-wrap:wrap; max-width:480px; }
  .lp .waitlist input { flex:1 1 230px; min-width:0; padding:14px 16px; font-size:1rem;
    color:#fff; background:rgba(255,255,255,.08); border:1px solid var(--hero-line);
    border-radius:12px; }
  .lp .waitlist input::placeholder { color:rgba(233,236,245,.55); }
  .lp .waitlist input:focus { outline:none; border-color:var(--accent);
    box-shadow:0 0 0 3px rgba(91,140,255,.35); }
  .lp .note { font-size:.85rem; color:var(--hero-muted); margin:13px 0 0; }

  /* hero preview card (glass) */
  .lp .preview { justify-self:end; width:100%; max-width:380px; }
  .lp .preview-card { background:rgba(255,255,255,.06); border:1px solid var(--hero-line);
    border-radius:20px; padding:20px; box-shadow:0 30px 70px rgba(0,0,0,.35);
    backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px); }
  .lp .preview-head { display:flex; gap:7px; margin-bottom:16px; }
  .lp .preview-head span { width:10px; height:10px; border-radius:50%; background:rgba(255,255,255,.22); }
  .lp .preview-label { font-size:.74rem; font-weight:650; letter-spacing:.12em;
    text-transform:uppercase; color:var(--hero-muted); margin:0 0 12px; }
  .lp .preview-list { list-style:none; margin:0; padding:0; display:grid; gap:11px; }
  .lp .preview-list li { display:flex; gap:11px; align-items:flex-start; font-size:.96rem;
    color:#eef1f8; }
  .lp .preview-list svg { color:var(--accent-2); flex:none; margin-top:2px; }

  /* sections */
  .lp .section { padding:92px 0; }
  .lp .band { background:var(--band); border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
  .lp .eyebrow { font-size:.76rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase;
    color:var(--accent-strong); margin:0 0 14px; }
  .lp .section h2 { font-size:clamp(1.7rem,3.4vw,2.4rem); letter-spacing:-.03em; font-weight:780;
    margin:0 0 44px; max-width:20ch; }

  /* value props */
  .lp .props { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
  .lp .prop { background:var(--card); border:1px solid var(--line); border-radius:var(--radius);
    padding:26px 24px; box-shadow:var(--shadow-sm);
    transition:transform .18s ease, box-shadow .18s ease; }
  .lp .prop:hover { transform:translateY(-4px); box-shadow:var(--shadow-md); }
  .lp .ico { display:inline-flex; align-items:center; justify-content:center; width:44px; height:44px;
    border-radius:12px; color:var(--accent-strong); background:rgba(91,140,255,.12); margin-bottom:16px; }
  .lp .prop h3 { margin:0 0 8px; font-size:1.12rem; letter-spacing:-.01em; }
  .lp .prop p { margin:0; color:var(--muted); font-size:.97rem; }

  /* features */
  .lp .features { list-style:none; padding:0; margin:0; display:grid;
    grid-template-columns:repeat(2,1fr); gap:16px 30px; }
  .lp .features li { display:flex; gap:13px; align-items:flex-start; font-size:1.02rem; }
  .lp .features .chk { display:inline-flex; align-items:center; justify-content:center; flex:none;
    width:26px; height:26px; border-radius:8px; color:var(--accent-strong); background:rgba(91,140,255,.12); }

  /* closing CTA (dark band) */
  .lp .cta { position:relative; overflow:hidden; background:var(--hero); color:var(--hero-ink); }
  .lp .cta .aurora { opacity:.7; }
  .lp .cta-inner { position:relative; text-align:center; padding:90px 24px; }
  .lp .cta h2 { font-size:clamp(1.9rem,4vw,2.7rem); letter-spacing:-.03em; margin:0 0 12px; }
  .lp .cta-sub { color:var(--hero-muted); margin:0 0 28px; font-size:1.05rem; }
  .lp .cta .waitlist { margin:0 auto; justify-content:center; }
  .lp .cta .note { text-align:center; }

  /* footer */
  .lp .footer { border-top:1px solid var(--line); }
  .lp .footer-inner { display:flex; align-items:center; justify-content:space-between;
    flex-wrap:wrap; gap:12px; padding:30px 24px; }
  .lp .footer .brand { color:var(--ink); }
  .lp .footer .brand .mark { color:var(--accent-strong); }
  .lp .footer .muted { color:var(--muted); font-size:.86rem; }

  @media (max-width:860px) {
    .lp .hero-inner { grid-template-columns:1fr; gap:40px; padding:60px 24px 72px; }
    .lp .preview { justify-self:stretch; max-width:none; }
    .lp .nav-links a:not(.btn) { display:none; }
    .lp .props { grid-template-columns:1fr; }
    .lp .features { grid-template-columns:1fr; }
    .lp .section { padding:64px 0; }
  }

  .lp .reveal { opacity:0; transform:translateY(14px); animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards; }
  .lp .reveal.d1 { animation-delay:.08s; }
  @keyframes rise { to { opacity:1; transform:none; } }
  @media (prefers-reduced-motion:reduce) { .lp .reveal { animation:none; opacity:1; transform:none; } }
</style>"""


def _body(copy: LandingCopy) -> str:
    """The page content + styles (no <html>/<head>/<body> wrapper)."""
    year = datetime.now(UTC).year
    name = _esc(copy.product_name)
    mark_name = f'<a class="brand" href="#top">{_MARK}<span>{name}</span></a>'

    props = "".join(
        '<article class="prop"><span class="ico">{icon}</span><h3>{title}</h3>{body}</article>'.format(
            icon=_ICONS[i % len(_ICONS)],
            title=_esc(p.title),
            body=f"<p>{_esc(p.body)}</p>" if p.body.strip() else "",
        )
        for i, p in enumerate(copy.value_props)
    )
    feats = "".join(
        f'<li><span class="chk">{_CHECK}</span><span>{_esc(f)}</span></li>'
        for f in copy.features
    )
    preview_items = "".join(
        f"<li>{_CHECK}<span>{_esc(f)}</span></li>" for f in copy.features[:4]
    )

    def waitlist(label: str) -> str:
        return (
            '<form class="waitlist" onsubmit="return false" aria-label="Join the waitlist">'
            '<input type="email" required placeholder="you@example.com" aria-label="Email address" />'
            f'<button class="btn" type="submit">{_esc(label)}</button>'
            "</form>"
        )

    return f"""{_STYLE}
<div class="lp">
  <header class="nav">
    <div class="wrap nav-inner">
      {mark_name}
      <nav class="nav-links">
        <a href="#why">Why it helps</a>
        <a href="#features">What you can do</a>
        <a class="btn btn-sm" href="#join">Join the waitlist</a>
      </nav>
    </div>
  </header>

  <section class="hero" id="top">
    <div class="aurora"></div>
    <div class="wrap hero-inner">
      <div class="hero-copy reveal">
        <span class="pill">Early access</span>
        <h1>{_esc(copy.headline)}</h1>
        <p class="sub">{_esc(copy.subheadline)}</p>
        <div id="join">{waitlist(copy.cta_label)}</div>
        <p class="note">{_esc(copy.cta_note)}</p>
      </div>
      <aside class="preview reveal d1">
        <div class="preview-card">
          <div class="preview-head"><span></span><span></span><span></span></div>
          <p class="preview-label">Early access includes</p>
          <ul class="preview-list">{preview_items}</ul>
        </div>
      </aside>
    </div>
  </section>

  <section class="section" id="why">
    <div class="wrap">
      <p class="eyebrow">Why it helps</p>
      <h2>Built to do the work you keep repeating.</h2>
      <div class="props">{props}</div>
    </div>
  </section>

  <section class="section band" id="features">
    <div class="wrap">
      <p class="eyebrow">What you can do</p>
      <h2>Everything in the first release.</h2>
      <ul class="features">{feats}</ul>
    </div>
  </section>

  <section class="cta">
    <div class="aurora"></div>
    <div class="wrap cta-inner">
      <h2>Get early access to {name}.</h2>
      <p class="cta-sub">{_esc(copy.cta_note)}</p>
      {waitlist(copy.cta_label)}
    </div>
  </section>

  <footer class="footer">
    <div class="wrap footer-inner">
      {mark_name}
      <span class="muted">© {year} · now in early access</span>
    </div>
  </footer>
</div>"""


def _document(copy: LandingCopy) -> str:
    """Wrap the body in a complete, standalone HTML document."""
    title = f"{copy.product_name}: {copy.headline}"
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
        f"<title>{_esc(title)}</title>\n"
        f'<meta name="description" content="{_esc(copy.subheadline)}" />\n'
        "</head>\n<body>\n"
        f"{_body(copy)}\n"
        "</body>\n</html>\n"
    )
