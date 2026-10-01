import { Link, useLocation } from 'react-router-dom'
import { Search, BarChart3, GitBranch, Settings, Home } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Overview', icon: Home },
  { path: '/investigate', label: 'Investigate', icon: Search },
  { path: '/compare', label: 'Compare', icon: GitBranch },
  { path: '/metrics', label: 'Metrics', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-navy-900">
      {/* Header */}
      <header className="border-b border-navy-700 bg-navy-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded bg-gradient-to-br from-cyan-400 to-cyan-500"></div>
              <div>
                <h1 className="text-xl font-bold text-gray-100">GraphProbe AI</h1>
                <p className="text-xs text-cyan-400">Investigate. Connect. Verify.</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 border-r border-navy-700 bg-navy-800/30 min-h-[calc(100vh-73px)]">
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path || 
                              (item.path !== '/' && location.pathname.startsWith(item.path))
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' 
                      : 'text-gray-400 hover:bg-navy-700 hover:text-gray-100'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
