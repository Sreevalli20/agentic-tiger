import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Activity, Clock, Zap, Layers, Loader2 } from 'lucide-react'
import { api } from '../services/api'

export default function AgentTrace() {
  const { runId } = useParams()
  const [trace, setTrace] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (runId) {
      loadTrace(runId)
    }
  }, [runId])

  const loadTrace = async (id: string) => {
    try {
      setLoading(true)
      const data = await api.getTrace(id)
      setTrace(data)
    } catch (err) {
      console.error('Failed to load trace:', err)
      setError(err instanceof Error ? err.message : 'Failed to load trace data')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Agent Trace</h2>
        <p className="text-gray-400">
          Run ID: {runId}
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="glass-panel p-6">
          <div className="flex items-center space-x-3">
            <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
            <p className="text-gray-400">Loading trace data...</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="glass-panel p-4 border border-red-500/50">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Trace Data */}
      {trace && !loading && (
        <>
          {/* Trace Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Activity className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Total Steps</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">{trace.steps?.length || 0}</p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Total Latency</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">
                {trace.timing?.total_latency_ms ? Math.round(trace.timing.total_latency_ms) : '--'}ms
              </p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Zap className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Total Tokens</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">{trace.total_tokens || '--'}</p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Layers className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Evidence Items</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">{trace.evidence_count || '--'}</p>
            </div>
          </div>

          {/* Step-by-step trace */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Execution Steps</h3>
            <div className="space-y-4">
              {trace.steps && trace.steps.length > 0 ? (
                trace.steps.map((step: any, index: number) => (
                  <div key={index} className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-cyan-400">Step {step.step}</span>
                      <span className="text-xs text-gray-500">{step.tool}</span>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{step.result_summary}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>Tokens: {step.tokens}</span>
                      <span>Latency: {Math.round(step.latency_ms)}ms</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No trace data available for this run
                </div>
              )}
            </div>
          </div>

          {/* Stopping Reason */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Stopping Reason</h3>
            <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
              <p className="text-gray-300">{trace.stopping_reason || 'No stopping reason recorded'}</p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
