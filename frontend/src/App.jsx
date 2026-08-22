import { useMemo, useState } from 'react'
import { authService, clearAuthState, getCurrentUserProfile, getOnboardingPhaseOne, getStoredUser, logoutUser } from './services/authApi'
import LandingPage from './pages/LandingPage'
import AuthForm from './components/AuthForm'
import DashboardShell from './pages/DashboardShell'
import { getApiErrorMessage } from './services/dashboardUi'
import OnboardingPage from './pages/OnboardingPage'
import { ForgotPasswordPage, ResetPasswordPage } from './pages/PasswordResetPage'

function App() {
  const [mode, setMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [currentUser, setCurrentUser] = useState(() => getStoredUser())
  const [view, setView] = useState(currentUser ? 'dashboard' : 'landing')
  const resetToken = new URLSearchParams(window.location.search).get('token')

  const currentUserMemo = useMemo(() => currentUser, [currentUser])

  const handleAuthSubmit = async (formData) => {
    setLoading(true)
    setError('')

    try {
      const activeMode = view === 'register' ? 'register' : 'login'

      if (activeMode === 'register') {
        await authService.register(formData)
      } else {
        await authService.login(formData)
      }

      const user = getStoredUser()
      setCurrentUser(user)
      if (activeMode === 'register') {
        setView('onboarding')
      } else {
        const onboarding = await getOnboardingPhaseOne()
        setView(onboarding.onboarding_completed ? 'dashboard' : 'onboarding')
      }
    } catch (err) {
      setError(getApiErrorMessage(err))
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

  if (window.location.pathname === '/forgot-password') {
    return <ForgotPasswordPage onBack={() => { window.history.pushState({}, '', '/'); setView('login') }} />
  }

  if (window.location.pathname === '/reset-password') {
    return <ResetPasswordPage token={resetToken || ''} onBack={() => { window.history.pushState({}, '', '/'); setView('login') }} />
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
        onForgotPassword={() => { window.history.pushState({}, '', '/forgot-password'); setView('forgot-password') }}
        switchMode={() => {
          setMode(view === 'login' ? 'register' : 'login')
          setView(view === 'login' ? 'register' : 'login')
          setError('')
        }}
      />
    )
  }

  if (view === 'onboarding') {
    return <OnboardingPage onComplete={() => setView('dashboard')} onLogout={handleLogout} />
  }

  return <DashboardShell user={currentUserMemo} onLogout={handleLogout} />
}

export default App
