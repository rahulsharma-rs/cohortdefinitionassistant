import React from 'react';

/**
 * ReasoningTrace — Displays transparent reasoning steps for the pipeline.
 */
export default function ReasoningTrace({ steps, activeTabId }) {
  if (!steps || steps.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: 'var(--space-2xl)', color: 'var(--color-text-tertiary)' }}>
        <p>Start refinement to see clinical reasoning steps...</p>
      </div>
    );
  }

  // Filter steps by activeTabId if it matches a step name, 
  // or show all for better visibility if tab switching is fast.
  // Given the requirement, we'll show all but highlight or focus? 
  // User asked for "each point in this panel as tab". 
  // So when a tab is clicked, we should strictly show that step's reasoning if possible.
  
  const filteredSteps = steps.filter(s => {
    if (!activeTabId) return true;

    // Map tab keys to strings found within the reasoning step names
    const matchMap = {
      inference: 'Inference',
      expansion: 'Expansion',
      drafting: 'Draft',
      refinement: 'Refinement',
      terminology: 'Terminology',
      verification: 'Verification',
      revision: 'Revision'
    };

    const searchStr = matchMap[activeTabId];
    if (!searchStr) return false;

    return s.step.toLowerCase().includes(searchStr.toLowerCase());
  });

  return (
    <div className="reasoning-trace-container">
      <ul className="reasoning-trace__list" style={{ borderLeft: 'none', marginLeft: 0 }}>
        {filteredSteps.length > 0 ? (
          filteredSteps.map((step, i) => (
            <li key={i} className="card reasoning-trace__item" style={{ marginBottom: 'var(--space-md)' }}>
              <div className="card__header">
                <div className={`process-step__icon ${step.status === 'completed' ? 'process-step__icon--completed' : step.status === 'failed' ? 'process-step__icon--failed' : 'process-step__icon--active'}`} style={{ width: 20, height: 20, fontSize: '0.6rem' }}>
                  {step.status === 'completed' ? '✓' : step.status === 'failed' ? '✕' : '●'}
                </div>
                <div className="card__title" style={{ fontSize: '0.9rem' }}>{step.step}</div>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                {step.summary}
              </p>
              {step.status === 'failed' && (
                <div style={{ color: 'var(--color-error)', fontSize: '0.8rem', marginTop: 'var(--space-sm)' }}>
                  ⚠️ {step.error || 'Step failed'}
                </div>
              )}
            </li>
          ))
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: 'var(--space-2xl)', color: 'var(--color-text-tertiary)' }}>
            <p>No reasoning steps recorded for this stage yet.</p>
          </div>
        )}
      </ul>
    </div>
  );
}
