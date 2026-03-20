"""
Refinement Agent — sequentially refines a cohort definition by focusing on 
specific clinical domains and grounding them in catalog concepts.
"""
import json
import os
from services.llm_service import call_llm
from services.retrieval_service import RetrievalService

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "domain_refinement.txt")


def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run(
    cohort_definition: dict,
    target_domain: str,
    csv_description: str,
    retrieval_service: RetrievalService
) -> dict:
    """
    Refine a cohort definition for a specific domain.

    Args:
        cohort_definition: Current cohort definition.
        target_domain: Clinical domain to focus on (e.g., 'conditions').
        csv_description: Description of the specific CSV being used.
        retrieval_service: Hybrid retrieval service.

    Returns:
        Refinement results with thinking and updated definition.
    """
    system_prompt = load_prompt()

    # Retrieve concepts for all inclusion criteria in this domain
    retrieved_context = []
    for i, crit in enumerate(cohort_definition.get("inclusion_criteria", [])):
        # Handle both dict and string formats from LLM
        if isinstance(crit, str):
            crit = {"id": f"I{i+1}", "description": crit, "domain": ""}
        
        crit_domain = crit.get("domain", "")
        crit_desc = crit.get("description", "")
        
        if crit_domain.lower() == target_domain.lower() or target_domain.lower() in crit_desc.lower():
            # Normalize domain for retrieval
            domain_map = {
                "diagnoses": "conditions", "conditions": "conditions",
                "medications": "drugs", "drugs": "drugs",
                "measurements": "measurements", "procedures": "procedures",
                "devices": "devices", "visits": "visits",
            }
            search_domain = domain_map.get(target_domain.lower(), None)
            
            # Search for best matches
            search_res = retrieval_service.retrieve_concepts(crit_desc, domain=search_domain, top_k=5)
            retrieved_context.append({
                "criterion_id": crit.get("id", f"I{i+1}"),
                "draft_description": crit_desc,
                "top_catalog_matches": [
                    {
                        "concept_name": m.get("concept_name", ""),
                        "concept_id": m.get("concept_id", ""),
                        "vocabulary": m.get("vocabulary_id", ""),
                        "patient_count": m.get("distinct_persons", 0),
                        "similarity": m.get("similarity", 0)
                    } for m in search_res.get("matches", [])
                ]
            })

    prompt = f"""Refine the {target_domain.upper()} portion of this cohort definition.

TARGET CSV DESCRIPTION:
{csv_description}

CURRENT COHORT DRAFT:
{json.dumps(cohort_definition, indent=2)}

RETRIEVED CATALOG CONCEPTS FOR {target_domain.upper()}:
{json.dumps(retrieved_context, indent=2)}

Use this information to replace speculative terms with direct, implementable concepts from the catalog.
Respond with JSON as specified in instructions."""

    response = call_llm(prompt, system_prompt=system_prompt, expect_json=True)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "refinement_thinking": "Failed to parse refinement. Keeping original.",
            "refined_criteria": [],
            "updated_cohort_definition": cohort_definition
        }
