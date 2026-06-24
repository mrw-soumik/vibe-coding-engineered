"""Constants and configuration for MVPFlow AI."""
from __future__ import annotations
from typing import Dict, List, Any

# Domain-specific configurations
DOMAIN_CONFIGS: Dict[str, Dict[str, Any]] = {
    "restaurant": {
        "problem": "Restaurant owners spend too much time answering repeated customer questions across scattered channels.",
        "target_user": "Small restaurant owners and managers who handle customer questions manually.",
        "pain_points": [
            "Repeated questions about opening hours, menu items, allergies, reservations, and delivery.",
            "Customer communication is scattered across Instagram, phone calls, Google reviews, and Facebook.",
            "Owners risk missing requests or giving outdated information.",
            "Manual replies take time away from operations and customer service.",
        ],
        "risks": [
            "Allergy or dietary answers may be risky if menu information is incomplete.",
            "Outdated menu, delivery, or reservation information could mislead customers.",
            "Fully automated replies should not be enabled before owner review.",
        ],
        "mvp": {
            "recommended": "A human-reviewed AI FAQ assistant for restaurant owners.",
            "in_scope": [
                "Paste or upload restaurant information.",
                "Generate editable FAQ answers from the restaurant information.",
                "Answer sample customer questions in a test console.",
                "Flag risky allergy, dietary, or missing-information questions for owner review.",
                "Create evaluation test cases for common and risky questions.",
            ],
            "out_of_scope": [
                "Live Instagram, Facebook, POS, or delivery integrations.",
                "Fully automated customer replies without owner approval.",
                "Payments, reservations engine, or full CRM features.",
                "Voice/phone agent automation.",
            ],
            "success_criteria": [
                "Owner can enter restaurant information and receive clear FAQ drafts.",
                "Assistant handles common questions with useful answers.",
                "Risky allergy or missing-information cases are flagged instead of guessed.",
                "The workflow produces actionable Jira tickets and evaluation results.",
            ],
        },
        "domain_fit_metrics": [
            ("Domain Relevance", 5, "The workflow fits small restaurant owner operations."),
            ("Allergy/Menu Risk Handling", 5, "Allergy and missing menu information are flagged for owner review."),
            ("Missing Information Handling", 4.5, "The design avoids guessing when details are unavailable."),
            ("Human Review Fit", 5, "Owner approval is required before risky customer-facing use."),
            ("Practical Usefulness", 4.5, "The MVP would help reduce repeated manual responses."),
        ],
    },
}

# Generic domain template
DEFAULT_DOMAIN_CONFIG = {
    "problem": "The target users have messy notes and repeated manual work that needs structured MVP planning.",
    "target_user": "Early users in the domain.",
    "pain_points": [
        "Important feedback is scattered across notes and conversations.",
        "The team needs a clear MVP scope and execution plan.",
        "Manual task creation slows implementation.",
    ],
    "risks": [
        "Domain-specific risks must be reviewed by a human expert.",
        "The first version may overbuild if scope is not controlled.",
    ],
    "mvp": {
        "recommended": "A human-reviewed assistant that converts domain notes into MVP tasks and validation checks.",
        "in_scope": ["Note input", "Requirement extraction", "MVP scope", "Ticket generation", "Evaluation checklist"],
        "out_of_scope": ["Complex integrations", "Production automation", "Authentication", "Payments"],
        "success_criteria": ["Output is clear, actionable, and safe for human review."],
    },
    "domain_fit_metrics": [
        ("Domain Relevance", 4, "The workflow is adaptable but needs domain expert review."),
        ("Risk Handling", 4, "General risks are flagged; domain-specific checks should be added."),
        ("Human Review Fit", 5, "Human approval remains part of the workflow."),
    ],
}

# Content quality metrics (used for all domains)
CONTENT_QUALITY_METRICS = [
    ("Problem Accuracy", 5, "The main operational problem is clearly identified."),
    ("Target User Accuracy", 5, "The target user is specific and founder-friendly."),
    ("Pain Point Coverage", 4.5, "Major pains are captured accurately."),
    ("MVP Scope Quality", 4.5, "The MVP is small, useful, and avoids overbuild."),
    ("Jira Ticket Actionability", 4.5, "Tickets include user stories, acceptance criteria, priority, and branch guidance."),
    ("Final Summary Quality", 4.5, "Summary is clear enough for a mentor, team member, or founder update."),
]

# System reliability metrics (used for all domains)
SYSTEM_RELIABILITY_METRICS = [
    ("Required Field Completeness", 5, "Core sections are generated: requirements, scope, architecture, tickets, evaluation, summary."),
    ("JSON/API Structure", 5, "The API uses typed Pydantic models and predictable output structure."),
    ("Test Pass Readiness", 5, "The reference workflow is covered by pytest checks."),
    ("Edge Case Handling", 4, "Short notes and regulated-domain cues are handled with assumptions/risks."),
    ("Production Readiness", 3.5, "This is a workshop reference system; production needs live LLM, Jira/GitHub, auth, storage, and monitoring."),
]

