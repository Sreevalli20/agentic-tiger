import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Server, Database, Cpu, Shield, CheckCircle, XCircle } from 'lucide-react'
import { api } from '../services/api'

interface ConfigData {
  llm_provider: string
  llm_model: string
  llm_configured: boolean
  tigergraph_host: string
  tigergraph_port: number
  tigergraph_graph: string
  tigergraph_configured: boolean
  vector_db_path: string
  embedding_model: string
  max_agent_iterations: number
  evidence_sufficiency_threshold: number
  max_token_budget: number
}

export default function Settings() {
  const [config, setConfig] = useState<ConfigData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const data = await api.config() as ConfigData
      setConfig(data)
      setError(null)
    } catch (err) {
      console.error('Failed to load config:', err)
      setError('Failed to load configuration')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading configuration...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Settings</h2>
        <div className="text-red-400 mb-4">{error}</div>
        <button
          onClick={loadConfig}
          className="btn-primary"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Settings</h2>
        <div className="text-gray-400">No configuration available</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <div className="flex items-center space-x-3 mb-6">
          <SettingsIcon className="h-6 w-6 text-cyan-400" />
          <h2 className="text-2xl font-bold text-gray-100">Configuration</h2>
        </div>
        <p className="text-gray-400 mb-6">View the current system configuration. These settings are managed on the backend.</p>

        <div className="grid gap-6">
          {/* LLM Configuration */}
          <div className="bg-navy-800/50 rounded-lg p-4 border border-navy-700">
            <div className="flex items-center space-x-2 mb-3">
              <Cpu className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-gray-100">LLM Configuration</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Provider</span>
                <span className="text-gray-100 font-medium">{config.llm_provider}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Model</span>
                <span className="text-gray-100 font-medium">{config.llm_model}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Status</span>
                {config.llm_configured ? (
                  <div className="flex items-center space-x-2 text-green-400">
                    <CheckCircle className="h-4 w-4" />
                    <span className="font-medium">Configured</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-red-400">
                    <XCircle className="h-4 w-4" />
                    <span className="font-medium">Not Configured</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* TigerGraph Configuration */}
          <div className="bg-navy-800/50 rounded-lg p-4 border border-navy-700">
            <div className="flex items-center space-x-2 mb-3">
              <Server className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-gray-100">TigerGraph Configuration</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Host</span>
                <span className="text-gray-100 font-medium">{config.tigergraph_host}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Port</span>
                <span className="text-gray-100 font-medium">{config.tigergraph_port}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Graph</span>
                <span className="text-gray-100 font-medium">{config.tigergraph_graph}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Status</span>
                {config.tigergraph_configured ? (
                  <div className="flex items-center space-x-2 text-green-400">
                    <CheckCircle className="h-4 w-4" />
                    <span className="font-medium">Configured</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-red-400">
                    <XCircle className="h-4 w-4" />
                    <span className="font-medium">Not Configured</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Vector Database Configuration */}
          <div className="bg-navy-800/50 rounded-lg p-4 border border-navy-700">
            <div className="flex items-center space-x-2 mb-3">
              <Database className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-gray-100">Vector Database</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Path</span>
                <span className="text-gray-100 font-medium">{config.vector_db_path}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Embedding Model</span>
                <span className="text-gray-100 font-medium">{config.embedding_model}</span>
              </div>
            </div>
          </div>

          {/* Agent Configuration */}
          <div className="bg-navy-800/50 rounded-lg p-4 border border-navy-700">
            <div className="flex items-center space-x-2 mb-3">
              <Shield className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-gray-100">Agent Configuration</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Max Iterations</span>
                <span className="text-gray-100 font-medium">{config.max_agent_iterations}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Evidence Threshold</span>
                <span className="text-gray-100 font-medium">{(config.evidence_sufficiency_threshold * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Max Token Budget</span>
                <span className="text-gray-100 font-medium">{config.max_token_budget.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
