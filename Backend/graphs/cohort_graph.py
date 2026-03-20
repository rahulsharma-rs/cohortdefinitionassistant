"""
LangGraph orchestration for the cohort refinement workflow.

Workflow:
  user_input → inference → expansion → drafting → terminology → verification
                                                                    ├── supported → finalize
                                                                    └── unsupported → revision → (loop back to drafting)
"""
import json
from typing import TypedDict, Annotated, Any
from langgraph.graph import StateGraph, END

from agents import (
    inference_agent,
    expansion_agent,
    drafting_agent,
    terminology_agent,
    verification_agent,
    revision_agent,
)
from services.catalog_service import CatalogService
from services.vector_service import VectorService
from services.retrieval_service import RetrievalService
from config import Config


# ── State Schema ──────────────────────────────────────────────────────────────

class CohortState(TypedDict):
    """State flowing through the cohort refinement graph."""
    user_input: str
    study_inference: dict
    expanded_criteria: dict
    cohort_definition: dict
    terminology_mappings: dict
    verification_results: dict
    targeted_domains: list  # List of {domain, csv_id, reason}
    refinement_index: int   # Current domain being refined
    revision_history: list
    reasoning_steps: list
    iteration: int
    max_iterations: int
    status: str
    error: str


# ── Shared services (initialized once) ───────────────────────────────────────

_catalog_service = None
_vector_service = None
_retrieval_service = None


def _init_services():
    global _catalog_service, _vector_service, _retrieval_service
    if _catalog_service is None:
        _catalog_service = CatalogService()
        _vector_service = VectorService()
        if not _vector_service.is_built:
            _vector_service.build_index()
        _retrieval_service = RetrievalService(_catalog_service, _vector_service)
    return _catalog_service, _vector_service, _retrieval_service


# ── Node Functions ────────────────────────────────────────────────────────────

def inference_node(state: CohortState) -> dict:
    """Run study inference agent."""
    try:
        result = inference_agent.run(state["user_input"])
        return {
            "study_inference": result,
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Study Inference",
                "status": "completed",
                "summary": f"Study type: {result.get('study_type', 'Unknown')}. "
                          f"Target: {result.get('target_population', 'Unknown')}.",
            }],
            "status": "inference_complete",
        }
    except Exception as e:
        return {
            "error": f"Inference failed: {str(e)}",
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Study Inference",
                "status": "failed",
                "summary": str(e),
            }],
        }


def expansion_node(state: CohortState) -> dict:
    """Run criteria expansion agent."""
    catalog_svc, _, _ = _init_services()
    try:
        domain_summary = catalog_svc.get_domain_summary()
        catalog_desc = catalog_svc.get_catalog_description()
        summary_text = f"EHR Catalog Summary:\n{json.dumps(domain_summary[:10], indent=2)}\n\nCatalog Description:\n{catalog_desc[:3000]}"

        result = expansion_agent.run(
            state["user_input"],
            state["study_inference"],
            summary_text,
        )
        return {
            "expanded_criteria": result,
            "targeted_domains": result.get("targeted_csvs", []),
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Criteria Expansion",
                "status": "completed",
                "summary": f"Expanded criteria and identified {len(result.get('targeted_csvs', []))} relevant catalog domains for grounding.",
            }],
            "status": "expansion_complete",
        }
    except Exception as e:
        return {
            "error": f"Expansion failed: {str(e)}",
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Criteria Expansion",
                "status": "failed",
                "summary": str(e),
            }],
        }


def drafting_node(state: CohortState) -> dict:
    """Run cohort drafting agent."""
    try:
        result = drafting_agent.run(
            state["user_input"],
            state["study_inference"],
            state["expanded_criteria"],
        )
        return {
            "cohort_definition": result,
            "refinement_index": 0,
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Initial Draft",
                "status": "completed",
                "summary": f"Generated initial speculative draft. Starting targeted grounding in EHR domains.",
            }],
            "status": "drafting_complete",
        }
    except Exception as e:
        return {
            "error": f"Drafting failed: {str(e)}",
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Cohort Drafting",
                "status": "failed",
                "summary": str(e),
            }],
        }


