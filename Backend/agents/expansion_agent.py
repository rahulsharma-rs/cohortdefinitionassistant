"""
Criteria Expansion Agent — expands the cohort definition with clinically
relevant criteria across 10 dimensions.
"""
import json
import os
from services.llm_service import call_llm


PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "criteria_expansion.txt")


def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run(user_input: str, study_inference: dict, catalog_summary: str) -> dict:
    """
    Expand the cohort definition with comprehensive clinical criteria.

    Args:
        user_input: Original cohort description from the user.
        study_inference: Output from the inference agent.
        catalog_summary: EHR catalog domain summary for context.

    Returns:
        Dict with expanded criteria across all dimensions.
    """
    system_prompt = load_prompt()

    prompt = f"""Expand the following cohort definition into comprehensive clinical criteria.

ORIGINAL COHORT DEFINITION:
{user_input}

INFERRED STUDY DESIGN:
{json.dumps(study_inference, indent=2)}

AVAILABLE EHR DATA SUMMARY:
{catalog_summary}

Based on the study design and available data, expand the criteria across all 10 dimensions.
Respond with the JSON structure as specified in your instructions."""

    response = call_llm(prompt, system_prompt=system_prompt, expect_json=True)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "demographics": {"age_range": None, "gender": None, "race": None, "ethnicity": None},
            "conditions": {"inclusion": [], "exclusion": []},
            "medications": {"inclusion": [], "exclusion": []},
            "measurements": {"criteria": []},
            "procedures": {"inclusion": [], "exclusion": []},
            "encounters": {"required_types": [], "minimum_count": None},
            "temporal_windows": {"baseline_period_days": 180, "followup_period_days": 365, "washout_period_days": None},
            "social_determinants": [],
            "outcomes": {"primary": "", "secondary": []},
            "data_completeness": {"min_observation_days": 180, "required_domains": []},
            "raw_response": response,
        }

    return result
