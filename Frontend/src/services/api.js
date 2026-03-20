/**
 * API service — handles communication with Flask backend.
 * Uses SSE (Server-Sent Events) for streaming pipeline progress.
 */
import config from '../config';

/**
 * Refine a cohort definition using the streaming SSE endpoint.
 *
 * @param {string} userInput - The natural language cohort description.
 * @param {function} onStep - Callback for each pipeline step update: (stepData) => void
 * @param {function} onResult - Callback for the final result: (result) => void
 * @param {function} onError - Callback for errors: (error) => void
 * @returns {function} abort function to cancel the request
 */
export function refineCohortStreaming(userInput, model, onStep, onResult, onError) {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(config.REFINE_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput, model: model }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        onError(errData.error || `HTTP ${response.status}`);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'result') {
                onResult(data);
              } else if (data.type === 'error') {
                onError(data.error);
              } else {
                onStep(data);
              }
            } catch {
              // Skip unparseable lines
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        onError(err.message);
      }
    }
  })();

  return () => controller.abort();
}

/**
 * Refine a cohort definition using the synchronous endpoint (fallback).
 */
export async function refineCohortSync(userInput, model) {
  const response = await fetch(config.REFINE_SYNC_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput, model: model }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.error || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Health check.
 */
export async function checkHealth() {
  const response = await fetch(config.HEALTH_ENDPOINT);
  return response.json();
}
