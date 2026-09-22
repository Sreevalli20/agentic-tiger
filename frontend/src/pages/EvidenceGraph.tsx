import { useParams } from 'react-router-dom'
import { GitBranch, Network } from 'lucide-react'

export default function EvidenceGraph() {
  const { runId } = useParams()

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Evidence Graph</h2>
        <p className="text-gray-400">
          Run ID: {runId}
        </p>
      </div>

      {/* Placeholder notice */}
      <div className="glass-panel p-4 border-l-4 border-yellow-500">
        <p className="text-sm text-yellow-400">
          <strong>NOT YET IMPLEMENTED:</strong> Evidence graph visualization will be available after running an investigation with graph context.
        </p>
      </div>

      {/* Graph Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Network className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Entities</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <GitBranch className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Relationships</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Network className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Documents</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
      </div>

      {/* Graph Visualization */}
      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Graph Visualization</h3>
        <div className="bg-navy-900/50 rounded-lg p-8 border border-navy-700 min-h-[400px] flex items-center justify-center">
          <div className="text-center">
            <Network className="h-16 w-16 text-navy-600 mx-auto mb-4" />
            <p className="text-gray-500">Graph visualization will appear here</p>
            <p className="text-sm text-gray-600 mt-2">Requires TigerGraph connection and data</p>
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
              <p className="text-gray-500 italic">--</p>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Relationships Traversed</label>
            <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
              <p className="text-gray-500 italic">--</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
