import { useMemo, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import {
  clearAuthState,
  getCurrentUserProfile,
  getStoredUser,
  loginUser,
  registerUser,
} from './services/authApi'

function LandingPage({ onNavigate }) {
  return (
    <div className="landing-shell">
      <nav className="topbar">
        <div className="brand">
          <span className="brand-mark">M</span>
          <span>MailForge</span>
        </div>
        <div className="nav-actions">
          <button className="secondary-button" onClick={() => onNavigate('login')}>
            Login
          </button>
          <button className="primary-button" onClick={() => onNavigate('register')}>
            Create account
          </button>
        </div>
      </nav>

      <main className="hero-section">
        <div className="hero-copy">
          <span className="eyebrow">Bulk campaign management</span>
          <h1>Launch smarter email campaigns from one place.</h1>
          <p>
            Manage contacts, create campaigns, and track engagement with a clean
            workflow designed for modern marketing teams.
          </p>
          <div className="cta-row">
            <button className="primary-button" onClick={() => onNavigate('register')}>
              Get started
            </button>
            <button className="secondary-button" onClick={() => onNavigate('login')}>
              Sign in
            </button>
          </div>
          <ul className="feature-list">
            <li>Audience segmentation</li>
            <li>Template-driven sends</li>
            <li>Delivery analytics</li>
          </ul>
        </div>

        <div className="hero-card">
          <div className="mini-card">
            <span className="mini-label">Campaign health</span>
            <strong>92.4%</strong>
            <small>Delivery rate</small>
          </div>
          <div className="stats-grid">
            <div>
              <span>Audience</span>
              <strong>24.8k</strong>
            </div>
            <div>
              <span>Templates</span>
              <strong>18</strong>
            </div>
            <div>
              <span>Opens</span>
              <strong>41%</strong>
            </div>
            <div>
              <span>CTR</span>
              <strong>6.8%</strong>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function AuthForm({ mode, onSubmit, loading, error, switchMode }) {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
  })

  const isRegister = mode === 'register'

  const handleChange = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit(form)
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-header">
          <span className="eyebrow">MailForge</span>
          <h2>{isRegister ? 'Create your account' : 'Welcome back'}</h2>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {isRegister && (
            <label>
              <span>Full name</span>
              <input
                type="text"
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                placeholder="Jane Doe"
                required
              />
            </label>
          )}

          <label>
            <span>Email</span>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="********"
              required
              minLength="8"
            />
          </label>

          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="primary-button form-submit" disabled={loading}>
            {loading ? 'Please wait...' : isRegister ? 'Sign up' : 'Login'}
          </button>
        </form>

        <p className="auth-switch">
          {isRegister ? 'Already have an account?' : 'Need an account?'}{' '}
          <button type="button" className="text-button" onClick={switchMode}>
            {isRegister ? 'Login' : 'Register'}
          </button>
        </p>
      </div>
    </div>
  )
}

function DashboardShell({ user, onLogout }) {
  const navItems = ['Overview', 'Contacts', 'Campaigns', 'Templates', 'Reports']

  return (
    <div className="dashboard-shell">
      <aside className="sidebar">
        <div className="brand sidebar-brand">
          <span className="brand-mark">M</span>
          <span>MailForge</span>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button key={item} className={item === 'Overview' ? 'nav-item active' : 'nav-item'}>
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="avatar">{user?.full_name?.charAt(0) || 'U'}</div>
          <div>
            <strong>{user?.full_name || 'User'}</strong>
            <small>{user?.email || 'user@example.com'}</small>
          </div>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <span className="eyebrow">Overview</span>
            <h1>Welcome back, {user?.full_name?.split(' ')[0] || 'there'}.</h1>
          </div>
          <button className="secondary-button" onClick={onLogout}>
            Logout
          </button>
        </header>

        <section className="stats-row">
          <div className="stat-card">
            <span>Total contacts</span>
            <strong>12,480</strong>
          </div>
          <div className="stat-card">
            <span>Active campaigns</span>
            <strong>08</strong>
          </div>
          <div className="stat-card">
            <span>Open rate</span>
            <strong>41.8%</strong>
          </div>
          <div className="stat-card">
            <span>Revenue</span>
            <strong>$8.4k</strong>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <h3>Campaign performance</h3>
            <div className="chart-bars">
              <span style={{ height: '35%' }} />
              <span style={{ height: '52%' }} />
              <span style={{ height: '66%' }} />
              <span style={{ height: '58%' }} />
              <span style={{ height: '80%' }} />
              <span style={{ height: '94%' }} />
            </div>
          </div>

          <div className="panel">
            <h3>Recent activity</h3>
            <ul className="activity-list">
              <li>Welcome campaign sent to 1,200 users</li>
              <li>New template published</li>
              <li>Audience segment updated</li>
            </ul>
          </div>
        </section>
      </main>
    </div>
  )
}

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

  const handleLogout = () => {
    clearAuthState()
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

export default function AppRoot() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
