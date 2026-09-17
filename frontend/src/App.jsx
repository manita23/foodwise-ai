import { lazy, Suspense } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'

const Dashboard    = lazy(() => import('./pages/Dashboard'))
const ForecastPage = lazy(() => import('./pages/ForecastPage'))
const WastePage    = lazy(() => import('./pages/WastePage'))
const QAPage       = lazy(() => import('./pages/QAPage'))
const ApprovalsPage= lazy(() => import('./pages/ApprovalsPage'))

const nav = [
  { to: '/',             label: '📊 Dashboard'    },
  { to: '/forecast',     label: '📈 Forecast'     },
  { to: '/waste',        label: '🗑️ Waste'        },
  { to: '/qa',           label: '💬 Ask AI'       },
  { to: '/approvals',    label: '✅ Approvals'    },
]

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="bg-blue-700 text-white px-6 py-3 flex items-center gap-4 shadow">
        <span className="text-xl font-bold tracking-tight">🍽️ FoodWise AI</span>
        <span className="text-blue-200 text-sm">powered by IBM Granite</span>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <nav className="w-44 bg-white border-r border-gray-200 pt-4 flex flex-col gap-1 shrink-0">
          {nav.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-4 py-2 text-sm rounded-r-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">
          <Suspense fallback={<p className="text-gray-400 text-sm">Loading…</p>}>
            <Routes>
              <Route path="/"           element={<Dashboard />} />
              <Route path="/forecast"   element={<ForecastPage />} />
              <Route path="/waste"      element={<WastePage />} />
              <Route path="/qa"         element={<QAPage />} />
              <Route path="/approvals"  element={<ApprovalsPage />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  )
}
