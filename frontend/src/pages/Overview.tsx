import { Link } from 'react-router-dom'
import { Search, GitBranch, BarChart3, ArrowRight } from 'lucide-react'
import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Overview() {
  const [healthStatus, setHealthStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const health = await api.health()
        setHealthStatus(health)
      } catch (error) {
        console.error('Failed to fetch health status:', error)
        // Set a default status so UI still renders
        setHealthStatus({
          status: 'unavailable',
          tigergraph_connected: false,
          vector_db_connected: false,
          llm_configured: false
        })
      } finally {
        setLoading(false)
      }
    }
    fetchHealth()
  }, [])

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="glass-panel p-8">
        <h2 className="text-3xl font-bold text-gray-100 mb-2">GraphProbe AI</h2>
        <p className="text-xl text-cyan-400 mb-4">Investigate. Connect. Verify. Know When to Stop.</p>
        <p className="text-gray-400 max-w-3xl">
          An explainable benchmarking and investigation platform that compares RAG, GraphRAG, 
          and Agentic GraphRAG on the same questions and evidence corpus.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/investigate" className="glass-panel p-6 hover:border-cyan-500/50 transition-colors cursor-pointer group">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-cyan-500/10 rounded-lg group-hover:bg-cyan-500/20 transition-colors">
              <Search className="h-6 w-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-100 mb-2">Investigate</h3>
              <p className="text-sm text-gray-400 mb-4">
                Ask questions and investigate them using RAG, GraphRAG, or Agentic GraphRAG
              </p>
              <div className="flex items-center text-cyan-400 text-sm font-medium">
                Start Investigation <ArrowRight className="h-4 w-4 ml-1" />
              </div>
            </div>
          </div>
        </Link>

        <Link to="/compare" className="glass-panel p-6 hover:border-cyan-500/50 transition-colors cursor-pointer group">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-cyan-500/10 rounded-lg group-hover:bg-cyan-500/20 transition-colors">
              <GitBranch className="h-6 w-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-100 mb-2">Compare</h3>
              <p className="text-sm text-gray-400 mb-4">
                Compare all three pipelines side-by-side on the same question
              </p>
              <div className="flex items-center text-cyan-400 text-sm font-medium">
                Compare Pipelines <ArrowRight className="h-4 w-4 ml-1" />
              </div>
            </div>
          </div>
        </Link>

        <Link to="/metrics" className="glass-panel p-6 hover:border-cyan-500/50 transition-colors cursor-pointer group">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-cyan-500/10 rounded-lg group-hover:bg-cyan-500/20 transition-colors">
              <BarChart3 className="h-6 w-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-100 mb-2">Metrics</h3>
              <p className="text-sm text-gray-400 mb-4">
                View benchmark results and performance metrics across all pipelines
              </p>
              <div className="flex items-center text-cyan-400 text-sm font-medium">
                View Metrics <ArrowRight className="h-4 w-4 ml-1" />
              </div>
            </div>
          </div>
        </Link>
      </div>

      {/* System Status */}
      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">System Status</h3>
        {loading ? (
          <div className="text-sm text-gray-400">Loading system status...</div>
        ) : healthStatus ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className={`h-3 w-3 rounded-full ${healthStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-400">Backend API</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`h-3 w-3 rounded-full ${healthStatus.tigergraph_connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-400">TigerGraph Connection</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`h-3 w-3 rounded-full ${healthStatus.vector_db_connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-400">Vector Database</span>
            </div>
          </div>
        ) : (
          <div className="text-sm text-red-400">Failed to load system status</div>
        )}
      </div>

      {/* Research Question */}
      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Research Question</h3>
        <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
          <p className="text-gray-300 italic">
            "When does Agentic GraphRAG actually provide enough additional reasoning value 
            to justify its additional retrieval steps, latency, and token cost?"
          </p>
        </div>
        <p className="text-sm text-gray-400 mt-4">
          This system demonstrates that simple questions can be handled by simpler retrieval 
          while complex multi-hop questions can trigger deeper agentic investigation.
        </p>
      </div>

      {/* Research Question */}
      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Research Question</h3>
        <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
          <p className="text-gray-300 italic">
            "When does Agentic GraphRAG actually provide enough additional reasoning value 
            to justify its additional retrieval steps, latency, and token cost?"
          </p>
        </div>
        <p className="text-sm text-gray-400 mt-4">
          This system demonstrates that simple questions can be handled by simpler retrieval 
          while complex multi-hop questions can trigger deeper agentic investigation.
        </p>
      </div>
    </div>
  )
}
