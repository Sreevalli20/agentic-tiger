import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { GitBranch, Network, Loader2 } from 'lucide-react'
import { api } from '../services/api'

export default function EvidenceGraph() {
  const { runId } = useParams()
  const [graphContext, setGraphContext] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (runId) {
      loadGraphContext(runId)
    }
  }, [runId])

  const loadGraphContext = async (id: string) => {
    try {
      setLoading(true)
      const graphData = await api.getEvidenceGraph(id)
      // Handle the backend response structure
      if (graphData && typeof graphData === 'object') {
        setGraphContext(graphData)
      } else {
        setError('Invalid graph data received from backend')
      }
    } catch (err) {
      console.error('Failed to load graph context:', err)
      setError(err instanceof Error ? err.message : 'Failed to load graph data')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Evidence Graph</h2>
        <p className="text-gray-400">
          Run ID: {runId}
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="glass-panel p-6">
          <div className="flex items-center space-x-3">
            <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
            <p className="text-gray-400">Loading graph data...</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="glass-panel p-4 border border-red-500/50">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Graph Data */}
      {graphContext && !loading && (
        <>
          {/* Graph Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Network className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Entities</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">{graphContext.entities?.length || 0}</p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <GitBranch className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Relationships</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">{graphContext.relationships?.length || 0}</p>
            </div>
            <div className="glass-panel p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Network className="h-5 w-5 text-cyan-400" />
                <h3 className="text-sm font-medium text-gray-400">Nodes Visited</h3>
              </div>
              <p className="text-2xl font-bold text-gray-100">{graphContext.nodes_visited || 0}</p>
            </div>
          </div>

          {/* Graph Visualization */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Graph Visualization</h3>
            <div className="bg-navy-900/50 rounded-lg p-8 border border-navy-700 min-h-[400px] flex items-center justify-center">
              <div className="text-center">
                <Network className="h-16 w-16 text-navy-600 mx-auto mb-4" />
                <p className="text-gray-500">Graph visualization requires graph data</p>
                <p className="text-sm text-gray-600 mt-2">
                  {graphContext.entities?.length > 0 
                    ? `${graphContext.entities.length} entities found` 
                    : 'No graph entities available'}
                </p>
              </div>
            </div>
          </div>

          {/* Graph Context */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Graph Context</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Entities Identified</label>
                <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                  {graphContext.entities && graphContext.entities.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {graphContext.entities.map((entity: string, index: number) => (
                        <span key={index} className="px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded text-sm">
                          {entity}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No entities identified</p>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Relationships Traversed</label>
                <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
                  {graphContext.relationships && graphContext.relationships.length > 0 ? (
                    <div className="space-y-2">
                      {graphContext.relationships.slice(0, 5).map((rel: any, index: number) => (
                        <div key={index} className="text-sm text-gray-300">
                          <span className="text-cyan-400">{rel.source}</span>
                          <span className="text-gray-500 mx-2">→</span>
                          <span className="text-cyan-400">{rel.target}</span>
                          <span className="text-gray-500 mx-2">({rel.type})</span>
                        </div>
                      ))}
                      {graphContext.relationships.length > 5 && (
                        <p className="text-xs text-gray-500">+{graphContext.relationships.length - 5} more relationships</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No relationships traversed</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
