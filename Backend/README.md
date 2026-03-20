# Backend — Cohort Refinement Assistant

Python Flask backend with LangGraph-orchestrated AI agents for cohort definition refinement.

## Agent Architecture

The system uses 6 specialized agents orchestrated via LangGraph:

| Agent | Prompt | Purpose |
|-------|--------|---------|
| `inference_agent` | `study_inference.txt` | Infer study type, population, exposure, outcome |
| `expansion_agent` | `criteria_expansion.txt` | Expand criteria across 10 dimensions |
| `drafting_agent` | `cohort_draft.txt` | Produce structured cohort definition |
| `terminology_agent` | — | Map terms to standard vocabularies |
| `verification_agent` | `ehr_verification.txt` | Verify against EHR catalog |
| `revision_agent` | `revision.txt` | Revise unsupported criteria |

## Catalog Ingestion

At startup, `catalog_service.py` reads all CSVs from `catelogue/`:
- Domain summary, vocabulary usage
- Standard concepts (conditions, drugs, procedures, devices, visits)
- Source code coverage (conditions, measurements, drugs, procedures, devices, visits)
- Demographic coverage (gender, race, ethnicity)
- Note/NLP presence

Data is loaded into SQLite for structured queries and a TF-IDF index for semantic search.

## Prompt System

All prompts are stored in `prompts/` as editable `.txt` files. Prompts use:
- **Graph-of-Thought**: Study inference (step-by-step reasoning)
- **Structured Output**: Criteria expansion, cohort drafting (JSON output)
- **ReAct**: Verification (tool usage + reasoning)

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/catalog/summary` | GET | EHR domain summary |
| `/api/refine-cohort` | POST | SSE streaming refinement |
| `/api/refine-cohort-sync` | POST | Synchronous refinement |

## Configuration

All settings in `.env`:
```
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
LLM_PROVIDER=google
LLM_MODEL=gemini-2.0-flash
SQLITE_DB_PATH=./database/cohort.db
```
