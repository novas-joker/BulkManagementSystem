import { useState } from 'react'

export default function AuthForm({ mode, onSubmit, loading, error, switchMode }) {
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
