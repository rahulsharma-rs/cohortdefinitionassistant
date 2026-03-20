"""
Study Inference Agent — infers the type of study the user intends.
Uses Graph-of-Thought prompting to decompose the reasoning.
"""
import json
import os
from services.llm_service import call_llm


PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "study_inference.txt")


def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run(user_input: str) -> dict:
    """
    Infer study design from user's natural language cohort description.

    Args:
        user_input: Raw cohort description from the user.

    Returns:
        Dict with study_type, target_population, exposure, outcome,
        index_event, assumptions, ambiguities.
    """
    system_prompt = load_prompt()

    prompt = f"""Analyze the following cohort definition and infer the study design.

USER COHORT DEFINITION:
{user_input}

Respond with the JSON structure as specified in your instructions."""

    response = call_llm(prompt, system_prompt=system_prompt, expect_json=True)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "study_type": "Unknown",
            "target_population": user_input,
            "exposure": None,
            "outcome": None,
            "index_event": "Not determined",
            "assumptions": ["Could not fully parse study design"],
            "ambiguities": ["Full study design inference was not possible"],
            "raw_response": response,
        }

    return result
