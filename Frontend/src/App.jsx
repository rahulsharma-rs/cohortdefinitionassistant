import React, { useState, useCallback } from 'react';
import CohortInput from './components/CohortInput';
import ProcessSteps from './components/ProcessSteps';
import ClarificationPanel from './components/ClarificationPanel';
import RefinedCohortDisplay from './components/RefinedCohortDisplay';
import ReasoningTrace from './components/ReasoningTrace';
import { refineCohortStreaming } from './services/api';

/**
 * Main App — orchestrates all components.
 */
export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [activeStep, setActiveStep] = useState(null);
  const [activeStatus, setActiveStatus] = useState(''); // New: for the flash status
  const [activeTabId, setActiveTabId] = useState('inference');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [stepSummaries, setStepSummaries] = useState({});
  const [reasoningSteps, setReasoningSteps] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [clarification, setClarification] = useState(null);

  const nodeToStep = {
    inference: 'inference',
    expansion: 'expansion',
    drafting: 'drafting',
    refinement: 'refinement', // Grounding tab
    terminology: 'terminology',
    verification: 'verification',
    revision: 'revision',
    finalize: 'finalize',
  };

  const handleSubmit = useCallback((userInput, model) => {
    // Reset state
    setIsLoading(true);
    setCompletedSteps([]);
    setActiveStep(null);
    setActiveStatus('');
    setActiveTabId('inference');
    setStepSummaries({});
    setReasoningSteps([]);
    setResult(null);
    setError(null);
    setClarification(null);

    const abort = refineCohortStreaming(
      userInput,
      model,
      // onStep
      (stepData) => {
        const node = stepData.node;
        const stepKey = nodeToStep[node] || node;

        // Update active step and status
        setActiveStep(stepKey);
        setActiveStatus(stepData.intelligent_status || "Processing...");
        setActiveTabId(stepKey); // Automatically switch to active step

        // Process reasoning steps
        if (stepData.reasoning_steps) {
          setReasoningSteps(stepData.reasoning_steps);

          // Mark completed steps
          const latest = stepData.reasoning_steps[stepData.reasoning_steps.length - 1];
          if (latest) {
            setStepSummaries((prev) => ({
              ...prev,
              [stepKey]: { summary: latest.summary, status: latest.status },
            }));

            if (latest.status === 'completed' || latest.status === 'failed') {
              setCompletedSteps((prev) => {
                if (prev.includes(stepKey)) return prev;
                return [...prev, stepKey];
              });
            }
          }
        }
      },
      // onResult
      (resultData) => {
        setIsLoading(false);
        setActiveStep(null);
        setActiveStatus('');
        setResult(resultData);
        setActiveTabId('results'); // Switch to results when done

        if (resultData.reasoning_steps) {
          setReasoningSteps(resultData.reasoning_steps);
        }
      },
      // onError
      (errorMsg) => {
        setIsLoading(false);
        setActiveStep(null);
        setActiveStatus('');
        setError(errorMsg);
      }
    );

    return abort;
  }, []);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-header__brand">
          <button 
            className="btn btn--secondary btn--small"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            title={isSidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isSidebarCollapsed ? '→' : '←'}
          </button>
          <div className="app-header__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <h1>AI Cohort Refinement Assistant</h1>
        </div>
        <div className="app-header-actions">
           {/* Placeholder for future header actions */}
        </div>
      </header>

      <div className="main-app-body">
        {/* Sidebar */}
        <aside className={`sidebar ${isSidebarCollapsed ? 'sidebar--collapsed' : ''}`}>
          <div className="sidebar-content">
            <CohortInput onSubmit={handleSubmit} isLoading={isLoading} />
            
            {clarification && (
              <ClarificationPanel
                question={clarification}
                onResponse={(response) => {
                  setClarification(null);
                }}
              />
            )}

            {error && (
              <div className="card" style={{ background: 'var(--color-error-bg)', borderColor: 'var(--color-error)', marginTop: 'var(--space-md)' }}>
                <div className="card__header">
                  <span style={{ fontSize: '1.2rem' }}>⚠️</span>
                  <div className="card__title" style={{ color: 'var(--color-error)' }}>Error</div>
                </div>
                <div className="card__subtitle">{error}</div>
              </div>
            )}
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="content-main">
          <ProcessSteps
            completedSteps={completedSteps}
            activeStep={activeStep}
            activeStatus={activeStatus}
            activeTabId={activeTabId}
            onTabChange={setActiveTabId}
            hasResult={!!result}
          />

          <div className="tab-content">
            {activeTabId === 'results' && result ? (
              <RefinedCohortDisplay result={result} />
            ) : (
              <ReasoningTrace 
                steps={reasoningSteps} 
                activeTabId={activeTabId} 
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
