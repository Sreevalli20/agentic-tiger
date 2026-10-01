import { useState } from 'react'
import { GitBranch, Loader2, Search, Network, Zap, ChevronDown, ChevronUp, FileText, Database } from 'lucide-react'
import { api } from '../services/api'

export default function Compare() {
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedPipeline, setExpandedPipeline] = useState<string | null>(null)

  const handleCompare = async () => {
    if (!question.trim()) return

    setIsLoading(true)
    setError(null)
    try {
      const data = await api.compare(question, ['rag', 'graphrag', 'agentic'])
      if (data && typeof data === 'object') {
        setResults(data)
      } else {
        setError('Invalid comparison data received from backend')
      }
    } catch (error) {
      console.error('Comparison failed:', error)
      setError(error instanceof Error ? error.message : 'Comparison failed')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleExpand = (pipeline: string) => {
    setExpandedPipeline(expandedPipeline === pipeline ? null : pipeline)
  }

  const getPipelineIcon = (pipeline: string) => {
    switch (pipeline) {
      case 'rag':
        return Search
      case 'graphrag':
        return Network
      case 'agentic':
        return Zap
      default:
        return GitBranch
    }
  }

  const getPipelineDescription = (pipeline: string) => {
    switch (pipeline) {
      case 'rag':
        return 'Retrieval-Augmented Generation'
      case 'graphrag':
        return 'Graph-based RAG with entity connections'
      case 'agentic':
        return 'Agentic investigation with adaptive reasoning'
      default:
        return pipeline
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Compare Pipelines</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Question</label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question..."
              className="input-field w-full h-32 resize-none"
            />
          </div>

          <button
            onClick={handleCompare}
            disabled={isLoading || !question.trim()}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Comparing...</span>
              </>
            ) : (
              <>
                <GitBranch className="h-5 w-5" />
                <span>Compare All Pipelines</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="glass-panel p-6 border border-red-500/50">
          <h3 className="text-lg font-semibold text-red-400 mb-2">Error</h3>
          <p className="text-gray-300">{error}</p>
        </div>
      )}

      {/* Comparison Results */}
      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {Object.entries(results.results).map(([pipeline, result]: [string, any]) => {
            const Icon = getPipelineIcon(pipeline)
            const isExpanded = expandedPipeline === pipeline
            const pipelineName = pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic GraphRAG'

            return (
              <div key={pipeline} className="glass-panel p-5 border-t-4 border-t-cyan-500">
                {/* Pipeline Header */}
                <div className="flex items-center space-x-3 mb-4">
                  <div className="h-10 w-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Icon className="h-5 w-5 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-100">{pipelineName}</h3>
                    <p className="text-xs text-gray-400">{getPipelineDescription(pipeline)}</p>
                  </div>
                </div>

                {/* Answer */}
                <div className="mb-4">
                  <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Answer</label>
                  <div className="bg-navy-900/50 rounded-lg p-3 border border-navy-700 max-h-32 overflow-y-auto">
                    <p className="text-sm text-gray-100 leading-relaxed">{result.answer}</p>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                    <label className="block text-xs text-gray-500 mb-1">Confidence</label>
                    <p className="text-cyan-400 font-semibold text-sm">
                      {(result.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                    <label className="block text-xs text-gray-500 mb-1">Latency</label>
                    <p className="text-gray-300 text-sm">
                      {result.metrics?.total_latency_ms?.toFixed(0) || 'N/A'}ms
                    </p>
                  </div>
                  <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                    <label className="block text-xs text-gray-500 mb-1">Tokens</label>
                    <p className="text-gray-300 text-sm">
                      {result.metrics?.total_tokens || 'N/A'}
                    </p>
                  </div>
                  <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                    <label className="block text-xs text-gray-500 mb-1">Evidence</label>
                    <p className="text-gray-300 text-sm">
                      {result.evidence?.length || 0}
                    </p>
                  </div>
                </div>

                {/* Why This Answer - Expandable */}
                <button
                  onClick={() => toggleExpand(pipeline)}
                  className="w-full flex items-center justify-between text-xs font-medium text-cyan-400 hover:text-cyan-300 mb-2 py-2 px-3 bg-navy-900/30 rounded-lg border border-navy-700"
                >
                  <span>Why this answer?</span>
                  {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>

                {/* Pipeline-specific reasoning */}
                {isExpanded && (
                  <div className="space-y-3 mt-3">
                    {/* RAG: Retrieved passages */}
                    {pipeline === 'rag' && result.evidence && (
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Retrieved Passages</label>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {result.evidence.map((evidence: any, index: number) => (
                            <div key={index} className="bg-navy-900/50 rounded p-3 border border-navy-700">
                              <div className="flex items-center space-x-2 mb-1">
                                <FileText className="h-3 w-3 text-gray-500" />
                                <span className="text-xs text-gray-500">{evidence.metadata?.source_type || 'document'}</span>
                              </div>
                              <p className="text-xs text-gray-300">{evidence.content}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* GraphRAG: Graph context */}
                    {pipeline === 'graphrag' && result.graph_context && (
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Graph Context</label>
                        <div className="bg-navy-900/50 rounded p-3 border border-navy-700 mb-2">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-gray-500">Entities:</span>
                              <span className="text-gray-300 ml-1">{result.graph_context.entities?.length || 0}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Relationships:</span>
                              <span className="text-gray-300 ml-1">{result.graph_context.relationships?.length || 0}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Traversal Depth:</span>
                              <span className="text-gray-300 ml-1">{result.graph_context.traversal_depth || 0}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Nodes Visited:</span>
                              <span className="text-gray-300 ml-1">{result.graph_context.nodes_visited || 0}</span>
                            </div>
                          </div>
                        </div>
                        {result.evidence && result.evidence.length > 0 && (
                          <div>
                            <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Graph Evidence</label>
                            <div className="space-y-2 max-h-48 overflow-y-auto">
                              {result.evidence.map((evidence: any, index: number) => (
                                <div key={index} className="bg-navy-900/50 rounded p-3 border border-navy-700">
                                  <div className="flex items-center space-x-2 mb-1">
                                    <Network className="h-3 w-3 text-cyan-400" />
                                    <span className="text-xs text-gray-500">{evidence.metadata?.source_type || 'graph'}</span>
                                  </div>
                                  <p className="text-xs text-gray-300">{evidence.content}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Agentic: Investigation trace */}
                    {pipeline === 'agentic' && result.agent_trace && (
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Investigation Trace</label>
                        <div className="bg-navy-900/50 rounded p-3 border border-navy-700 mb-2">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-gray-500">Steps:</span>
                              <span className="text-gray-300 ml-1">{result.agent_trace.steps?.length || 0}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Strategy Changes:</span>
                              <span className="text-gray-300 ml-1">{result.agent_trace.strategy_changes?.length || 0}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Evidence Count:</span>
                              <span className="text-gray-300 ml-1">{result.agent_trace.evidence_count || 0}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Total Tokens:</span>
                              <span className="text-gray-300 ml-1">{result.agent_trace.total_tokens || 0}</span>
                            </div>
                          </div>
                        </div>
                        {result.agent_trace.steps && result.agent_trace.steps.length > 0 && (
                          <div className="space-y-2 max-h-48 overflow-y-auto">
                            {result.agent_trace.steps.map((step: any, index: number) => (
                              <div key={index} className="bg-navy-900/50 rounded p-2 border border-navy-700">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-xs font-medium text-cyan-400">Step {step.step}</span>
                                  <span className="text-xs text-gray-500">{step.tool}</span>
                                </div>
                                <p className="text-xs text-gray-300">{step.result_summary}</p>
                              </div>
                            ))}
                          </div>
                        )}
                        {result.agent_trace.stopping_reason && (
                          <div className="mt-2 bg-navy-900/50 rounded p-2 border border-cyan-500/30">
                            <label className="block text-xs font-medium text-cyan-400 mb-1 uppercase tracking-wide">Stopping Decision</label>
                            <p className="text-xs text-gray-300">{result.agent_trace.stopping_reason}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Evidence items for all pipelines */}
                    {result.evidence && result.evidence.length > 0 && pipeline !== 'rag' && pipeline !== 'graphrag' && (
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Evidence Items</label>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {result.evidence.map((evidence: any, index: number) => (
                            <div key={index} className="bg-navy-900/50 rounded p-3 border border-navy-700">
                              <div className="flex items-center space-x-2 mb-1">
                                <Database className="h-3 w-3 text-gray-500" />
                                <span className="text-xs text-gray-500">{evidence.metadata?.source_type || 'unknown'}</span>
                              </div>
                              <p className="text-xs text-gray-300">{evidence.content}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Comparison Summary */}
      {results && results.comparison && (
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Performance Comparison</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Latency Comparison</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="space-y-2">
                  {Object.entries(results.comparison.latency_comparison).map(([pipeline, value]) => (
                    <div key={pipeline} className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 capitalize">{pipeline}</span>
                      <span className="text-sm text-gray-300">{typeof value === 'number' ? value.toFixed(0) : String(value)}ms</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Token Comparison</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="space-y-2">
                  {Object.entries(results.comparison.token_comparison).map(([pipeline, value]) => (
                    <div key={pipeline} className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 capitalize">{pipeline}</span>
                      <span className="text-sm text-gray-300">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Evidence Count</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="space-y-2">
                  {Object.entries(results.comparison.evidence_count).map(([pipeline, value]) => (
                    <div key={pipeline} className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 capitalize">{pipeline}</span>
                      <span className="text-sm text-gray-300">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
