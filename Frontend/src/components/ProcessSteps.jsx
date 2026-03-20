import React from 'react';

/**
 * Pipeline steps in order.
 */
const PIPELINE_STEPS = [
  { key: 'inference', label: 'Inference', icon: '🔍' },
  { key: 'expansion', label: 'Expansion', icon: '📋' },
  { key: 'drafting', label: 'Drafting', icon: '📝' },
  { key: 'refinement', label: 'Grounding', icon: '🎯' },
  { key: 'terminology', label: 'Terminology', icon: '🏷️' },
  { key: 'verification', label: 'Verification', icon: '✅' },
  { key: 'revision', label: 'Revision', icon: '🔄' },
];

/**
 * ProcessSteps — horizontal tab bar for the pipeline.
 */
export default function ProcessSteps({ 
  completedSteps, 
  activeStep, 
  activeTabId, 
  onTabChange, 
  hasResult,
  activeStatus // New prop for current activity description
}) {
  // Filter steps and add Results if available
  const visibleSteps = PIPELINE_STEPS.filter((step) => {
    if (step.key === 'revision' && !completedSteps.includes('revision') && activeStep !== 'revision') {
      return false;
    }
    if (step.key === 'refinement' && !completedSteps.includes('refinement') && activeStep !== 'refinement') {
      return false;
    }
    return true;
  });

  const tabs = [...visibleSteps];
  if (hasResult) {
    tabs.push({ key: 'results', label: 'Results', icon: '🎯' });
  }

  return (
    <div className="process-steps-container">
      {/* Real-time intelligent agent activity status positioned above the pipeline */}
      <div className="status-flash-wrapper">
        {activeStep && activeStatus && (
          <div className="status-flash">
            <span className="pulse-slow">●</span> {activeStatus}
          </div>
        )}
      </div>

      <div className="horizontal-pipeline">
        {tabs.map((tab, index) => {
          const isCompleted = completedSteps.includes(tab.key);
        const isActive = activeStep === tab.key;
        const isSelected = activeTabId === tab.key;
        
        return (
          <React.Fragment key={tab.key}>
            <div 
              className={`pipeline-tab ${isSelected ? 'pipeline-tab--active' : ''} ${isCompleted ? 'pipeline-tab--completed' : ''}`}
              onClick={() => onTabChange(tab.key)}
            >
              <div className={`pipeline-tab__dot ${isActive ? 'pulse-slow' : ''}`}>
                {isCompleted ? '✓' : index + 1}
              </div>
              <div className="pipeline-tab__title">
                {tab.label}
              </div>
            </div>
            {index < tabs.length - 1 && <div className="pipeline-connector" />}
          </React.Fragment>
        );
      })}
      </div>
    </div>
  );
}
