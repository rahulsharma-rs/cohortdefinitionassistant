"""
Flask application for the Cohort Refinement Assistant.
Provides SSE-based streaming endpoint for real-time pipeline status.
"""
import json
import sys
import os

# Ensure backend directory is on import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from config import Config
from database.db import init_db
from services.catalog_service import CatalogService
from services.vector_service import VectorService
from services.retrieval_service import RetrievalService
from graphs.cohort_graph import run_cohort_refinement
from agents.status_agent import generate_status

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# ── Initialize services on startup ───────────────────────────────────────────

catalog_service = None
vector_service = None
retrieval_service = None


def startup():
    """Initialize database, ingest catalog, and build vector index."""
    global catalog_service, vector_service, retrieval_service

    print("=" * 60)
    print("  Cohort Refinement Assistant — Starting up")
    print("=" * 60)

    # 1. Initialize database
    print("\n[1/3] Initializing database...")
    init_db()
    print("  [OK] Database initialized")

    # 2. Ingest catalog CSVs
    print("\n[2/3] Ingesting EHR catalog...")
    catalog_service = CatalogService()
    catalog_service.ingest_all()

    # 3. Build vector index
    print("\n[3/3] Building vector search index...")
    vector_service = VectorService()
    vector_service.build_index()

    # 4. Create retrieval service
    retrieval_service = RetrievalService(catalog_service, vector_service)

    print("\n" + "=" * 60)
    print("  Startup complete! Server ready.")
    print("=" * 60 + "\n")


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "cohort-refinement-assistant"})


@app.route("/api/catalog/summary", methods=["GET"])
def get_catalog_summary():
    """Return EHR catalog domain summary."""
    if catalog_service:
        summary = catalog_service.get_domain_summary()
        return jsonify({"summary": summary})
    return jsonify({"error": "Catalog not loaded"}), 503


@app.route("/api/refine-cohort", methods=["POST"])
def refine_cohort():
    """
    Main endpoint: refine a cohort definition.
    Accepts JSON with 'user_input' string.
    Returns Server-Sent Events for streaming progress.
    """
    data = request.get_json()
    if not data or "user_input" not in data:
        return jsonify({"error": "Missing 'user_input' field"}), 400

    user_input = data["user_input"].strip()
    if not user_input:
        return jsonify({"error": "'user_input' cannot be empty"}), 400

    def generate():
        """SSE generator for streaming workflow updates."""
        final_state = {}

        try:
            for state_update in run_cohort_refinement(user_input):
                # state_update is a dict with the node name as key
                for node_name, node_state in state_update.items():
                    # Generate intelligent status for the next likely action
                    intelligent_status = generate_status(node_state)
                    
                    # Send step update
                    event_data = {
                        "node": node_name,
                        "status": node_state.get("status", ""),
                        "reasoning_steps": node_state.get("reasoning_steps", []),
                        "intelligent_status": intelligent_status,
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"

                    # Track latest state
                    final_state.update(node_state)

            # Send final result
            result = {
                "type": "result",
                "refined_definition": final_state.get("cohort_definition", {}),
                "reasoning_steps": final_state.get("reasoning_steps", []),
                "verification_status": final_state.get("verification_results", {}),
                "terminology_mappings": final_state.get("terminology_mappings", {}),
                "revision_history": final_state.get("revision_history", []),
                "status": final_state.get("status", "completed"),
            }
            yield f"data: {json.dumps(result)}\n\n"

        except Exception as e:
            error_data = {
                "type": "error",
                "error": str(e),
                "reasoning_steps": final_state.get("reasoning_steps", []),
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/refine-cohort-sync", methods=["POST"])
def refine_cohort_sync():
    """
    Synchronous version of the refinement endpoint.
    Returns the full result at once (useful for testing).
    """
    data = request.get_json()
    if not data or "user_input" not in data:
        return jsonify({"error": "Missing 'user_input' field"}), 400

    user_input = data["user_input"].strip()
    if not user_input:
        return jsonify({"error": "'user_input' cannot be empty"}), 400

    final_state = {}
    try:
        for state_update in run_cohort_refinement(user_input):
            for node_name, node_state in state_update.items():
                final_state.update(node_state)

        return jsonify({
            "refined_definition": final_state.get("cohort_definition", {}),
            "reasoning_steps": final_state.get("reasoning_steps", []),
            "verification_status": final_state.get("verification_results", {}),
            "terminology_mappings": final_state.get("terminology_mappings", {}),
            "revision_history": final_state.get("revision_history", []),
            "status": final_state.get("status", "completed"),
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "reasoning_steps": final_state.get("reasoning_steps", []),
        }), 500


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    startup()
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )
