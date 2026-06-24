#!/usr/bin/env bash
# Regenerate the workshop PDF from the canonical Markdown source.
# The Markdown file is the single source of truth; the committed PDF is derived.
#
# Primary path: the Python generator (markdown + weasyprint).
#   pip install markdown weasyprint   # weasyprint needs pango: brew install pango
# Usage:  bash scripts/build_pdf.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if python -c "import weasyprint, markdown" 2>/dev/null; then
  python scripts/build_pdf.py
elif command -v pandoc >/dev/null 2>&1; then
  echo "weasyprint not available; falling back to pandoc..."
  pandoc "../MVPFlow_AI_Workshop_Package.md" \
    -o "../MVPFlow_AI_Workshop_Package.pdf"
else
  echo "Install the renderer first:" >&2
  echo "  pip install markdown weasyprint   (brew install pango)" >&2
  echo "  or: brew install pandoc" >&2
  exit 1
fi
