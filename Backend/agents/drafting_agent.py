"""
Cohort Drafting Agent — produces a structured, implementable cohort definition.
"""
import json
import os
from services.llm_service import call_llm


PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "cohort_draft.txt")


def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run(user_input: str, study_inference: dict, expanded_criteria: dict) -> dict:
    """
    Produce a structured cohort definition from the expanded criteria.

    Args:
        user_input: Original cohort description.
        study_inference: Output from inference agent.
        expanded_criteria: Output from expansion agent.

    Returns:
        Structured cohort definition dict.
    """
    system_prompt = load_prompt()

    prompt = f"""Draft a structured cohort definition based on the following inputs.

ORIGINAL COHORT DEFINITION:
{user_input}

INFERRED STUDY DESIGN:
{json.dumps(study_inference, indent=2)}

EXPANDED CRITERIA:
{json.dumps(expanded_criteria, indent=2)}

Produce a complete, implementable cohort definition with all required sections.
Respond with the JSON structure as specified in your instructions."""

    response = call_llm(prompt, system_prompt=system_prompt, expect_json=True)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "study_objective": "Could not generate structured definition",
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "index_event": {"description": "Not determined", "domain": "unknown"},
            "baseline_window": {"days_before_index": 180, "description": ""},
            "followup_window": {"days_after_index": 365, "description": ""},
            "temporal_logic": [],
            "raw_response": response,
        }

    return result
