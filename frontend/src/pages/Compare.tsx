import { useState } from 'react'
import { GitBranch, Loader2 } from 'lucide-react'

export default function Compare() {
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<any>(null)

  const handleCompare = async () => {
    if (!question.trim()) return
    
    setIsLoading(true)
    try {
      const response = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question,
          pipelines: ['rag', 'graphrag', 'agentic']
        })
      })
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Comparison failed:', error)
    } finally {
      setIsLoading(false)
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

      {/* Comparison Results */}
      {results && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(results.results).map(([pipeline, result]: [string, any]) => (
            <div key={pipeline} className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4 capitalize">
                {pipeline === 'rag' ? 'RAG' : pipeline === 'graphrag' ? 'GraphRAG' : 'Agentic GraphRAG'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Answer</label>
                  <div className="bg-navy-900/50 rounded-lg p-3 border border-navy-700 max-h-40 overflow-y-auto">
                    <p className="text-sm text-gray-300">{result.answer}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-1">Confidence</label>
                    <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                      <p className="text-cyan-400 text-sm font-semibold">
                        {(result.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-1">Latency</label>
                    <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                      <p className="text-gray-300 text-sm">
                        {result.metrics.total_latency_ms.toFixed(0)}ms
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-1">Tokens</label>
                    <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                      <p className="text-gray-300 text-sm">
                        {result.metrics.total_tokens}
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-1">Evidence</label>
                    <div className="bg-navy-900/50 rounded p-2 border border-navy-700">
                      <p className="text-gray-300 text-sm">
                        {result.evidence.length}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Evidence Items</label>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {result.evidence.slice(0, 3).map((evidence: any, index: number) => (
                      <div key={index} className="bg-navy-900/50 rounded p-2 border border-navy-700">
                        <p className="text-xs text-gray-400 truncate">{evidence.content}</p>
                      </div>
                    ))}
                    {result.evidence.length > 3 && (
                      <p className="text-xs text-gray-500">+{result.evidence.length - 3} more</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Comparison Summary */}
      {results && results.comparison && (
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Comparison Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Latency Comparison</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="space-y-2">
                  {Object.entries(results.comparison.latency_comparison).map(([pipeline, value]: [string, number]) => (
                    <div key={pipeline} className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 capitalize">{pipeline}</span>
                      <span className="text-sm text-gray-300">{value.toFixed(0)}ms</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Token Comparison</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="space-y-2">
                  {Object.entries(results.comparison.token_comparison).map(([pipeline, value]: [string, number]) => (
                    <div key={pipeline} className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 capitalize">{pipeline}</span>
                      <span className="text-sm text-gray-300">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Evidence Count</label>
              <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                <div className="space-y-2">
                  {Object.entries(results.comparison.evidence_count).map(([pipeline, value]: [string, number]) => (
                    <div key={pipeline} className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 capitalize">{pipeline}</span>
                      <span className="text-sm text-gray-300">{value}</span>
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
