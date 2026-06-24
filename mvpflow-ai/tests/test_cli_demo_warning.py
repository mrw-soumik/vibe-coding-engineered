"""The CLI must warn when it runs without a live model, so nobody mistakes the
built-in sample for output generated from their own notes."""
import os
import subprocess
import sys


def test_cli_warns_in_demo_mode(tmp_path):
    notes = tmp_path / "n.txt"
    notes.write_text("real founder notes about a real problem", encoding="utf-8")
    out = tmp_path / "out.md"

    env = {**os.environ, "USE_LLM": "false"}
    env.pop("GROQ_API_KEY", None)
    env.pop("ANTHROPIC_API_KEY", None)

    result = subprocess.run(
        [sys.executable, "-m", "app.cli", "--input", str(notes), "--output", str(out)],
        capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0
    assert "DEMO mode" in result.stderr
