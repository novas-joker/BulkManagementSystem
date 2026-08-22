import { useEffect, useState } from 'react'
import { requestPasswordReset, resetPassword, validatePasswordResetToken } from '../services/authApi'
import { getApiErrorMessage } from '../services/dashboardUi'
import { Check, Mail, X } from 'lucide-react'

function ResetShell({ children, title, subtitle }) {
  return <div className="password-reset-page"><header className="password-reset-header"><a className="auth-logo" href="#top"><span className="onboarding-logo-mark">MF</span><span><strong>MailForge</strong><small>Bulk Email for Gmail</small></span></a><span className="password-reset-postmark">MAILFORGE / PRIVATE POST</span></header><main className="password-reset-layout"><section className="password-reset-story"><span className="eyebrow">A quiet way back in</span><h1>{title}</h1><p>{subtitle}</p><div className="password-reset-seal">✦ <span>SECURE ACCOUNT MAIL</span></div></section><section className="password-reset-card">{children}</section></main></div>
}

export function ForgotPasswordPage({ onBack }) {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (event) => {
    event.preventDefault()
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setError('Please enter a valid email address.'); return }
    try { setLoading(true); setError(''); await requestPasswordReset(email); setSubmitted(true) } catch (err) { setError(getApiErrorMessage(err)) } finally { setLoading(false) }
  }

  return <ResetShell title={submitted ? <>Check your<br /><em>inbox.</em></> : <>Let’s find<br /><em>your way back.</em></>} subtitle={submitted ? 'If an account exists for that address, a reset link is on its way. It will be valid for 30 minutes.' : 'Enter the email connected to your MailForge workspace and we’ll send a secure reset link.'}>
    {submitted ? <div className="password-reset-success"><div className="password-reset-icon"><Mail size={22} /></div><h2>Reset link sent</h2><p>Check your email, including the spam folder. The message will not reveal whether an account exists.</p><button type="button" className="primary-button" onClick={onBack}>Back to sign in</button></div> : <form className="password-reset-form" onSubmit={submit}><label htmlFor="reset-email"><span>Workspace email</span><input id="reset-email" name="email" type="email" value={email} onChange={(event) => { setEmail(event.target.value); setError('') }} placeholder="you@example.com" autoComplete="email" required /></label>{error && <p className="password-reset-error" role="alert">{error}</p>}<button className="primary-button" type="submit" disabled={loading}>{loading ? 'Sending...' : 'Send reset link'} <Mail size={16} aria-hidden="true" /></button><button type="button" className="password-reset-back" onClick={onBack}>Back to sign in</button></form>}
  </ResetShell>
}

export function ResetPasswordPage({ token, onBack }) {
  const [valid, setValid] = useState(null)
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { validatePasswordResetToken(token).then((data) => setValid(data.valid)).catch(() => setValid(false)) }, [token])

  const submit = async (event) => {
    event.preventDefault()
    if (password.length < 8) { setError('Password must contain at least 8 characters.'); return }
    if (password !== confirmPassword) { setError('Passwords do not match.'); return }
    try { setLoading(true); setError(''); await resetPassword(token, password); setPassword(''); setConfirmPassword(''); setSuccess(true) } catch (err) { setError(getApiErrorMessage(err)) } finally { setLoading(false) }
  }

  return <ResetShell title={success ? <>You’re back<br /><em>in control.</em></> : <>Set a new<br /><em>password.</em></>} subtitle={success ? 'Your password has been updated and other sessions have been signed out.' : 'Choose a strong password for your MailForge workspace.'}>
    {valid === null && <p className="password-reset-status">Checking your reset link...</p>}
    {valid === false && !success && <div className="password-reset-success"><div className="password-reset-icon"><X size={22} /></div><h2>Link unavailable</h2><p>This reset link may be expired or already used.</p><button type="button" className="primary-button" onClick={onBack}>Request a new link</button></div>}
    {valid && !success && <form className="password-reset-form" autoComplete="off" onSubmit={submit}><label htmlFor="new-password"><span>New password</span><input id="new-password" name="new_password" type="password" value={password} onChange={(event) => { setPassword(event.target.value); setError('') }} autoComplete="new-password" required /></label><label htmlFor="confirm-password"><span>Confirm password</span><input id="confirm-password" name="confirm_password" type="password" value={confirmPassword} onChange={(event) => { setConfirmPassword(event.target.value); setError('') }} autoComplete="new-password" required /></label><small className="password-reset-hint">Use at least 8 characters.</small>{error && <p className="password-reset-error" role="alert">{error}</p>}<button className="primary-button" type="submit" disabled={loading}>{loading ? 'Updating...' : 'Update password'} <Check size={16} aria-hidden="true" /></button></form>}
    {success && <div className="password-reset-success"><div className="password-reset-icon"><Check size={22} /></div><h2>Password updated</h2><p>Your new password is ready to use.</p><button type="button" className="primary-button" onClick={onBack}>Return to sign in</button></div>}
  </ResetShell>
}