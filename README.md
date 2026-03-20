# AI Cohort Definition Refinement Assistant

An agentic AI system that refines natural language cohort definitions into structured, implementable definitions grounded in an OMOP-based EHR data catalog.

## Architecture

- **Frontend**: React + Vite — Google-Drive-inspired clean UI
- **Backend**: Python Flask with LangGraph orchestration
- **LLM**: Google Gemini (default) or OpenAI
- **Database**: SQLite (catalog data) + TF-IDF vector search

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- API key (Google or OpenAI) in `Backend/.env`

### Backend

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
cd Backend
pip install -r requirements.txt

# Start Flask server
python app.py
```

The backend starts on `http://localhost:5000` and automatically:
1. Initializes the SQLite database
2. Ingests all EHR catalog CSVs
3. Builds the TF-IDF vector search index

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

The frontend starts on `http://localhost:5173` with API calls proxied to Flask.

## How It Works

1. User enters a natural language cohort description
2. **Study Inference Agent** — infers study type, population, exposure, outcome
3. **Criteria Expansion Agent** — expands across 10 clinical dimensions
4. **Cohort Draft Agent** — produces structured inclusion/exclusion criteria
5. **Terminology Agent** — maps terms to ICD-10, SNOMED, LOINC, CPT, RxNorm
6. **Verification Agent** — checks feasibility against EHR catalog
7. **Revision Agent** — adjusts unsupported criteria (iterates up to 3 times)

## Project Structure

```
├── Backend/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── agents/             # 6 AI agents
│   ├── graphs/             # LangGraph orchestration
│   ├── services/           # LLM, catalog, vector, retrieval
│   ├── database/           # SQLite schema
│   ├── prompts/            # Editable prompt templates
│   └── catelogue/          # EHR catalog CSVs
└── Frontend/
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── services/       # API client
    │   └── styles/         # CSS design system
    └── vite.config.js
```