def refinement_node(state: CohortState) -> dict:
    """Run sequential refinement for a specific domain."""
    from agents import refinement_agent
    catalog_svc, _, retrieval_svc = _init_services()
    
    idx = state["refinement_index"]
    domains = state["targeted_domains"]
    
    if idx >= len(domains):
        return {"status": "refinement_finished"}
        
    target = domains[idx]
    domain_name = target.get("dimension", "general")
    csv_id = target.get("csv_id", "unknown")
    
    try:
        # Get description for this specific CSV if possible, or use general
        catalog_desc = catalog_svc.get_catalog_description()
        
        result = refinement_agent.run(
            state["cohort_definition"],
            domain_name,
            f"CSV: {csv_id}. Reason: {target.get('reason')}",
            retrieval_svc
        )
        
        updated_def = result.get("updated_cohort_definition", state["cohort_definition"])
        
        return {
            "cohort_definition": updated_def,
            "refinement_index": idx + 1,
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": f"Refinement: {domain_name}",
                "status": "completed",
                "summary": f"Grounded criteria into {csv_id}. {result.get('refinement_thinking', '')}",
            }],
            "status": "refining",
        }
    except Exception as e:
        return {
            "refinement_index": idx + 1,
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": f"Refinement: {domain_name}",
                "status": "skipped",
                "summary": f"Failed to refine: {str(e)}",
            }],
        }


def terminology_node(state: CohortState) -> dict:
    """Run terminology mapping agent."""
    _, _, retrieval_svc = _init_services()
    try:
        result = terminology_agent.run(
            state["cohort_definition"],
            retrieval_svc,
        )
        return {
            "terminology_mappings": result,
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Terminology Mapping",
                "status": "completed",
                "summary": f"Mapped {result.get('fully_mapped', 0)}/{result.get('total_criteria_mapped', 0)} "
                          f"criteria to standard vocabularies.",
            }],
            "status": "terminology_complete",
        }
    except Exception as e:
        return {
            "error": f"Terminology mapping failed: {str(e)}",
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Terminology Mapping",
                "status": "failed",
                "summary": str(e),
            }],
        }


def verification_node(state: CohortState) -> dict:
    """Run EHR verification agent."""
    catalog_svc, _, retrieval_svc = _init_services()
    try:
        domain_summary = catalog_svc.get_domain_summary()
        catalog_desc = catalog_svc.get_catalog_description()
        summary_text = f"Domain Summary:\n{json.dumps(domain_summary[:10], indent=2)}\n\nCatalog:\n{catalog_desc[:2000]}"

        result = verification_agent.run(
            state["cohort_definition"],
            state["terminology_mappings"],
            retrieval_svc,
            summary_text,
        )
        return {
            "verification_results": result,
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "Final EHR Verification",
                "status": "completed",
                "summary": f"Overall status: {result.get('overall_status', 'Unknown')}. {result.get('summary', '')}",
            }],
            "status": "verification_complete",
        }
    except Exception as e:
        return {
            "error": f"Verification failed: {str(e)}",
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": "EHR Verification",
                "status": "failed",
                "summary": str(e),
            }],
        }


