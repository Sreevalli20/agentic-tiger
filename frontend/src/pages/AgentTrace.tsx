import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Activity, Clock, Zap, Layers, Loader2, CheckCircle, Search, Network, GitBranch, AlertCircle } from 'lucide-react'
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
      if (data && typeof data === 'object') {
        setTrace(data)
      } else {
        setError('Invalid trace data received from backend')
      }
    } catch (err) {
      console.error('Failed to load trace:', err)
      setError(err instanceof Error ? err.message : 'Failed to load trace data')
    } finally {
      setLoading(false)
    }
  }

  const getStepIcon = (tool: string) => {
    switch (tool) {
      case 'entity_link':
        return Network
      case 'graph_traverse':
        return GitBranch
      case 'vector_search':
        return Search
      case 'document_retrieve':
        return Layers
      case 'evaluate_evidence':
        return Zap
      case 'aggregate':
        return Activity
      case 'verify':
        return CheckCircle
      case 'stop':
        return CheckCircle
      default:
        return Activity
    }
  }

  const getStepLabel = (tool: string) => {
    switch (tool) {
      case 'entity_link':
        return 'Entity Linking'
      case 'graph_traverse':
        return 'Graph Traversal'
      case 'vector_search':
        return 'Vector Search'
      case 'document_retrieve':
        return 'Document Retrieval'
      case 'evaluate_evidence':
        return 'Evidence Evaluation'
      case 'aggregate':
        return 'Aggregation'
      case 'verify':
        return 'Verification'
      case 'stop':
        return 'Stopping Decision'
      default:
        return tool
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Agent Execution Trace</h2>
        <p className="text-gray-400">
          Run ID: <span className="text-cyan-400 font-mono">{runId}</span>
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
        <div className="glass-panel p-6 border border-red-500/50">
          <div className="flex items-center space-x-3 mb-2">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <h3 className="text-lg font-semibold text-red-400">Error</h3>
          </div>
          <p className="text-gray-300">{error}</p>
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
                {trace.total_latency_ms ? Math.round(trace.total_latency_ms) : '--'}ms
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

          {/* Question */}
          {trace.question && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Original Question</h3>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <p className="text-gray-100">{trace.question}</p>
              </div>
            </div>
          )}

          {/* Step-by-step trace */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Execution Timeline</h3>
            <div className="space-y-4">
              {trace.steps && trace.steps.length > 0 ? (
                trace.steps.map((step: any, index: number) => {
                  const StepIcon = getStepIcon(step.tool)
                  return (
                    <div key={index} className="relative">
                      {/* Timeline line */}
                      {index < trace.steps.length - 1 && (
                        <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-navy-700" />
                      )}

                      <div className="flex items-start space-x-4">
                        {/* Step number circle */}
                        <div className="flex-shrink-0">
                          <div className="h-12 w-12 rounded-full bg-cyan-500/20 border-2 border-cyan-500 flex items-center justify-center">
                            <StepIcon className="h-5 w-5 text-cyan-400" />
                          </div>
                        </div>

                        {/* Step content */}
                        <div className="flex-1 bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-3">
                              <span className="text-sm font-semibold text-cyan-400">STEP {String(step.step).padStart(2, '0')}</span>
                              <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                                {getStepLabel(step.tool)}
                              </span>
                            </div>
                            {step.timestamp && (
                              <span className="text-xs text-gray-500">
                                {new Date(step.timestamp).toLocaleTimeString()}
                              </span>
                            )}
                          </div>

                          <p className="text-sm text-gray-300 mb-3">{step.result_summary}</p>

                          {/* Step details */}
                          <div className="grid grid-cols-3 gap-2 text-xs">
                            <div className="bg-navy-800/50 rounded p-2">
                              <span className="text-gray-500 block">Tokens</span>
                              <span className="text-gray-300">{step.tokens || 0}</span>
                            </div>
                            <div className="bg-navy-800/50 rounded p-2">
                              <span className="text-gray-500 block">Latency</span>
                              <span className="text-gray-300">{Math.round(step.latency_ms)}ms</span>
                            </div>
                            <div className="bg-navy-800/50 rounded p-2">
                              <span className="text-gray-500 block">Status</span>
                              <span className="text-green-400">Complete</span>
                            </div>
                          </div>

                          {/* Input if available */}
                          {step.input && (
                            <div className="mt-3 pt-3 border-t border-navy-700">
                              <label className="block text-xs text-gray-500 mb-1">Input</label>
                              <p className="text-xs text-gray-400">{step.input}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No trace data available for this run
                </div>
              )}
            </div>
          </div>

          {/* Strategy Changes */}
          {trace.strategy_changes && trace.strategy_changes.length > 0 && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Strategy Changes</h3>
              <div className="space-y-2">
                {trace.strategy_changes.map((change: string, index: number) => (
                  <div key={index} className="bg-navy-900/50 rounded-lg p-3 border border-navy-700">
                    <div className="flex items-center space-x-2">
                      <GitBranch className="h-4 w-4 text-cyan-400" />
                      <p className="text-sm text-gray-300">{change}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stopping Decision */}
          <div className="glass-panel p-6 border-l-4 border-l-cyan-500">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircle className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-cyan-400">Investigation Decision</h3>
            </div>
            <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
              <p className="text-gray-100">{trace.stopping_reason || 'No stopping reason recorded'}</p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
