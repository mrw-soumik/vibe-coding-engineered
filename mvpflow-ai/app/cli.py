from __future__ import annotations
import argparse
import json
import sys
import logging
from pathlib import Path
from app.core.workflow import run_workflow
from app.integrations.jira import push_tickets, jira_enabled
from app.llm.client import llm_enabled

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the MVPFlow AI workflow from founder notes.
    
    Reads notes from an input file, runs the complete workflow,
    and outputs results as Markdown summary and optional JSON.
    
    Exit codes:
        0: Success
        1: File not found or invalid input
        2: Workflow execution failed
    """
    # Force UTF-8 console output so status glyphs (e.g. the check mark) do not
    # crash on a Windows cp1252 console (UnicodeEncodeError) partway through a run.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        description="Run the MVPFlow AI workflow on founder notes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app.cli --input notes.txt --output summary.md
  python -m app.cli --input notes.txt --output summary.md --json output.json --domain restaurant
        """,
    )
    parser.add_argument("--input", required=True, help="Path to notes text file (required)")
    parser.add_argument("--output", required=True, help="Path to Markdown summary output (required)")
    parser.add_argument("--json", required=False, help="Optional path to JSON workflow output")
    parser.add_argument(
        "--landing",
        required=False,
        help="Optional path to write a self-contained HTML landing page for the MVP",
    )
    parser.add_argument(
        "--tickets-dir",
        required=False,
        help="Optional directory to write each ticket as its own Markdown file "
        "(plus a starter AGENTS.md), ready to hand to an AI coding agent.",
    )
    parser.add_argument(
        "--domain",
        default="restaurant",
        help="Domain for domain-fit evaluation (default: restaurant)",
    )
    parser.add_argument(
        "--push-jira",
        action="store_true",
        help="Push generated tickets to Jira. Dry-run by default; add --jira-live to actually create issues.",
    )
    parser.add_argument(
        "--jira-live",
        action="store_true",
        help="With --push-jira, actually create issues in Jira (requires JIRA_* env vars). Without this flag, --push-jira only previews payloads.",
    )
    args = parser.parse_args()

    logger.info(f"MVPFlow AI CLI - Starting workflow")
    logger.debug(f"Input file: {args.input}")
    logger.debug(f"Output file: {args.output}")
    logger.debug(f"Domain: {args.domain}")

    # Read input file
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input}")
            print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
            sys.exit(1)

        notes = input_path.read_text(encoding="utf-8")
        logger.info(f"Read {len(notes)} characters from input file")
    except IOError as e:
        logger.error(f"Error reading input file: {str(e)}")
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Warn loudly if there is no live model, so the built-in sample is not mistaken
    # for output generated from the user's own notes.
    if not llm_enabled():
        print(
            "! No LLM key detected - running in DEMO mode: output is a built-in sample, "
            "not based on your notes. Set USE_LLM=true and a provider key (GROQ_API_KEY "
            "or ANTHROPIC_API_KEY) to run on your own notes and domain.",
            file=sys.stderr,
        )

    # Run workflow
    try:
        logger.info("Running workflow...")
        result = run_workflow(notes, args.domain)
        logger.info(f"Workflow completed successfully. Overall score: {result.evaluation.overall_score}/5")
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        print(f"Error: Invalid input - {str(e)}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        print(f"Error: Workflow execution failed - {str(e)}", file=sys.stderr)
        sys.exit(2)

    # Write Markdown output
    try:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.final_summary, encoding="utf-8")
        logger.info(f"Summary written to {args.output}")
        print(f"✓ Summary written to {args.output}")
    except IOError as e:
        logger.error(f"Error writing output file: {str(e)}")
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(2)

    # Write JSON output (if requested)
    if args.json:
        try:
            json_path = Path(args.json)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
            logger.info(f"JSON output written to {args.json}")
            print(f"✓ JSON output written to {args.json}")
        except IOError as e:
            logger.error(f"Error writing JSON file: {str(e)}")
            print(f"Error writing JSON file: {e}", file=sys.stderr)
            sys.exit(2)

    # Write landing page (if requested)
    if args.landing:
        try:
            from app.core.landing import create_landing_page

            landing_path = Path(args.landing)
            landing_path.parent.mkdir(parents=True, exist_ok=True)
            html = create_landing_page(result.requirements, result.mvp_plan, args.domain)
            landing_path.write_text(html, encoding="utf-8")
            logger.info(f"Landing page written to {args.landing}")
            print(f"✓ Landing page written to {args.landing}")
        except IOError as e:
            logger.error(f"Error writing landing page: {str(e)}")
            print(f"Error writing landing page: {e}", file=sys.stderr)
            sys.exit(2)

    # Write ticket files (if requested)
    if args.tickets_dir:
        try:
            from app.core.tickets import write_tickets

            written = write_tickets(result.jira_tickets, args.tickets_dir, args.domain)
            logger.info(f"Wrote {len(written)} files to {args.tickets_dir}")
            print(
                f"✓ Wrote {len(result.jira_tickets)} tickets + AGENTS.md to {args.tickets_dir}/"
            )
        except IOError as e:
            logger.error(f"Error writing tickets: {str(e)}")
            print(f"Error writing tickets: {e}", file=sys.stderr)
            sys.exit(2)

    # Optionally push tickets to Jira
    if args.push_jira:
        dry_run = not args.jira_live
        if args.jira_live and not jira_enabled():
            print(
                "Error: --jira-live requires JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN "
                "to be set in the environment.",
                file=sys.stderr,
            )
            sys.exit(2)

        mode = "DRY RUN (no issues created)" if dry_run else "LIVE (creating issues)"
        print(f"\n{'='*60}\nJira push: {mode}\n{'='*60}")
        try:
            results = push_tickets(result.jira_tickets, dry_run=dry_run)
        except Exception as e:
            logger.error(f"Jira push failed: {str(e)}", exc_info=True)
            print(f"Error: Jira push failed - {str(e)}", file=sys.stderr)
            sys.exit(2)

        for r in results:
            if r["status"] == "created":
                print(f"  ✓ {r['ticket']} -> {r['key']} ({r['url']})")
            elif r["status"] == "dry_run":
                summary = r["payload"]["fields"]["summary"]
                sp = r.get("story_points")
                sp_field = r.get("story_points_field")
                sp_note = (
                    f" | {sp} pts -> {sp_field}" if (sp is not None and sp_field)
                    else f" | {sp} pts (field not resolved; set JIRA_STORY_POINTS_FIELD or run with creds)" if sp is not None
                    else ""
                )
                print(f"  • {r['ticket']} -> would create: {summary}{sp_note}")
            else:
                print(f"  ✗ {r['ticket']} -> error {r.get('status_code')}: {r.get('detail')}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Overall evaluation score: {result.evaluation.overall_score}/5")
    print(f"{'='*60}")
    logger.info("CLI execution completed successfully")


if __name__ == "__main__":
    main()
