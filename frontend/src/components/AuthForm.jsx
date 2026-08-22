import { useEffect, useState } from 'react'
import { requestPasswordReset } from '../services/authApi'
import { ArrowUpRight, Check, Eye, EyeOff, LockKeyhole, Mail, UserRound } from 'lucide-react'

function AuthLogo() {
  return <span className="auth-logo"><svg viewBox="0 0 34 34" aria-hidden="true"><path d="M4.5 9.5 17 19 29.5 9.5v15H4.5z" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round"/><path d="m5 9 12 9 12-9M17 19V5m-3.8 3.8L17 5l3.8 3.8" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"/></svg><span><strong>MailForge</strong><small>Bulk Email for Gmail</small></span></span>
}

function EnvelopeMark() {
  return <span className="auth-envelope-mark" aria-hidden="true"><svg viewBox="0 0 48 38"><path d="M3 7.5 24 24 45 7.5v25H3z" fill="#f0edff" stroke="#6847ff" strokeWidth="2"/><path d="m4 8 20 16L44 8" fill="none" stroke="#6847ff" strokeWidth="2"/><path d="M24 24V4m-6 6 6-6 6 6" fill="none" stroke="#3347c7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></span>
}

function MailboxIllustration() {
  return <svg className="auth-mailbox" viewBox="0 0 360 250" role="img" aria-label="MailForge envelope and mailbox illustration"><ellipse cx="178" cy="224" rx="106" ry="12" fill="#ddd9f3" opacity=".7"/><path d="M145 142h67v74h-67z" fill="#5a45d8"/><path d="M160 142h38v74h-38z" fill="#7967e9"/><path d="M78 144V83c0-35 28-63 63-63h72c35 0 63 28 63 63v61H78Z" fill="#6847ff"/><path d="M98 130V84c0-25 20-45 45-45h67c25 0 45 20 45 45v46H98Z" fill="#faf9ff"/><path d="M98 130h157v15H78v-15z" fill="#5030d9" opacity=".8"/><path d="m180 107 58-42 16 19-74 53-74-53 16-19z" fill="#fff" stroke="#d8d2f4" strokeWidth="3"/><path d="m106 84 74 53 74-53" fill="none" stroke="#c1baf0" strokeWidth="3"/><path d="M259 101V54l23-11v58z" fill="#5030d9"/><path d="M282 43V25c0-6-5-10-11-10h-20v11h20v17z" fill="#6847ff"/><circle cx="232" cy="79" r="8" fill="#fff" stroke="#6847ff" strokeWidth="2"/><path d="m228 79 3 3 6-7" fill="none" stroke="#6847ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
}

function FieldIcon({ type }) {
  if (type === 'person') return <UserRound size={18} aria-hidden="true" />
  if (type === 'email') return <Mail size={18} aria-hidden="true" />
  return <LockKeyhole size={18} aria-hidden="true" />
}

function EyeIcon({ hidden }) {
  return hidden ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />
}

function Benefits() {
  return <div className="auth-benefits"><div><span><Check size={16} /></span><p><strong>Secure by default</strong><small>Your data is encrypted and never shared.</small></p></div><div><span><ArrowUpRight size={16} /></span><p><strong>Works in Gmail</strong><small>Seamlessly connect and send emails from Gmail.</small></p></div><div><span><Mail size={16} /></span><p><strong>Track what matters</strong><small>Monitor opens, clicks, and results in real time.</small></p></div></div>
}

function SignupLetter() {
  return <><article className="signup-letter"><div className="signup-letter-top"><span>MAILFORGE / POST</span><span className="letter-stamp">MF</span></div><div className="letter-cancel">✦ &nbsp; MF &nbsp; ✦ &nbsp; MF</div><p>“MailForge has completely simplified how we run email campaigns. It just works.”</p><div className="signup-letter-footer"><span className="letter-avatar">SM</span><span><strong>Sophia Martinez</strong><small>Growth Marketer, Acme Inc.</small></span><b>★★★★★</b></div></article><FlowDiagram /></>
}

function FlowDiagram() {
  return <div className="flow-diagram" aria-label="MailForge flow: create a mailbox, prepare a letter, send it by paper plane, and receive a response"><div className="flow-track"><svg viewBox="0 0 420 120" aria-hidden="true"><path d="M28 78C108 12 171 108 239 54s102-35 153-13"/><path className="flow-track-dash" d="M28 78C108 12 171 108 239 54s102-35 153-13"/></svg></div><div className="flow-step flow-step-mailbox"><span className="flow-icon"><span className="mini-mailbox" /></span><strong>Create</strong><small>your mailbox</small></div><div className="flow-step flow-step-letter"><span className="flow-icon"><span className="mini-letter" /></span><strong>Prepare</strong><small>your campaign</small></div><div className="flow-step flow-step-plane"><span className="flow-icon"><span className="mini-plane">↗</span></span><strong>Send</strong><small>with MailForge</small></div><div className="flow-step flow-step-response"><span className="flow-icon"><span className="mini-response">↩</span></span><strong>Receive</strong><small>real responses</small></div><span className="flow-spark spark-a">✦</span><span className="flow-spark spark-b">·</span></div>
}

