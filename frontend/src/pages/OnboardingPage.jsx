import { useEffect, useState } from 'react'
import { getOnboardingPhaseOne, saveOnboardingPhaseOne } from '../services/authApi'
import { getApiErrorMessage } from '../services/dashboardUi'

const phases = [
  { label: 'Audience & source', eyebrow: 'A thoughtful beginning', title: <>Let’s make room<br /><em>for your audience.</em></>, description: 'A quick estimate helps us shape the right starting point for your MailForge workspace.' },
  { label: 'Business profile', eyebrow: 'Make it yours', title: <>Tell us what<br /><em>you’re building.</em></>, description: 'This gives your workspace a little more context. Your website is optional.' },
  { label: 'Compliance address', eyebrow: 'Send responsibly', title: <>A clear address<br /><em>builds trust.</em></>, description: 'Marketing emails need a physical address in their footer. We’ll keep it ready for every send.' },
  { label: 'Your first goal', eyebrow: 'Choose your direction', title: <>What would feel<br /><em>like a win?</em></>, description: 'We’ll use your answer to make the first steps in your workspace feel relevant.' },
  { label: 'Product updates', eyebrow: 'One last choice', title: <>Stay close to<br /><em>what’s next.</em></>, description: 'Occasional notes about new MailForge features. You’re always in control.' },
]

