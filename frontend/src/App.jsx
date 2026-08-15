import { useMemo, useState } from 'react'
import './App.css'
import { clearAuthState, getCurrentUserProfile, getStoredUser, loginUser, logoutUser, registerUser } from './services/authApi'
import LandingPage from './pages/LandingPage'
import AuthForm from './components/AuthForm'
import DashboardShell from './pages/DashboardShell'

function App() {
  const [mode, setMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [currentUser, setCurrentUser] = useState(() => getStoredUser())
  const [view, setView] = useState(currentUser ? 'dashboard' : 'landing')

  const currentUserMemo = useMemo(() => currentUser, [currentUser])

  const handleAuthSubmit = async (formData) => {
    setLoading(true)
    setError('')

    try {
      const activeMode = view === 'register' ? 'register' : 'login'

      if (activeMode === 'register') {
        await registerUser(formData)
      } else {
        await loginUser(formData)
      }

      const user = getStoredUser()
      setCurrentUser(user)
      setView('dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleViewSwitch = async (target) => {
    if (target === 'dashboard') {
      try {
        const user = await getCurrentUserProfile()
        setCurrentUser(user)
        setView('dashboard')
      } catch {
        clearAuthState()
        setCurrentUser(null)
        setView('landing')
      }
      return
    }

    setMode(target)
    setView(target)
    setError('')
  }

  const handleLogout = async () => {
    try {
      await logoutUser()
    } catch {
      clearAuthState()
    }
    setCurrentUser(null)
    setView('landing')
  }

  if (view === 'landing') {
    return <LandingPage onNavigate={handleViewSwitch} />
  }

  if (view === 'login' || view === 'register') {
    return (
      <AuthForm
        mode={view}
        onSubmit={handleAuthSubmit}
        loading={loading}
        error={error}
        switchMode={() => {
          setMode(view === 'login' ? 'register' : 'login')
          setView(view === 'login' ? 'register' : 'login')
          setError('')
        }}
      />
    )
  }

  return <DashboardShell user={currentUserMemo} onLogout={handleLogout} />
}

export default App
