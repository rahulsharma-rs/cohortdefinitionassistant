# Frontend — Cohort Refinement Assistant

React + Vite frontend with a Google-Drive-inspired design system.

## UI Architecture

### Components

| Component | File | Purpose |
|-----------|------|---------|
| `CohortInput` | `components/CohortInput.jsx` | Text area + "Refine Cohort" button with examples |
| `ProcessSteps` | `components/ProcessSteps.jsx` | Live pipeline progress tracker |
| `ClarificationPanel` | `components/ClarificationPanel.jsx` | Interactive Yes/No/Specify dialog |
| `RefinedCohortDisplay` | `components/RefinedCohortDisplay.jsx` | Structured cohort result cards |
| `ReasoningTrace` | `components/ReasoningTrace.jsx` | Collapsible reasoning step log |

### Pages

- `App.jsx` — Main page orchestrating all components with SSE state management

### Services

- `services/api.js` — API client using SSE for streaming pipeline updates

### Design System

- `styles/index.css` — Custom CSS variables, card components, animations
- Color palette: Google Drive blue/white/light grey
- Typography: Inter (Google Fonts)
- Shadows, hover effects, and micro-animations

## API Communication

The frontend uses **Server-Sent Events (SSE)** for real-time updates:

1. `POST /api/refine-cohort` initiates the pipeline
2. Each agent step sends an SSE event with status + reasoning
3. Final result arrives as a `type: "result"` event

Vite proxies `/api` requests to the Flask backend at `localhost:5000`.

## Development

```bash
npm install
npm run dev    # http://localhost:5173
npm run build  # Production build
```
