/** API client for backend communication. */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://graphprobe-ai-backend.onrender.com');

export const api = {
  /**
   * Generic API request handler
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    return response.json();
  },

  /**
   * Health check
   */
  async health() {
    return this.request('/api/health');
  },

  /**
   * Get configuration
   */
  async config() {
    return this.request('/api/config');
  },

  /**
   * Investigate a question
   */
  async investigate(question: string, pipeline: string) {
    return this.request('/api/investigate', {
      method: 'POST',
      body: JSON.stringify({ question, pipeline }),
    });
  },

  /**
   * Compare pipelines
   */
  async compare(question: string, pipelines: string[]) {
    return this.request('/api/compare', {
      method: 'POST',
      body: JSON.stringify({ question, pipelines }),
    });
  },

  /**
   * Run benchmark
   */
  async runBenchmark(pipelines?: string[], limit?: number, resumeFrom?: string) {
    const params = new URLSearchParams();
    if (pipelines) pipelines.forEach(p => params.append('pipelines', p));
    if (limit) params.append('limit', limit.toString());
    if (resumeFrom) params.append('resume_from', resumeFrom);
    
    return this.request(`/api/benchmark/run?${params.toString()}`, {
      method: 'POST',
    });
  },

  /**
   * Get benchmark results
   */
  async getBenchmarkResults() {
    return this.request('/api/benchmark/results');
  },

  /**
   * Get specific benchmark run
   */
  async getBenchmarkRun(runId: string) {
    return this.request(`/api/benchmark/${runId}`);
  },

  /**
   * Get benchmark metrics
   */
  async getBenchmarkMetrics(runId: string) {
    return this.request(`/api/benchmark/${runId}/metrics`);
  },

  /**
   * Get trace
   */
  async getTrace(runId: string) {
    return this.request(`/api/trace/${runId}`);
  },

  /**
   * Get evidence
   */
  async getEvidence(runId: string) {
    return this.request(`/api/evidence/${runId}`);
  },

  /**
   * Get evidence graph context
   */
  async getEvidenceGraph(runId: string) {
    return this.request(`/api/evidence/${runId}/graph`);
  },

  /**
   * Get metrics
   */
  async getMetrics() {
    return this.request('/api/metrics');
  },
};

export default api;