def revision_node(state: CohortState) -> dict:
    """Run revision agent to fix unsupported criteria."""
    catalog_svc, _, _ = _init_services()
    try:
        domain_summary = catalog_svc.get_domain_summary()
        catalog_desc = catalog_svc.get_catalog_description()
        summary_text = f"Domain Summary:\n{json.dumps(domain_summary[:10], indent=2)}\n\n{catalog_desc[:2000]}"

        result = revision_agent.run(
            state["cohort_definition"],
            state["verification_results"],
            summary_text,
        )

        revised_def = result.get("revised_definition", state["cohort_definition"])
        changes = result.get("changes_made", [])

        return {
            "cohort_definition": revised_def,
            "revision_history": state["revision_history"] + [{
                "iteration": state["iteration"],
                "changes": changes,
                "remaining_issues": result.get("remaining_issues", []),
            }],
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": f"Revision (iteration {state['iteration']})",
                "status": "completed",
                "summary": f"Made {len(changes)} revisions to unsupported criteria.",
            }],
            "iteration": state["iteration"] + 1,
            "status": "revision_complete",
        }
    except Exception as e:
        return {
            "error": f"Revision failed: {str(e)}",
            "reasoning_steps": state["reasoning_steps"] + [{
                "step": f"Revision (iteration {state['iteration']})",
                "status": "failed",
                "summary": str(e),
            }],
        }


def finalize_node(state: CohortState) -> dict:
    """Finalize the cohort definition."""
    return {
        "status": "finalized",
        "reasoning_steps": state["reasoning_steps"] + [{
            "step": "Finalization",
            "status": "completed",
            "summary": "Cohort definition finalized and grounded in real EHR data.",
        }],
    }


# ── Routing ───────────────────────────────────────────────────────────────────

def should_refine(state: CohortState) -> str:
    """Decide whether to continue refinement or move to terminology."""
    if state["refinement_index"] < len(state["targeted_domains"]):
        return "refine"
    return "terminology"


def should_revise(state: CohortState) -> str:
    """Decide whether to revise or finalize based on verification."""
    if state.get("error"):
        return "finalize"

    verification = state.get("verification_results", {})
    overall_status = verification.get("overall_status", "SUPPORTED")

    if overall_status == "SUPPORTED":
        return "finalize"

    if state["iteration"] >= state["max_iterations"]:
        return "finalize"

    return "revise"


# ── Graph Construction ────────────────────────────────────────────────────────

def build_graph():
    """Build and compile the LangGraph cohort refinement graph."""
    graph = StateGraph(CohortState)

    # Add nodes
    graph.add_node("inference", inference_node)
    graph.add_node("expansion", expansion_node)
    graph.add_node("drafting", drafting_node)
    graph.add_node("refinement", refinement_node)
    graph.add_node("terminology", terminology_node)
    graph.add_node("verification", verification_node)
    graph.add_node("revision", revision_node)
    graph.add_node("finalize", finalize_node)

    # Add edges
    graph.set_entry_point("inference")
    graph.add_edge("inference", "expansion")
    graph.add_edge("expansion", "drafting")
    
    # Sequential Refinement Loop
    graph.add_conditional_edges(
        "drafting",
        should_refine,
        {"refine": "refinement", "terminology": "terminology"}
    )
    graph.add_conditional_edges(
        "refinement",
        should_refine,
        {"refine": "refinement", "terminology": "terminology"}
    )

    graph.add_edge("terminology", "verification")

    # Conditional: revise or finalize
    graph.add_conditional_edges(
        "verification",
        should_revise,
        {
            "revise": "revision",
            "finalize": "finalize",
        },
    )

    # After revision, loop back to terminology mapping
    graph.add_edge("revision", "terminology")

    # Finalize ends the graph
    graph.add_edge("finalize", END)

    return graph.compile()


def run_cohort_refinement(user_input: str):
    """
    Run the full cohort refinement workflow.

    Args:
        user_input: Natural language cohort definition.

    Yields:
        State updates as the workflow progresses.
    """
    graph = build_graph()

    initial_state = CohortState(
        user_input=user_input,
        study_inference={},
        expanded_criteria={},
        cohort_definition={},
        terminology_mappings={},
        verification_results={},
        targeted_domains=[],
        refinement_index=0,
        revision_history=[],
        reasoning_steps=[],
        iteration=0,
        max_iterations=Config.MAX_REVISION_ITERATIONS,
        status="started",
        error="",
    )

    # Stream state updates
    for state_update in graph.stream(initial_state):
        yield state_update
