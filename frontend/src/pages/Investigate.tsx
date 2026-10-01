import { useState } from 'react'
import { Send, Loader2, Activity, GitBranch, CheckCircle, AlertCircle, Search, Network, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

type PipelineType = 'rag' | 'graphrag' | 'agentic'

export default function Investigate() {
  const [question, setQuestion] = useState('')
  const [pipeline, setPipeline] = useState<PipelineType>('agentic')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInvestigate = async () => {
    if (!question.trim()) return

    setIsLoading(true)
    setError(null)
    try {
      const data = await api.investigate(question, pipeline)
      setResult(data)
    } catch (error) {
      console.error('Investigation failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'Investigation failed'
      if (errorMessage.includes('timed out')) {
        setError('Investigation timed out. Please try a simpler question.')
      } else {
        setError(errorMessage)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const getInvestigationStages = () => {
    if (pipeline === 'agentic') {
      return [
        { icon: Search, label: 'Analyzing question' },
        { icon: Network, label: 'Identifying entities' },
        { icon: Search, label: 'Retrieving evidence' },
        { icon: GitBranch, label: 'Following connections' },
        { icon: Zap, label: 'Evaluating evidence' },
        { icon: CheckCircle, label: 'Synthesizing answer' },
      ]
    } else if (pipeline === 'graphrag') {
      return [
        { icon: Search, label: 'Analyzing question' },
        { icon: Network, label: 'Extracting entities' },
        { icon: GitBranch, label: 'Traversing graph' },
        { icon: CheckCircle, label: 'Generating answer' },
      ]
    } else {
      return [
        { icon: Search, label: 'Analyzing question' },
        { icon: Search, label: 'Retrieving documents' },
        { icon: CheckCircle, label: 'Generating answer' },
      ]
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Investigate</h2>

        {/* Question Input */}
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

          {/* Pipeline Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Pipeline</label>
            <div className="flex space-x-4">
              {[
                { value: 'rag', label: 'RAG' },
                { value: 'graphrag', label: 'GraphRAG' },
                { value: 'agentic', label: 'Agentic GraphRAG' }
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setPipeline(option.value as PipelineType)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    pipeline === option.value
                      ? 'bg-cyan-500 text-navy-900 font-semibold'
                      : 'bg-navy-700 text-gray-400 hover:bg-navy-600'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            onClick={handleInvestigate}
            disabled={isLoading || !question.trim()}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Investigating...</span>
              </>
            ) : (
              <>
                <Send className="h-5 w-5" />
                <span>Investigate</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Loading State - Investigation Process */}
      {isLoading && (
        <div className="glass-panel p-6 border border-cyan-500/30">
          <div className="flex items-center space-x-3 mb-6">
            <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
            <div>
              <h3 className="text-lg font-semibold text-cyan-400">Investigation Active</h3>
              <p className="text-sm text-gray-400">Processing your question through the {pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic GraphRAG'} pipeline</p>
            </div>
          </div>

          <div className="space-y-3">
            {getInvestigationStages().map((stage, index) => (
              <div key={index} className="flex items-center space-x-3 text-sm">
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  index === 0 ? 'bg-cyan-500/20 text-cyan-400 animate-pulse' : 'bg-navy-700 text-gray-500'
                }`}>
                  <stage.icon className="h-4 w-4" />
                </div>
                <span className={index === 0 ? 'text-cyan-400' : 'text-gray-500'}>{stage.label}</span>
              </div>
            ))}
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

      {/* Results */}
      {result && !isLoading && (
        <div className="space-y-6">
          {/* Final Answer Section */}
          <div className="glass-panel p-6 border-l-4 border-cyan-500">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-cyan-400">FINAL FINDING</h3>
            </div>
            <div className="bg-navy-900/50 rounded-lg p-5 border border-navy-700">
              <p className="text-gray-100 text-lg leading-relaxed">{result.result?.answer || 'No answer generated'}</p>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Zap className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-medium text-gray-400">Confidence</h3>
              </div>
              <p className="text-xl font-bold text-cyan-400">
                {(result.result?.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Activity className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-medium text-gray-400">Latency</h3>
              </div>
              <p className="text-xl font-bold text-gray-100">
                {result.result?.metrics?.total_latency_ms?.toFixed(0)}ms
              </p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <GitBranch className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-medium text-gray-400">Evidence</h3>
              </div>
              <p className="text-xl font-bold text-gray-100">
                {result.result?.evidence?.length || 0}
              </p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Search className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-medium text-gray-400">Tokens</h3>
              </div>
              <p className="text-xl font-bold text-gray-100">
                {result.result?.metrics?.total_tokens || 'N/A'}
              </p>
            </div>
          </div>

          {/* Why This Answer Section */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">WHY THIS ANSWER</h3>
            <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
              <div className="space-y-3 text-sm">
                <div className="flex items-start space-x-2">
                  <div className="h-2 w-2 rounded-full bg-cyan-400 mt-2 flex-shrink-0" />
                  <div>
                    <p className="text-gray-400">Pipeline used:</p>
                    <p className="text-gray-100 capitalize">{pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic GraphRAG'}</p>
                  </div>
                </div>
                {result.result?.graph_context && (
                  <div className="flex items-start space-x-2">
                    <div className="h-2 w-2 rounded-full bg-cyan-400 mt-2 flex-shrink-0" />
                    <div>
                      <p className="text-gray-400">Graph context:</p>
                      <p className="text-gray-100">{result.result.graph_context.entities?.length || 0} entities, {result.result.graph_context.relationships?.length || 0} relationships</p>
                    </div>
                  </div>
                )}
                {result.result?.agent_trace && (
                  <div className="flex items-start space-x-2">
                    <div className="h-2 w-2 rounded-full bg-cyan-400 mt-2 flex-shrink-0" />
                    <div>
                      <p className="text-gray-400">Investigation steps:</p>
                      <p className="text-gray-100">{result.result.agent_trace.steps?.length || 0} steps executed</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Evidence Section */}
          {result.result?.evidence && result.result.evidence.length > 0 && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">EVIDENCE ({result.result.evidence.length} items)</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {result.result.evidence.map((evidence: any, index: number) => (
                  <div key={index} className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-xs font-medium text-cyan-400">Evidence #{index + 1}</span>
                      <span className="text-xs text-gray-500">
                        {evidence.metadata?.source_type || 'unknown'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{evidence.content}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      {evidence.metadata?.source && (
                        <span>Source: {evidence.metadata.source}</span>
                      )}
                      {evidence.relevance_score !== undefined && (
                        <span>Relevance: {(evidence.relevance_score * 100).toFixed(1)}%</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Citations Section */}
          {result.result?.citations && result.result.citations.length > 0 && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">CITATIONS ({result.result.citations.length})</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {result.result.citations.map((citation: any, index: number) => (
                  <div key={index} className="bg-navy-900/50 rounded-lg p-3 border border-navy-700">
                    <p className="text-sm text-gray-300">{citation.claim || citation.text || JSON.stringify(citation)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Investigation Links */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">INVESTIGATION DETAILS</h3>
            <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
              <p className="text-sm text-cyan-400 font-mono mb-3">{result.investigation_id}</p>
              <div className="flex space-x-4">
                <Link
                  to={`/trace/${result.investigation_id}`}
                  className="flex items-center space-x-2 text-sm text-cyan-400 hover:text-cyan-300"
                >
                  <Activity className="h-4 w-4" />
                  <span>View Full Trace</span>
                </Link>
                <Link
                  to={`/evidence/${result.investigation_id}`}
                  className="flex items-center space-x-2 text-sm text-cyan-400 hover:text-cyan-300"
                >
                  <GitBranch className="h-4 w-4" />
                  <span>View Evidence Graph</span>
                </Link>
              </div>
            </div>
          </div>

          {/* Detailed Metrics */}
          {result.result?.metrics && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">PERFORMANCE METRICS</h3>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 block">Total Latency:</span>
                    <span className="text-gray-300">{result.result.metrics.total_latency_ms?.toFixed(0)}ms</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Total Tokens:</span>
                    <span className="text-gray-300">{result.result.metrics.total_tokens}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Retrieval Time:</span>
                    <span className="text-gray-300">{result.result.metrics.retrieval_time_ms?.toFixed(0)}ms</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Generation Time:</span>
                    <span className="text-gray-300">{result.result.metrics.generation_time_ms?.toFixed(0)}ms</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Chunks Retrieved:</span>
                    <span className="text-gray-300">{result.result.metrics.chunks_retrieved}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Retrieval Steps:</span>
                    <span className="text-gray-300">{result.result.metrics.retrieval_steps}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
