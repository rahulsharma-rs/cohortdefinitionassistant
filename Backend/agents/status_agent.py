"""
Status Agent — generates an intelligent, real-time activity status message
based on the current state of the backend LangGraph workflow.
"""
from services.llm_service import call_llm

def generate_status(state: dict) -> str:
    """
    Generate a dynamic, intelligent status message for the UI.
    """
    status = state.get("status", "unknown")
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", 3)
    
    # Infer the expected next action based on current status
    next_action_guess = "Processing"
    if status == "started": next_action_guess = "Inference Agent is preparing to analyze the request"
    elif status == "inference_complete": next_action_guess = "Expansion Agent is identifying relevant EHR dimensions"
    elif status == "expansion_complete": next_action_guess = "Drafting Agent is building the initial cohort structure"
    elif status == "drafting_complete": next_action_guess = "Grounding Agent is starting search in the EHR catalog"
    elif status == "refining": next_action_guess = "Grounding Agent is searching specific EHR domains"
    elif status == "refinement_finished": next_action_guess = "Terminology Agent is mapping criteria to standard codes"
    elif status == "terminology_complete": next_action_guess = "Verification Agent is validating logic against data"
    elif status == "verification_complete":
        overall = state.get("verification_results", {}).get("overall_status")
        if overall != "SUPPORTED" and iteration < max_iter:
            next_action_guess = f"Revision Agent is adjusting criteria for better support (Iteration {iteration + 1})"
        else:
            next_action_guess = "Finalizing the refined cohort definition"
    elif status == "revision_complete": next_action_guess = "Terminology Agent is re-mapping revised criteria to standard codes"

    # Grab recent reasoning steps to give the LLM context
    reasoning_steps = state.get("reasoning_steps", [])
    recent = reasoning_steps[-2:] if len(reasoning_steps) > 2 else reasoning_steps
    recent_text = "\n".join([f"- {r.get('step')}: {r.get('summary')}" for r in recent])

    prompt = f"""You are the UI narrator for an Agentic AI system building clinical cohorts.
The system just finished: '{status}'.
The likely next step is: '{next_action_guess}'.

Recent AI progress:
{recent_text}

Task: Write ONE short, highly descriptive sentence (max 10-12 words) describing what the AI is DOING NOW (the next step).
Rules:
1. Start with the Agent's name (e.g., "Expansion Agent is...", "Revision Agent is...").
2. Make it intelligent by referencing the specific data or action it's working on from the 'Recent AI progress'.
3. If it is revising, explicitly mention the iteration like "(Iteration {iteration + 1})".
4. Do not output anything else. No quotes.

Status Message:"""

    try:
        response = call_llm(prompt)
        response = response.strip().replace('"', '')
        return response + "..."
    except Exception:
        return next_action_guess + "..."
