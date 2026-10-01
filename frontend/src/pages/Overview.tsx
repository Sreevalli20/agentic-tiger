import { Link } from 'react-router-dom'
import { Search, GitBranch, BarChart3, ArrowRight } from 'lucide-react'

export default function Overview() {

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="glass-panel p-8">
        <h2 className="text-3xl font-bold text-gray-100 mb-2">GraphProbe AI</h2>
        <p className="text-xl text-cyan-400 mb-4">Investigate. Connect. Verify.</p>
        <p className="text-gray-400 max-w-3xl">
          An explainable investigation platform that uses evidence, graph relationships, and agentic reasoning to answer complex questions.
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
              <h3 className="text-lg font-semibold text-gray-100 mb-2">Start Investigation</h3>
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
              <h3 className="text-lg font-semibold text-gray-100 mb-2">Compare Pipelines</h3>
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
              <h3 className="text-lg font-semibold text-gray-100 mb-2">View Metrics & Traces</h3>
              <p className="text-sm text-gray-400 mb-4">
                View benchmark results, performance metrics, and detailed agent traces
              </p>
              <div className="flex items-center text-cyan-400 text-sm font-medium">
                View Metrics <ArrowRight className="h-4 w-4 ml-1" />
              </div>
            </div>
          </div>
        </Link>
      </div>


    </div>
  )
}