const subscriberOptions = [['less_than_500', 'Less than 500', 'A small, focused audience'], ['500_to_1000', '500 - 1,000', 'Growing an engaged list'], ['1000_to_5000', '1,000 - 5,000', 'A busy sending rhythm'], ['more_than_5000', 'More than 5,000', 'A larger audience to reach']]
const toolOptions = [['none', 'I am starting fresh'], ['mailerlite', 'MailerLite'], ['mailchimp', 'Mailchimp'], ['convertkit', 'ConvertKit'], ['other', 'Another tool']]
const industryOptions = [['ecommerce', 'Ecommerce'], ['saas', 'Software & SaaS'], ['agency', 'Agency or consulting'], ['creator', 'Creator or publication'], ['other', 'Something else']]
const goalOptions = [['send_first_email', 'Send my first email', 'Start a campaign and reach your audience'], ['organize_contacts', 'Organize my contacts', 'Bring lists, tags, and segments together'], ['improve_results', 'Understand my results', 'Learn what makes each send work'], ['explore', 'Just explore for now', 'Take a calm tour before deciding']]
const countries = ['India', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Singapore', 'Other']

function OnboardingMark({ phase }) {
  return <div className="onboarding-mark" aria-hidden="true"><span>{String(phase).padStart(2, '0')}</span><svg viewBox="0 0 50 40"><path d="M4 8 25 24 46 8v28H4z" fill="none" stroke="currentColor" strokeWidth="2" /><path d="m5 9 20 15L45 9M25 24V4m-6 6 6-6 6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg></div>
}

function Choice({ name, value, label, description, selected, onChange, compact = false }) {
  return <label className={`onboarding-option ${compact ? 'onboarding-option--compact' : ''} ${selected ? 'is-selected' : ''}`}><input type="radio" name={name} value={value} checked={selected} onChange={onChange} /><span className="onboarding-radio" /><span><strong>{label}</strong>{description && <small>{description}</small>}</span></label>
}

export default function OnboardingPage({ onComplete, onLogout }) {
  const [phase, setPhase] = useState(1)
  const [form, setForm] = useState({ subscriber_count_bracket: '', previous_tool: '', business_industry: '', business_website: '', compliance_address: { street: '', city: '', country: '' }, user_primary_goal: '', product_updates_consent: null })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const current = phases[phase - 1]

  useEffect(() => {
    getOnboardingPhaseOne().then((data) => {
      setForm((value) => ({ ...value, ...data, compliance_address: { ...value.compliance_address, ...(data.compliance_address || {}) } }))
      setPhase(Math.min(data.onboarding_phase || 1, 5))
    }).catch((err) => setError(getApiErrorMessage(err))).finally(() => setLoading(false))
  }, [])

  const update = (field, value) => setForm((currentForm) => ({ ...currentForm, [field]: value }))
  const updateAddress = (field, value) => setForm((currentForm) => ({ ...currentForm, compliance_address: { ...currentForm.compliance_address, [field]: value } }))

  const validate = () => {
    if (phase === 1 && (!form.subscriber_count_bracket || !form.previous_tool)) return 'Choose your audience size and tell us where you are starting from.'
    if (phase === 2 && !form.business_industry) return 'Choose the industry that best fits your business.'
    if (phase === 3 && (!form.compliance_address.street.trim() || !form.compliance_address.city.trim() || !form.compliance_address.country.trim())) return 'Complete your street address, city, and country.'
    if (phase === 4 && !form.user_primary_goal) return 'Choose the goal that matters most right now.'
    if (phase === 5 && form.product_updates_consent === null) return 'Choose whether you would like product updates.'
    return ''
  }

  const submit = async (event) => {
    event.preventDefault()
    const validationError = validate()
    if (validationError) { setError(validationError); return }
    const isComplete = phase === 5
    try {
      setSaving(true)
      setError('')
      await saveOnboardingPhaseOne({ ...form, onboarding_phase: isComplete ? 5 : phase + 1, onboarding_completed: isComplete })
      if (isComplete) onComplete()
      else setPhase((value) => value + 1)
    } catch (err) { setError(getApiErrorMessage(err)) } finally { setSaving(false) }
  }

  if (loading) return <div className="onboarding-page"><div className="onboarding-loading">Preparing your workspace...</div></div>

  return <div className="onboarding-page">
    <header className="onboarding-header"><a className="auth-logo" href="#top"><span className="onboarding-logo-mark">MF</span><span><strong>MailForge</strong><small>Bulk Email for Gmail</small></span></a><nav className="onboarding-breadcrumbs" aria-label="Breadcrumb"><span>Account</span><span>/</span><strong>Onboarding</strong></nav><button type="button" className="onboarding-exit" onClick={onLogout}>Sign out</button></header>
    <main className="onboarding-layout"><section className="onboarding-intro"><OnboardingMark phase={phase} /><span className="eyebrow">{current.eyebrow}</span><h1>{current.title}</h1><p>{current.description}</p><div className="onboarding-note"><span>✦</span><p><strong>A few thoughtful answers, then you’re in.</strong><small>You can update these details later in workspace settings.</small></p></div></section>
      <section className="onboarding-card"><nav className="onboarding-flow-progress" aria-label="Onboarding progress">{phases.map((item, index) => { const step = index + 1; const state = step < phase ? 'is-completed' : step === phase ? 'is-active' : 'is-upcoming'; return <button type="button" key={item.label} className={`onboarding-flow-step ${state}`} onClick={() => step <= phase && setPhase(step)} disabled={step > phase}><span>{step < phase ? '✓' : step}</span><small>{item.label}</small></button> })}</nav><form onSubmit={submit}>
        {phase === 1 && <><fieldset><legend>How many subscribers do you have?</legend><p className="onboarding-helper">An estimate is perfect. We’ll use it to tune your first view.</p><div className="onboarding-options onboarding-options--audience">{subscriberOptions.map(([value, label, description]) => <Choice key={value} name="subscriber_count_bracket" value={value} label={label} description={description} selected={form.subscriber_count_bracket === value} onChange={(event) => update('subscriber_count_bracket', event.target.value)} />)}</div></fieldset><fieldset><legend>Where are you coming from?</legend><p className="onboarding-helper">This helps us understand what you want to bring with you.</p><div className="onboarding-options">{toolOptions.map(([value, label]) => <Choice key={value} name="previous_tool" value={value} label={label} compact selected={form.previous_tool === value} onChange={(event) => update('previous_tool', event.target.value)} />)}</div></fieldset></>}
        {phase === 2 && <><fieldset><legend>What kind of business are you?</legend><p className="onboarding-helper">Choose the closest fit. You can change this later.</p><div className="onboarding-options">{industryOptions.map(([value, label]) => <Choice key={value} name="business_industry" value={value} label={label} compact selected={form.business_industry === value} onChange={(event) => update('business_industry', event.target.value)} />)}</div></fieldset><label className="onboarding-text-field" htmlFor="business-website"><span>Business website <small>Optional</small></span><input id="business-website" name="business_website" type="url" value={form.business_website} onChange={(event) => update('business_website', event.target.value)} placeholder="https://yourwebsite.com" /></label></>}
        {phase === 3 && <fieldset><legend>Where is your business based?</legend><p className="onboarding-helper">This address appears in the footer of your marketing emails.</p><div className="onboarding-address"><label className="onboarding-text-field" htmlFor="compliance-street"><span>Street address</span><input id="compliance-street" name="street" value={form.compliance_address.street} onChange={(event) => updateAddress('street', event.target.value)} placeholder="123 Market Street" /></label><div className="onboarding-address-row"><label className="onboarding-text-field" htmlFor="compliance-city"><span>City</span><input id="compliance-city" name="city" value={form.compliance_address.city} onChange={(event) => updateAddress('city', event.target.value)} placeholder="Austin" /></label><label className="onboarding-text-field" htmlFor="compliance-country"><span>Country</span><select id="compliance-country" name="country" value={form.compliance_address.country} onChange={(event) => updateAddress('country', event.target.value)}><option value="">Choose a country</option>{countries.map((country) => <option key={country} value={country}>{country}</option>)}</select></label></div></div></fieldset>}
        {phase === 4 && <fieldset><legend>What is your top priority?</legend><p className="onboarding-helper">There is no wrong answer. Start with what feels most useful.</p><div className="onboarding-goals">{goalOptions.map(([value, label, description]) => <Choice key={value} name="user_primary_goal" value={value} label={label} description={description} selected={form.user_primary_goal === value} onChange={(event) => update('user_primary_goal', event.target.value)} />)}</div></fieldset>}
        {phase === 5 && <fieldset><legend>Would you like product updates?</legend><p className="onboarding-helper">A small note when something useful changes. No noisy inbox.</p><div className="onboarding-consent"><Choice name="product_updates_consent" value="yes" label="Yes, keep me posted" description="New features, practical ideas, and occasional product news." selected={form.product_updates_consent === true} onChange={() => update('product_updates_consent', true)} /><Choice name="product_updates_consent" value="no" label="No, thanks" description="I’ll discover updates when I’m in the workspace." selected={form.product_updates_consent === false} onChange={() => update('product_updates_consent', false)} /></div></fieldset>}
        {error && <p className="onboarding-error" role="alert">{error}</p>}<div className="onboarding-actions"><button type="button" className="onboarding-back" onClick={() => { setError(''); setPhase((value) => Math.max(1, value - 1)) }} disabled={phase === 1 || saving}>Back</button><span>Step {phase} of 5</span><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Saving...' : phase === 5 ? 'Enter workspace  →' : 'Continue  →'}</button></div>
      </form></section></main>
  </div>
}
