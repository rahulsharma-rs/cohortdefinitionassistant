"""
Terminology Mapping Agent — maps clinical terms in the cohort definition
to standard vocabularies (ICD-10, SNOMED, LOINC, CPT, RxNorm) using
the retrieval service.
"""
import json
from services.retrieval_service import RetrievalService


def run(cohort_definition: dict, retrieval_service: RetrievalService) -> dict:
    """
    Map all clinical terms in the cohort definition to standard codes.

    Args:
        cohort_definition: Structured cohort definition from drafting agent.
        retrieval_service: Hybrid retrieval service instance.

    Returns:
        Dict of terminology mappings for each criterion.
    """
    mappings = []

    # Map inclusion criteria
    for i, criterion in enumerate(cohort_definition.get("inclusion_criteria", [])):
        # Handle both dict and string formats from LLM
        if isinstance(criterion, str):
            criterion = {"id": f"I{i+1}", "description": criterion, "domain": ""}
        mapping = _map_criterion(criterion, retrieval_service)
        mappings.append(mapping)

    # Map exclusion criteria
    for i, criterion in enumerate(cohort_definition.get("exclusion_criteria", [])):
        if isinstance(criterion, str):
            criterion = {"id": f"E{i+1}", "description": criterion, "domain": ""}
        mapping = _map_criterion(criterion, retrieval_service)
        mappings.append(mapping)

    # Map index event
    index_event = cohort_definition.get("index_event", {})
    if index_event.get("description"):
        index_mapping = _map_criterion(
            {"id": "INDEX", "description": index_event["description"], "domain": index_event.get("domain", "")},
            retrieval_service,
        )
        mappings.append(index_mapping)

    return {
        "terminology_mappings": mappings,
        "total_criteria_mapped": len(mappings),
        "fully_mapped": sum(1 for m in mappings if m.get("mapped_concepts")),
    }


def _map_criterion(criterion: dict, retrieval_service: RetrievalService) -> dict:
    """Map a single criterion to standard terminology."""
    description = criterion.get("description", "")
    domain = criterion.get("domain", "")
    criterion_id = criterion.get("id", "")

    # Determine search domain
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
        "visit": None,
        "demographic": None,
    }
    search_domain = domain_map.get(domain.lower(), None)

    # Search for matching concepts
    results = retrieval_service.retrieve_concepts(
        description, domain=search_domain, top_k=5
    )

    mapped_concepts = []
    for match in results.get("matches", []):
        mapped_concepts.append({
            "concept_name": match.get("concept_name", ""),
            "concept_id": match.get("concept_id"),
            "concept_code": match.get("concept_code", ""),
            "vocabulary_id": match.get("vocabulary_id", ""),
            "match_type": match.get("match_type", ""),
            "patient_count": match.get("distinct_persons", 0),
        })

    return {
        "criterion_id": criterion_id,
        "criterion_description": description,
        "domain": domain,
        "mapped_concepts": mapped_concepts,
        "is_mapped": len(mapped_concepts) > 0,
    }
