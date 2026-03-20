import React, { useState } from 'react';

/**
 * ClarificationPanel — interactive dialog for clarification questions.
 */
export default function ClarificationPanel({ question, onResponse }) {
  const [specifyText, setSpecifyText] = useState('');
  const [showSpecify, setShowSpecify] = useState(false);

  if (!question) return null;

  const handleSpecifySubmit = () => {
    if (specifyText.trim()) {
      onResponse(specifyText.trim());
      setShowSpecify(false);
      setSpecifyText('');
    }
  };

  return (
    <div className="card clarification-panel" id="clarification-panel">
      <div className="card__header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <div>
          <div className="card__title">Clarification Needed</div>
          <div className="card__subtitle">The system needs additional information</div>
        </div>
      </div>

      <div className="clarification-panel__question">{question}</div>

      {!showSpecify ? (
        <div className="clarification-panel__actions">
          <button className="btn btn--primary" onClick={() => onResponse('Yes')}>
            Yes
          </button>
          <button className="btn btn--secondary" onClick={() => onResponse('No')}>
            No
          </button>
          <button className="btn btn--secondary" onClick={() => setShowSpecify(true)}>
            Specify
          </button>
        </div>
      ) : (
        <div>
          <textarea
            className="cohort-input__textarea"
            value={specifyText}
            onChange={(e) => setSpecifyText(e.target.value)}
            placeholder="Provide additional details..."
            style={{ minHeight: '80px', marginBottom: '12px' }}
          />
          <div className="clarification-panel__actions">
            <button className="btn btn--primary" onClick={handleSpecifySubmit}>
              Submit
            </button>
            <button className="btn btn--secondary" onClick={() => setShowSpecify(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