function AuthFormContent({ mode, onSubmit, loading, error, switchMode, forgotControl }) {
  const isRegister = mode === 'register'
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [touched, setTouched] = useState({})
  const [localError, setLocalError] = useState('')

  useEffect(() => {
    const clearAutofilledPasswords = () => {
      document.querySelectorAll('.signup-page input[type="password"]').forEach((input) => {
        input.value = ''
      })
    }

    clearAutofilledPasswords()
    const timer = window.setTimeout(clearAutofilledPasswords, 100)
    return () => window.clearTimeout(timer)
  }, [mode])

  const updateField = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setTouched((current) => ({ ...current, [name]: true }))
    setLocalError('')
  }

  const validate = () => {
    if (isRegister && form.full_name.trim().length < 2) return 'Please enter your full name.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'Please enter a valid email address.'
    if (form.password.length < 8) return 'Password must contain at least 8 characters.'
    if (isRegister && !termsAccepted) return 'Please agree to the Terms of Service and Privacy Policy.'
    return ''
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    setTouched({ full_name: true, email: true, password: true })
    const validationError = validate()
    if (validationError) { setLocalError(validationError); return }
    onSubmit(isRegister ? form : { email: form.email, password: form.password })
  }

  if (!isRegister) {
    return <div className="signup-page login-page"><div className="signup-background" aria-hidden="true"><svg viewBox="0 0 1200 800" preserveAspectRatio="none"><path d="M-40 540C180 270 305 680 520 420s300-180 440-15 235 80 340-160"/><path d="M-40 190c220 190 380-50 570 120s340 230 720-55"/><path d="M90 0c170 180 280 240 450 115s320-85 630 90"/></svg><span className="signup-dot signup-dot-one"/><span className="signup-dot signup-dot-two"/><span className="signup-paper signup-paper-one">↗</span><span className="signup-paper signup-paper-two">+</span><span className="signup-orbit"/></div><header className="auth-header-bar"><a href="#top" aria-label="MailForge home"><AuthLogo /></a><p>Need an account? <button type="button" onClick={switchMode}>Create one <span>→</span></button></p></header><main className="signup-layout login-layout"><section className="signup-story"><div className="signup-hero-illustration"><MailboxIllustration /></div><div className="signup-story-copy"><span className="eyebrow">Welcome back to your workspace</span><h1>Pick up<br /><span>where you</span><br /><em>left off.</em></h1><p>Your campaigns, contacts, and thoughtful follow-ups are ready when you are.</p><Benefits /></div></section><section className="signup-card-wrap"><div className="signup-card"><div className="signup-card-heading"><EnvelopeMark /><h2>Welcome back</h2><p>Sign in to your MailForge workspace</p></div><div className="mail-divider"><span />✉<span /></div><form className="signup-form" onSubmit={handleSubmit} noValidate><label className="signup-field"><span>Email</span><div><FieldIcon type="email" /><input type="email" name="email" value={form.email} onChange={updateField} onBlur={() => setTouched((current) => ({ ...current, email: true }))} placeholder="Enter your email" autoComplete="email" required /></div></label><label className="signup-field"><span>Password</span><div><FieldIcon type="password" /><input type={showPassword ? 'text' : 'password'} name="password" value={form.password} onChange={updateField} onBlur={() => setTouched((current) => ({ ...current, password: true }))} placeholder="Enter your password" autoComplete="current-password" required /><button type="button" className="password-toggle" onClick={() => setShowPassword((current) => !current)} aria-label={showPassword ? 'Hide password' : 'Show password'}><EyeIcon hidden={!showPassword} /></button></div></label>{forgotControl}{error && <p className="signup-error" role="alert">{error}</p>}<button type="submit" className="create-account-button" disabled={loading}>{loading ? <><span className="loading-spinner" /> Signing in...</> : <>Sign in <span>→</span></>}</button></form><div className="security-badge"><span>✓</span><strong>Private by default</strong><i /><span>✦</span><strong>Your workspace awaits</strong></div></div><SignupLetter /></section><aside className="signup-aside"><FlowDiagram /></aside></main></div>
  }

  const displayedError = localError || error
  return <div className="signup-page"><div className="signup-background" aria-hidden="true"><svg viewBox="0 0 1200 800" preserveAspectRatio="none"><path d="M-40 540C180 270 305 680 520 420s300-180 440-15 235 80 340-160"/><path d="M-40 190c220 190 380-50 570 120s340 230 720-55"/><path d="M90 0c170 180 280 240 450 115s320-85 630 90"/></svg><span className="signup-dot signup-dot-one"/><span className="signup-dot signup-dot-two"/><span className="signup-paper signup-paper-one">↗</span><span className="signup-paper signup-paper-two">+</span><span className="signup-orbit"/></div><header className="auth-header-bar"><a href="#top" aria-label="MailForge home"><AuthLogo /></a><p>Already have an account? <button type="button" onClick={switchMode}>Sign in <span>→</span></button></p></header><main className="signup-layout"><section className="signup-story"><div className="signup-hero-illustration"><MailboxIllustration /></div><div className="signup-story-copy"><span className="eyebrow">Your first piece of MailForge</span><h1>Create your<br /><span>MailForge</span><br /><em>account</em></h1><p>Start sending smarter emails from your Gmail workspace in just a few steps.</p><Benefits /></div></section><section className="signup-card-wrap"><div className="signup-card"><div className="signup-card-heading"><EnvelopeMark /><h2>Welcome to MailForge</h2><p>Let's create your account</p></div><div className="mail-divider"><span />✉<span /></div><form className="signup-form" onSubmit={handleSubmit} noValidate><label className={`signup-field ${touched.full_name && form.full_name.trim().length < 2 ? 'has-error' : ''}`}><span>Full name</span><div><FieldIcon type="person" /><input type="text" name="full_name" value={form.full_name} onChange={updateField} onBlur={() => setTouched((current) => ({ ...current, full_name: true }))} placeholder="Enter your full name" autoComplete="name" aria-invalid={touched.full_name && form.full_name.trim().length < 2} required /></div></label><label className={`signup-field ${touched.email && form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? 'has-error' : ''}`}><span>Email</span><div><FieldIcon type="email" /><input type="email" name="email" value={form.email} onChange={updateField} onBlur={() => setTouched((current) => ({ ...current, email: true }))} placeholder="Enter your email" autoComplete="email" required /></div></label><label className={`signup-field ${touched.password && form.password.length < 8 ? 'has-error' : ''}`}><span>Password</span><div><FieldIcon type="password" /><input type={showPassword ? 'text' : 'password'} name="password" value={form.password} onChange={updateField} onBlur={() => setTouched((current) => ({ ...current, password: true }))} placeholder="Create a strong password" autoComplete="new-password" required /><button type="button" className="password-toggle" onClick={() => setShowPassword((current) => !current)} aria-label={showPassword ? 'Hide password' : 'Show password'}><EyeIcon hidden={!showPassword} /></button></div></label><p className="password-note">Use at least 8 characters with a mix of letters, numbers &amp; symbols.</p><label className="terms-row"><input type="checkbox" checked={termsAccepted} onChange={(event) => setTermsAccepted(event.target.checked)} required /><span className="custom-check">✓</span><span>I agree to the <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a></span></label>{displayedError && <p className="signup-error" role="alert">{displayedError}</p>}<button type="submit" className="create-account-button" disabled={loading}>{loading ? <><span className="loading-spinner" /> Creating account...</> : <>Create account <span>→</span></>}</button></form><div className="security-badge"><span>✓</span><strong>No credit card required</strong><i /> <span>✦</span><strong>Free to get started</strong></div></div><SignupLetter /></section><aside className="signup-aside"><div className="aside-envelope">✉</div><p>Every thoughtful campaign<br />starts with a blank page.</p><span>MAIL / MF-001</span></aside></main></div>
}

