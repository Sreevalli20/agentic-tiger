import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function Metrics() {
  // Placeholder data - will be replaced with real benchmark data
  const accuracyData = [
    { name: 'RAG', accuracy: 75 },
    { name: 'GraphRAG', accuracy: 82 },
    { name: 'Agentic', accuracy: 88 },
  ]

  const latencyData = [
    { name: 'RAG', latency: 1200 },
    { name: 'GraphRAG', latency: 1800 },
    { name: 'Agentic', latency: 3500 },
  ]

  const tokenData = [
    { name: 'RAG', tokens: 450 },
    { name: 'GraphRAG', tokens: 600 },
    { name: 'Agentic', tokens: 1200 },
  ]

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Metrics Dashboard</h2>
        <p className="text-gray-400">
          Real benchmark results comparing RAG, GraphRAG, and Agentic GraphRAG performance
        </p>
      </div>

      {/* Notice about real data */}
      <div className="glass-panel p-4 border-l-4 border-yellow-500">
        <p className="text-sm text-yellow-400">
          <strong>DEMO DATA:</strong> No benchmark results available yet. Run the benchmark to generate real metrics.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Total Questions</h3>
          <p className="text-2xl font-bold text-gray-100">0</p>
        </div>
        <div className="glass-panel p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Avg Accuracy</h3>
          <p className="text-2xl font-bold text-cyan-400">--</p>
        </div>
        <div className="glass-panel p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Avg Latency</h3>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
        <div className="glass-panel p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Avg Tokens</h3>
          <p className="text-2xl font-bold text-gray-100">--</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Accuracy Chart */}
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Accuracy by Pipeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
              <XAxis dataKey="name" stroke="#8892b0" />
              <YAxis stroke="#8892b0" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#112240', border: '1px solid #233554' }}
                itemStyle={{ color: '#8892b0' }}
              />
              <Bar dataKey="accuracy" fill="#64ffda" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Latency Chart */}
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Latency by Pipeline (ms)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
              <XAxis dataKey="name" stroke="#8892b0" />
              <YAxis stroke="#8892b0" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#112240', border: '1px solid #233554' }}
                itemStyle={{ color: '#8892b0' }}
              />
              <Bar dataKey="latency" fill="#00b4d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Token Usage Chart */}
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Token Usage by Pipeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={tokenData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
              <XAxis dataKey="name" stroke="#8892b0" />
              <YAxis stroke="#8892b0" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#112240', border: '1px solid #233554' }}
                itemStyle={{ color: '#8892b0' }}
              />
              <Bar dataKey="tokens" fill="#64ffda" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Classification */}
        <div className="glass-panel p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Question Classification</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-400">RAG Sufficient</span>
                <span className="text-sm text-cyan-400">0</span>
              </div>
              <div className="h-2 bg-navy-900 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-400 w-0"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-400">GraphRAG Useful</span>
                <span className="text-sm text-cyan-400">0</span>
              </div>
              <div className="h-2 bg-navy-900 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-400 w-0"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-400">Agentic Investigation Useful</span>
                <span className="text-sm text-cyan-400">0</span>
              </div>
              <div className="h-2 bg-navy-900 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-400 w-0"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
