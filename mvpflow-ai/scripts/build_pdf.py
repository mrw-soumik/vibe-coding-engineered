#!/usr/bin/env python3
"""Render the workshop master Markdown to a styled PDF.

The Markdown file (repo root) is the single source of truth; this regenerates
the committed PDF from it. Requires `markdown` and `weasyprint`
(``pip install markdown weasyprint``; weasyprint needs pango, ``brew install
pango`` on macOS).

Usage:  python scripts/build_pdf.py
"""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "MVPFlow_AI_Workshop_Package.md"
OUT = REPO_ROOT / "MVPFlow_AI_Workshop_Package.pdf"

CSS = """
@page { size: A4; margin: 2cm 2.2cm; @bottom-center { content: counter(page);
  font-size: 9pt; color: #888; } }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 20pt; color: #0b3d63; border-bottom: 2px solid #0b3d63;
  padding-bottom: 4px; margin-top: 0; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; color: #0b3d63; margin-top: 1.4em; }
h3 { font-size: 11.5pt; color: #333; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9pt;
  background: #f3f4f6; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px;
  padding: 10px 12px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0;
  page-break-inside: avoid; }
th, td { border: 1px solid #d0d7de; padding: 5px 9px; text-align: left;
  font-size: 9.5pt; vertical-align: top; }
th { background: #eef2f6; }
blockquote { border-left: 3px solid #0b3d63; margin: 0.8em 0; padding: 2px 14px;
  color: #444; background: #f8fafc; }
a { color: #0b5cad; text-decoration: none; }
"""

TITLE = """
<div style="text-align:center; margin-bottom:2.5cm;">
  <h1 style="border:none; page-break-before:avoid; font-size:30pt;">MVPFlow AI</h1>
  <p style="font-size:13pt; color:#555;">Full Workshop Package</p>
  <p style="font-size:10pt; color:#888;">An end-to-end AI-assisted product engineering workflow for founders</p>
</div>
"""


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"]
    )
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style>" \
           f"</head><body>{TITLE}{body}</body></html>"
    HTML(string=html, base_url=str(REPO_ROOT)).write_pdf(str(OUT))
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
