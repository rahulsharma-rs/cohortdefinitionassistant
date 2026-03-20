import React from 'react';

/**
 * RefinedCohortDisplay — card-based display of the final refined cohort.
 */
export default function RefinedCohortDisplay({ result }) {
  if (!result) return null;

  const definition = result.refined_definition || {};
  const verification = result.verification_status || {};
  const terminology = result.terminology_mappings || {};

  return (
    <div className="card refined-cohort" id="refined-cohort-display">
      <div className="card__header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <div>
          <div className="card__title">Refined Cohort Definition</div>
          <div className="card__subtitle">
            {verification.overall_status && (
              <VerificationBadge status={verification.overall_status} />
            )}
          </div>
        </div>
      </div>

      {/* Natural Language Summary */}
      {definition.human_readable_summary && (
        <Section title="Cohort Summary">
          <div className="refined-cohort__objective" style={{ background: 'var(--color-surface)', borderLeft: '3px solid var(--color-success)', fontStyle: 'italic' }}>
            {definition.human_readable_summary}
          </div>
        </Section>
      )}

      {/* Study Objective */}
      {definition.study_objective && (
        <Section title="Study Objective">
          <div className="refined-cohort__objective">{definition.study_objective}</div>
        </Section>
      )}

      {/* Inclusion Criteria */}
      {definition.inclusion_criteria?.length > 0 && (
        <Section title="Inclusion Criteria">
          <CriteriaList criteria={definition.inclusion_criteria} />
        </Section>
      )}

      {/* Exclusion Criteria */}
      {definition.exclusion_criteria?.length > 0 && (
        <Section title="Exclusion Criteria">
          <CriteriaList criteria={definition.exclusion_criteria} />
        </Section>
      )}

      {/* Index Event */}
      {definition.index_event && (
        <Section title="Index Event">
          <div className="refined-cohort__objective">
            {definition.index_event.description}
            {definition.index_event.domain && (
              <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
                {' '} — Domain: {definition.index_event.domain}
              </span>
            )}
          </div>
        </Section>
      )}

      {/* Temporal Logic */}
      {definition.temporal_logic?.length > 0 && (
        <Section title="Temporal Logic">
          <ul className="criteria-list">
            {definition.temporal_logic.map((rule, i) => (
              <li key={i} className="criterion">
                <span className="criterion__id">T{i + 1}</span>
                <div>
                  <div className="criterion__text">{rule.rule}</div>
                  {rule.criteria_ids?.length > 0 && (
                    <div className="criterion__temporal">
                      Applies to: {rule.criteria_ids.join(', ')}
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Windows */}
      {(definition.baseline_window || definition.followup_window) && (
        <Section title="Observation Windows">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {definition.baseline_window && (
              <div style={{
                background: 'var(--color-info-bg)',
                padding: '12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.875rem',
              }}>
                <div style={{ fontWeight: 600, color: 'var(--color-info)', marginBottom: '4px' }}>
                  Baseline Window
                </div>
                <div>{definition.baseline_window.days_before_index} days before index</div>
                {definition.baseline_window.description && (
                  <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
                    {definition.baseline_window.description}
                  </div>
                )}
              </div>
            )}
            {definition.followup_window && (
              <div style={{
                background: 'var(--color-success-bg)',
                padding: '12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.875rem',
              }}>
                <div style={{ fontWeight: 600, color: 'var(--color-success)', marginBottom: '4px' }}>
                  Follow-up Window
                </div>
                <div>{definition.followup_window.days_after_index} days after index</div>
                {definition.followup_window.description && (
                  <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
                    {definition.followup_window.description}
                  </div>
                )}
              </div>
            )}
          </div>
        </Section>
      )}

      {/* Terminology Mappings */}
      {terminology.terminology_mappings?.length > 0 && (
        <Section title="Terminology Mappings">
          <div style={{ overflowX: 'auto' }}>
            <table className="terminology-table">
              <thead>
                <tr>
                  <th>Criterion</th>
                  <th>Concept</th>
                  <th>Code</th>
                  <th>Vocabulary</th>
                  <th>Patients</th>
                </tr>
              </thead>
              <tbody>
                {terminology.terminology_mappings
                  .filter((m) => m.mapped_concepts?.length > 0)
                  .map((mapping, i) => (
                    mapping.mapped_concepts.slice(0, 2).map((concept, j) => (
                      <tr key={`${i}-${j}`}>
                        {j === 0 && (
                          <td rowSpan={Math.min(mapping.mapped_concepts.length, 2)} style={{ fontWeight: 500 }}>
                            {mapping.criterion_id}
                          </td>
                        )}
                        <td>{concept.concept_name}</td>
                        <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                          {concept.concept_code}
                        </td>
                        <td>{concept.vocabulary_id}</td>
                        <td>{concept.patient_count?.toLocaleString() || '—'}</td>
                      </tr>
                    ))
                  ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {/* Verification Results */}
      {verification.criteria_verification?.length > 0 && (
        <Section title="Verification Results">
          {verification.criteria_verification.map((crit, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '8px',
              margin: '8px 0',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--color-bg)',
            }}>
              <VerificationBadge status={crit.status} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500, fontSize: '0.875rem' }}>
                  {crit.criterion_id}: {crit.criterion_description}
                </div>
                {crit.issues?.length > 0 && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    {crit.issues.join('; ')}
                  </div>
                )}
                {crit.suggestions?.length > 0 && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-info)', marginTop: '2px' }}>
                    💡 {crit.suggestions.join('; ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          {verification.summary && (
            <div style={{
              marginTop: '12px',
              padding: '12px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-info-bg)',
              fontSize: '0.875rem',
              color: 'var(--color-text-primary)',
            }}>
              <strong>Summary:</strong> {verification.summary}
            </div>
          )}
        </Section>
      )}
    </div>
  );
}

/* ── Helper Components ──────────────────────────────────────────── */

function Section({ title, children }) {
  return (
    <div className="refined-cohort__section">
      <div className="refined-cohort__section-title">{title}</div>
      {children}
    </div>
  );
}

function CriteriaList({ criteria }) {
  return (
    <ul className="criteria-list">
      {criteria.map((crit, i) => (
        <li key={i} className={`criterion ${crit.revised ? 'criterion--revised' : ''}`}>
          <span className="criterion__id">{crit.id}</span>
          <div>
            <div className="criterion__text">{crit.description}</div>
            {crit.temporal && (
              <div className="criterion__temporal">⏱ {crit.temporal}</div>
            )}
            {crit.revision_note && (
              <div className="criterion__revision-note">📝 {crit.revision_note}</div>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}

function VerificationBadge({ status }) {
  const normalized = (status || '').toUpperCase().replace(/ /g, '_');
  let className = 'verification-badge--supported';
  let label = status;

  if (normalized.includes('NOT_SUPPORTED')) {
    className = 'verification-badge--unsupported';
    label = 'Not Supported';
  } else if (normalized.includes('PARTIAL') || normalized.includes('NEEDS_MODIFICATION')) {
    className = 'verification-badge--partial';
    label = normalized.includes('PARTIAL') ? 'Partially Supported' : 'Needs Modification';
  } else {
    label = 'Supported';
  }

  return <span className={`verification-badge ${className}`}>{label}</span>;
}
