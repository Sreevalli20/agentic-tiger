import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../services/api'

export default function Metrics() {
  const [benchmarkRuns, setBenchmarkRuns] = useState<any[]>([])
  const [selectedRun, setSelectedRun] = useState<string | null>(null)
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadBenchmarkRuns()
  }, [])

  const loadBenchmarkRuns = async () => {
    try {
      setLoading(true)
      const data = await api.getBenchmarkResults() as any
      setBenchmarkRuns(data.runs || [])
      
      // Auto-select the most recent run
      if (data.runs && data.runs.length > 0) {
        const latestRun = data.runs[0]
        setSelectedRun(latestRun.run_id)
        loadMetrics(latestRun.run_id)
      }
    } catch (error) {
      console.error('Failed to load benchmark runs:', error)
      setError(error instanceof Error ? error.message : 'Failed to load benchmark data')
    } finally {
      setLoading(false)
    }
  }

  const loadMetrics = async (runId: string) => {
    try {
      const data = await api.getBenchmarkMetrics(runId) as any
      setMetrics(data.metrics)
    } catch (error) {
      console.error('Failed to load metrics:', error)
    }
  }

  const handleRunChange = (runId: string) => {
    setSelectedRun(runId)
    loadMetrics(runId)
  }

  // Transform metrics for charts
  const accuracyData = metrics ? Object.entries(metrics).map(([pipeline, data]: [string, any]) => ({
    name: pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic',
    accuracy: (data.accuracy * 100).toFixed(1)
  })) : []

  const latencyData = metrics ? Object.entries(metrics).map(([pipeline, data]: [string, any]) => ({
    name: pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic',
    latency: data.avg_latency.toFixed(0)
  })) : []

  const tokenData = metrics ? Object.entries(metrics).map(([pipeline, data]: [string, any]) => ({
    name: pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic',
    tokens: data.avg_tokens.toFixed(0)
  })) : []

  // Calculate aggregate metrics
  const totalQuestions = benchmarkRuns.length > 0 ? benchmarkRuns[0].total_results : 0
  const avgAccuracy = metrics ? (Object.values(metrics).reduce((sum: number, data: any) => sum + data.accuracy, 0) / Object.keys(metrics).length * 100).toFixed(1) : '--'
  const avgLatency = metrics ? (Object.values(metrics).reduce((sum: number, data: any) => sum + data.avg_latency, 0) / Object.keys(metrics).length).toFixed(0) : '--'
  const avgTokens = metrics ? (Object.values(metrics).reduce((sum: number, data: any) => sum + data.avg_tokens, 0) / Object.keys(metrics).length).toFixed(0) : '--'

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Metrics Dashboard</h2>
        <p className="text-gray-400">
          Real benchmark results comparing RAG, GraphRAG, and Agentic GraphRAG performance
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="glass-panel p-4 border border-red-500/50">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="glass-panel p-6">
          <p className="text-gray-400">Loading benchmark data...</p>
        </div>
      )}

      {/* No data */}
      {!loading && benchmarkRuns.length === 0 && (
        <div className="glass-panel p-6 border-l-4 border-yellow-500">
          <p className="text-sm text-yellow-400">
            <strong>No benchmark results available.</strong> Run the benchmark to generate real metrics.
          </p>
        </div>
      )}

      {/* Benchmark selector */}
      {benchmarkRuns.length > 0 && (
        <div className="glass-panel p-4">
          <label className="block text-sm font-medium text-gray-400 mb-2">Select Benchmark Run</label>
          <select
            value={selectedRun || ''}
            onChange={(e) => handleRunChange(e.target.value)}
            className="w-full bg-navy-900 border border-navy-700 rounded-lg px-4 py-2 text-gray-300"
          >
            {benchmarkRuns.map((run) => (
              <option key={run.run_id} value={run.run_id}>
                {run.run_id} ({run.total_results} results) - {run.timestamp ? new Date(run.timestamp).toLocaleString() : 'Unknown date'}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Key Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-panel p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Total Questions</h3>
            <p className="text-2xl font-bold text-gray-100">{totalQuestions}</p>
          </div>
          <div className="glass-panel p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Avg Accuracy</h3>
            <p className="text-2xl font-bold text-cyan-400">{avgAccuracy}%</p>
          </div>
          <div className="glass-panel p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Avg Latency</h3>
            <p className="text-2xl font-bold text-gray-100">{avgLatency}ms</p>
          </div>
          <div className="glass-panel p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Avg Tokens</h3>
            <p className="text-2xl font-bold text-gray-100">{avgTokens}</p>
          </div>
        </div>
      )}

      {/* Charts */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Accuracy Chart */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Accuracy by Pipeline</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={accuracyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
                <XAxis dataKey="name" stroke="#8892b0" />
                <YAxis stroke="#8892b0" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#112240', border: '1px solid #233554' }}
                  itemStyle={{ color: '#8892b0' }}
                />
                <Bar dataKey="accuracy" fill="#64ffda" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Latency Chart */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Latency by Pipeline (ms)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={latencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
                <XAxis dataKey="name" stroke="#8892b0" />
                <YAxis stroke="#8892b0" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#112240', border: '1px solid #233554' }}
                  itemStyle={{ color: '#8892b0' }}
                />
                <Bar dataKey="latency" fill="#00b4d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Token Usage Chart */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Token Usage by Pipeline</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tokenData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
                <XAxis dataKey="name" stroke="#8892b0" />
                <YAxis stroke="#8892b0" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#112240', border: '1px solid #233554' }}
                  itemStyle={{ color: '#8892b0' }}
                />
                <Bar dataKey="tokens" fill="#64ffda" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Per-question-type accuracy */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Accuracy by Question Type</h3>
            <div className="space-y-4">
              {Object.entries(metrics).map(([pipeline, data]: [string, any]) => (
                <div key={pipeline} className="border-b border-navy-700 pb-3">
                  <h4 className="text-sm font-medium text-cyan-400 mb-2 capitalize">
                    {pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic'}
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(data.question_types || {}).map(([qtype, qdata]: [string, any]) => (
                      <div key={qtype} className="flex justify-between items-center">
                        <span className="text-xs text-gray-400 capitalize">{qtype}</span>
                        <span className="text-xs text-gray-300">{(qdata.accuracy * 100).toFixed(1)}% ({qdata.correct}/{qdata.total})</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
