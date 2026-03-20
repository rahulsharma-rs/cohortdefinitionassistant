// Frontend configuration
const config = {
  // API base URL — in dev mode, Vite proxies /api to Flask backend
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',

  // SSE endpoint for streaming cohort refinement
  REFINE_ENDPOINT: '/api/refine-cohort',

  // Sync endpoint (fallback)
  REFINE_SYNC_ENDPOINT: '/api/refine-cohort-sync',

  // Health check
  HEALTH_ENDPOINT: '/api/health',

  // Catalog summary
  CATALOG_ENDPOINT: '/api/catalog/summary',
};

export default config;
