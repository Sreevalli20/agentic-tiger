import { useState } from 'react'
import { Send, Loader2, Activity, GitBranch } from 'lucide-react'
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
      setError(error instanceof Error ? error.message : 'Investigation failed')
    } finally {
      setIsLoading(false)
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

      {/* Live Progress for Agentic */}
      {isLoading && pipeline === 'agentic' && (
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Agentic Investigation Progress</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></div>
              <span className="text-sm text-gray-400">Analyzing question...</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-navy-600"></div>
              <span className="text-sm text-gray-500">Selecting retrieval method...</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-navy-600"></div>
              <span className="text-sm text-gray-500">Retrieving evidence...</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-navy-600"></div>
              <span className="text-sm text-gray-500">Evaluating evidence...</span>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="glass-panel p-6 border border-red-500/50">
          <h3 className="text-lg font-semibold text-red-400 mb-2">Error</h3>
          <p className="text-gray-300">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Results</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Answer</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <p className="text-gray-300">{result.result?.answer || 'No answer generated'}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Confidence</label>
                <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                  <p className="text-cyan-400 font-semibold">
                    {(result.result?.confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Latency</label>
                <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                  <p className="text-gray-300">
                    {result.result?.metrics?.total_latency_ms?.toFixed(0)}ms
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Investigation ID</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <p className="text-sm text-cyan-400 font-mono mb-2">{result.investigation_id}</p>
                <div className="flex space-x-3">
                  <Link 
                    to={`/trace/${result.investigation_id}`}
                    className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300"
                  >
                    <Activity className="h-3 w-3" />
                    <span>View Trace</span>
                  </Link>
                  <Link 
                    to={`/evidence/${result.investigation_id}`}
                    className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300"
                  >
                    <GitBranch className="h-3 w-3" />
                    <span>View Evidence</span>
                  </Link>
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Evidence ({result.result?.evidence?.length || 0} items)</label>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {result.result?.evidence?.map((evidence: any, index: number) => (
                  <div key={index} className="bg-navy-900/50 rounded-lg p-3 border border-navy-700">
                    <p className="text-sm text-gray-300">{evidence.content}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Source: {evidence.metadata?.source} ({evidence.metadata?.source_type})
                    </p>
                  </div>
                ))}
              </div>
            </div>
            
            {result.result?.citations && result.result.citations.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Citations ({result.result.citations.length})</label>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {result.result.citations.map((citation: any, index: number) => (
                    <div key={index} className="bg-navy-900/50 rounded-lg p-2 border border-navy-700">
                      <p className="text-xs text-gray-400">{citation.text || JSON.stringify(citation)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {result.result?.metrics && (
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Metrics</label>
                <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">Total Latency:</span>
                      <span className="text-gray-300 ml-2">{result.result.metrics.total_latency_ms?.toFixed(0)}ms</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Total Tokens:</span>
                      <span className="text-gray-300 ml-2">{result.result.metrics.total_tokens}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">LLM Calls:</span>
                      <span className="text-gray-300 ml-2">{result.result.metrics.llm_calls}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Retrieval Calls:</span>
                      <span className="text-gray-300 ml-2">{result.result.metrics.retrieval_calls}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