export default function AuthForm({ mode, onSubmit, loading, error, switchMode }) {
  const [forgotState, setForgotState] = useState({ loading: false, message: '', error: '' })

  const handleForgotPassword = async () => {
    const email = document.querySelector('input[name="email"]')?.value.trim() || ''
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setForgotState({ loading: false, message: '', error: 'Enter a valid email address first.' })
      return
    }

    try {
      setForgotState({ loading: true, message: '', error: '' })
      await requestPasswordReset(email)
      setForgotState({ loading: false, message: 'If an account exists, a reset link has been sent.', error: '' })
    } catch {
      setForgotState({ loading: false, message: '', error: 'We could not send the reset link. Please try again.' })
    }
  }

  const forgotControl = mode === 'login' ? <div className="auth-forgot-area"><button type="button" className="auth-forgot-link" onClick={handleForgotPassword} disabled={forgotState.loading}>{forgotState.loading ? 'Sending reset link...' : 'Forgot your password?'}</button>{forgotState.error && <span className="auth-forgot-message auth-forgot-message--error" role="alert">{forgotState.error}</span>}{forgotState.message && <span className="auth-forgot-message" role="status">{forgotState.message}</span>}</div> : null
  return <AuthFormContent mode={mode} onSubmit={onSubmit} loading={loading} error={error} switchMode={switchMode} forgotControl={forgotControl} />
}
