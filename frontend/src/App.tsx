import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Overview from './pages/Overview'
import Investigate from './pages/Investigate'
import Compare from './pages/Compare'
import Metrics from './pages/Metrics'
import AgentTrace from './pages/AgentTrace'
import EvidenceGraph from './pages/EvidenceGraph'
import Settings from './pages/Settings'
import { InvestigationProvider } from './contexts/InvestigationContext'

function App() {
  return (
    <BrowserRouter>
      <InvestigationProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/investigate" element={<Investigate />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/metrics" element={<Metrics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/agent-trace/:runId" element={<AgentTrace />} />
            <Route path="/evidence/:runId" element={<EvidenceGraph />} />
          </Routes>
        </Layout>
      </InvestigationProvider>
    </BrowserRouter>
  )
}

export default App
