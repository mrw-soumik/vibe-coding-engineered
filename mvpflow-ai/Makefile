.PHONY: install test demo api

install:
	python -m pip install -r requirements.txt

test:
	pytest -q

demo:
	python -m app.cli --input examples/restaurant_founder_notes.txt --output docs/generated_demo_summary.md --json examples/sample_workflow_output.json

api:
	uvicorn app.main:app --reload
