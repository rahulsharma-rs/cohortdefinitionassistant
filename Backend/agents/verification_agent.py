"""
EHR Catalog Verification Agent — checks the drafted cohort definition
against the EHR catalog for domain availability, vocabulary coverage,
and data completeness.
"""
import json
import os
from services.llm_service import call_llm
from services.retrieval_service import RetrievalService


PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "ehr_verification.txt")


def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run(
    cohort_definition: dict,
    terminology_mappings: dict,
    retrieval_service: RetrievalService,
    catalog_summary: str,
) -> dict:
    """
    Verify the cohort definition against EHR catalog.

    Args:
        cohort_definition: Structured cohort definition.
        terminology_mappings: Output from terminology agent.
        retrieval_service: Hybrid retrieval service.
        catalog_summary: Domain summary string.

    Returns:
        Verification results dict.
    """
    system_prompt = load_prompt()

    # Build verification context by checking each criterion
    verification_context = []
    for mapping in terminology_mappings.get("terminology_mappings", []):
        crit_id = mapping.get("criterion_id", "")
        desc = mapping.get("criterion_description", "")
        domain = mapping.get("domain", "")

        # Check against catalog
        result = retrieval_service.verify_criterion(desc, domain=_normalize_domain(domain))
        
        # Explicitly mention which domain/CSV we are checking against for the UI
        checkpoint_msg = f"Checking {domain.upper()} domain (Catalog CSVs) for: {desc}"
        
        verification_context.append({
            "criterion_id": crit_id,
            "description": desc,
            "domain": domain,
            "verification_action": checkpoint_msg,
            "catalog_check": {
                "supported": result["supported"],
                "confidence": result["confidence"],
                "matches_found": len(result["matches"]),
                "top_matches": [
                    {
                        "concept_name": m.get("concept_name", ""),
                        "concept_id": m.get("concept_id", ""),
                        "vocabulary_id": m.get("vocabulary_id", ""),
                        "patient_count": m.get("distinct_persons", 0),
                    }
                    for m in result["matches"][:3]
                ],
            },
        })

    prompt = f"""Verify the following cohort definition against the EHR catalog.

COHORT DEFINITION:
{json.dumps(cohort_definition, indent=2)}

CATALOG VERIFICATION RESULTS FOR EACH CRITERION:
{json.dumps(verification_context, indent=2)}

EHR DATA SUMMARY:
{catalog_summary}

Assess each criterion and provide the verification result.
Respond with the JSON structure as specified in your instructions."""

    response = call_llm(prompt, system_prompt=system_prompt, expect_json=True)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "overall_status": "PARTIALLY_SUPPORTED",
            "criteria_verification": verification_context,
            "summary": "Verification completed with raw results",
            "raw_response": response,
        }

    return result


def _normalize_domain(domain: str) -> str:
    """Normalize domain string for retrieval service."""
    domain_map = {
        "condition": "conditions",
        "conditions": "conditions",
        "drug": "drugs",
        "drugs": "drugs",
        "medication": "drugs",
        "medications": "drugs",
        "procedure": "procedures",
        "procedures": "procedures",
        "measurement": "measurements",
        "measurements": "measurements",
        "lab": "measurements",
    }
    return domain_map.get(domain.lower(), None) if domain else None