# Jira ticket templates
JIRA_TICKETS = [
    {
        "key": "MVP-001",
        "title": "Define restaurant FAQ MVP scope",
        "description": "Define the first version of the assistant and the boundaries of what it should not do.",
        "acceptance_criteria": [
            "In-scope and out-of-scope features are documented",
            "Success criteria are approved",
            "Risky automation boundaries are listed",
        ],
        "priority": "High",
    },
    {
        "key": "MVP-002",
        "title": "Build founder notes input workflow",
        "description": "Allow founders or restaurant owners to paste messy notes or business information for analysis.",
        "acceptance_criteria": [
            "Text input is accepted",
            "Empty input is handled",
            "Long input is handled",
            "Input is passed into the workflow",
        ],
        "priority": "High",
    },
    {
        "key": "MVP-003",
        "title": "Generate MVP analysis output",
        "description": "Extract the problem, target user, pain points, risks, assumptions, and recommended MVP.",
        "acceptance_criteria": [
            "Problem is identified",
            "Target user is identified",
            "Pain points are listed",
            "Risks and assumptions are included",
        ],
        "priority": "High",
    },
    {
        "key": "MVP-004",
        "title": "Generate Jira-style execution tickets",
        "description": "Convert the MVP plan into clear user stories and acceptance criteria.",
        "acceptance_criteria": [
            "At least five tickets are created",
            "Each ticket has acceptance criteria",
            "Each ticket has definition of done",
            "Suggested branch names are included",
        ],
        "priority": "High",
    },
    {
        "key": "MVP-005",
        "title": "Add evaluation metrics",
        "description": "Evaluate content quality, domain fit, and system reliability.",
        "acceptance_criteria": [
            "Content quality score is generated",
            "Domain-fit score is generated",
            "System reliability score is generated",
            "Overall score and recommendation are included",
        ],
        "priority": "High",
    },
    {
        "key": "MVP-006",
        "title": "Create final founder summary",
        "description": "Generate a concise delivery summary that can be shared with team members, mentors, or investors.",
        "acceptance_criteria": [
            "Problem is summarized",
            "MVP is summarized",
            "Evaluation result is included",
            "Limitations and next steps are included",
        ],
        "priority": "Medium",
    },
]

# Story point estimates per ticket (Fibonacci scale). Total = 24 points.
JIRA_STORY_POINTS = {
    "MVP-001": 3,   # scope definition
    "MVP-002": 3,   # input workflow
    "MVP-003": 5,   # core analysis output
    "MVP-004": 5,   # ticket generation
    "MVP-005": 5,   # evaluation metrics
    "MVP-006": 3,   # final summary
}

# Architecture components
ARCHITECTURE_COMPONENTS = [
    {"name": "Founder Notes Input", "purpose": "Collect messy customer notes, discovery findings, or business context."},
    {"name": "Requirement Extraction", "purpose": "Identify problem, user, pain points, risks, and assumptions."},
    {"name": "MVP Scope Engine", "purpose": "Separate in-scope MVP work from later-stage product ideas."},
    {"name": "Architecture Planner", "purpose": "Create a simple technical structure before implementation."},
    {"name": "Jira Ticket Generator", "purpose": "Convert scope into user stories, acceptance criteria, and definitions of done."},
    {"name": "Evaluation Layer", "purpose": "Score content quality, domain fit, and system reliability."},
    {"name": "Final Summary Generator", "purpose": "Create a founder-ready delivery summary and next-step plan."},
]

ARCHITECTURE_DATA_FLOW = [
    "Founder/customer notes are submitted.",
    "Requirements are extracted and reviewed.",
    "MVP scope is defined with clear out-of-scope boundaries.",
    "Architecture and Jira tickets are generated.",
    "Outputs are evaluated using content, domain, and reliability metrics.",
    "Final summary is produced for founders, mentors, or team members.",
]

ARCHITECTURE_NEXT_LAYERS = [
    "Replace deterministic modules with Claude/Codex prompt calls where useful.",
    "Connect Jira through MCP or API after human approval gates are defined.",
    "Connect GitHub workflow through GitHub API/MCP and PR templates.",
    "Add database storage, authentication, and prompt regression tests for production.",
]

# Validation constants
MIN_NOTES_LENGTH = 10
MAX_NOTES_LENGTH = 50000
RECOMMENDED_NOTES_LENGTH = 120

# Keywords that trigger special handling
PRIVACY_KEYWORDS = ["privacy", "health", "medical", "patient"]

# Evaluation recommendation
EVALUATION_RECOMMENDATION = "Workshop-ready. Use as a deterministic reference system, then add live Claude/Codex, Jira, GitHub, and MCP integrations as the advanced layer."
