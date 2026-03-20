import React, { useState } from 'react';

/**
 * CohortInput — text area + "Refine Cohort" button.
 */
export default function CohortInput({ onSubmit, isLoading }) {
  const [input, setInput] = useState('');
  const [model, setModel] = useState('gpt-5-nano');

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (trimmed && !isLoading) {
      onSubmit(trimmed, model);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.metaKey) {
      handleSubmit();
    }
  };

  const examples = [
    'Adults aged 18 and older with type 2 diabetes who were prescribed metformin and developed acute kidney injury within 1 year',
    'Patients with essential hypertension who received at least one antihypertensive medication and had a follow-up visit within 6 months',
    'Adults receiving vancomycin who developed nephrotoxicity, excluding patients with pre-existing chronic kidney disease',
  ];

  return (
    <div className="card cohort-input" id="cohort-input-card">
      <div className="card__header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
        <div>
          <div className="card__title">Cohort Definition</div>
          <div className="card__subtitle">Describe the cohort you want to build in natural language</div>
        </div>
      </div>

      <div style={{ marginBottom: '12px' }}>
        <label htmlFor="model-select" style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--color-text-secondary)', display: 'block', marginBottom: '4px' }}>AI Model:</label>
        <select 
          id="model-select" 
          value={model} 
          onChange={(e) => setModel(e.target.value)}
          disabled={isLoading}
          style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg)', color: 'var(--color-text)' }}
        >
          <option value="gpt-5-nano">GPT-5 Nano (OpenAI)</option>
          <option value="gemini-3.1-flash-lite-preview">Gemini 3.1 Flash-Lite Preview</option>
        </select>
      </div>

      <textarea
        id="cohort-definition-input"
        className="cohort-input__textarea"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Describe the cohort you want to build..."
        disabled={isLoading}
      />

      <div style={{ marginTop: '8px', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)' }}>
          Try an example:
        </span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
          {examples.map((ex, i) => (
            <button
              key={i}
              className="btn btn--secondary btn--small"
              onClick={() => setInput(ex)}
              disabled={isLoading}
              style={{ textAlign: 'left', fontSize: '0.75rem', maxWidth: '100%' }}
            >
              {ex.length > 80 ? ex.slice(0, 80) + '…' : ex}
            </button>
          ))}
        </div>
      </div>

      <div className="cohort-input__actions">
        <button
          className="btn btn--secondary"
          onClick={() => setInput('')}
          disabled={isLoading || !input}
        >
          Clear
        </button>
        <button
          id="refine-cohort-btn"
          className="btn btn--primary"
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
        >
          {isLoading && <span className="btn__spinner" />}
          {isLoading ? 'Refining…' : 'Refine Cohort'}
        </button>
      </div>
    </div>
  );
}
