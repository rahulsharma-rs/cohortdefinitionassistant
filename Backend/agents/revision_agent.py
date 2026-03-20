"""
Revision Agent — revises the cohort definition when verification finds
unsupported or problematic criteria.
"""
import json
import os
from services.llm_service import call_llm


PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "revision.txt")


def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run(
    cohort_definition: dict,
    verification_results: dict,
    catalog_summary: str,
) -> dict:
    """
    Revise the cohort definition based on verification results.

    Args:
        cohort_definition: Current cohort definition.
        verification_results: Output from verification agent.
        catalog_summary: EHR catalog summary for context.

    Returns:
        Revised cohort definition with change documentation.
    """
    system_prompt = load_prompt()

    # Identify problematic criteria
    unsupported = []
    for crit in verification_results.get("criteria_verification", []):
        status = crit.get("status", "")
        if status in ("NOT_SUPPORTED", "NEEDS_MODIFICATION", "PARTIALLY_SUPPORTED"):
            unsupported.append(crit)

    if not unsupported:
        # Nothing to revise
        return {
            "revised_definition": cohort_definition,
            "changes_made": [],
            "remaining_issues": [],
        }

    prompt = f"""Revise the following cohort definition based on verification results.

CURRENT COHORT DEFINITION:
{json.dumps(cohort_definition, indent=2)}

UNSUPPORTED OR PROBLEMATIC CRITERIA:
{json.dumps(unsupported, indent=2)}

FULL VERIFICATION RESULTS:
{json.dumps(verification_results, indent=2)}

EHR DATA SUMMARY:
{catalog_summary}

Revise only the criteria that need modification. Keep supported criteria unchanged.
Respond with the JSON structure as specified in your instructions."""

    response = call_llm(prompt, system_prompt=system_prompt, expect_json=True)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "revised_definition": cohort_definition,
            "changes_made": [],
            "remaining_issues": ["Could not parse revision response"],
            "raw_response": response,
        }

    return result
