import { useParams } from 'react-router-dom'
import { Activity, Clock, Zap, Layers } from 'lucide-react'

export default function AgentTrace() {
  const { runId } = useParams()

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Agent Trace</h2>
        <p className="text-gray-400">
          Run ID: {runId}
        </p>
      </div>

      {/* Placeholder notice */}
      <div className="glass-panel p-4 border-l-4 border-yellow-500">
        <p className="text-sm text-yellow-400">
          <strong>NOT YET IMPLEMENTED:</strong> Agent trace visualization will be available after running an agentic investigation.
        </p>
      </div>

      {/* Trace Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Total Steps</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Total Latency</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Zap className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Total Tokens</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
        <div className="glass-panel p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Layers className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-gray-400">Evidence Items</h3>
          </div>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
      </div>

      {/* Step-by-step trace */}
      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Execution Steps</h3>
        <div className="space-y-4">
          <div className="text-center py-8 text-gray-500">
            No trace data available for this run
          </div>
        </div>
      </div>

      {/* Stopping Reason */}
      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Stopping Reason</h3>
        <div className="bg-navy-900/50 rounded-lg p-4 border border-navy-700">
          <p className="text-gray-400 italic">--</p>
        </div>
      </div>
    </div>
  )
}
