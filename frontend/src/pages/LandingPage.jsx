import { useEffect, useState } from 'react'

const features = [
  ['01', 'Bulk email campaigns', 'Send personalized emails to thousands of recipients in a few clicks.', 'arrow'],
  ['02', 'Contact management', 'Organize, segment, and manage every relationship effortlessly.', 'people'],
  ['03', 'Email templates', 'Beautiful, responsive templates to create standout emails fast.', 'paper'],
  ['04', 'Analytics and reports', 'Track opens, clicks, bounces, and more in real time.', 'chart'],
  ['05', 'Automation', 'Automate follow-ups and workflows to save time and boost engagement.', 'spark'],
  ['06', 'Security and privacy', 'Your data is encrypted and never shared. Your trust matters.', 'shield'],
]

const featureDetails = {
  'Bulk email campaigns': {
    eyebrow: 'The send desk',
    title: 'One message, thoughtfully delivered.',
    body: 'Build a campaign once, personalize every send, and keep the whole delivery moving from one calm workspace. MailForge handles the repetitive work while you stay close to the message.',
    steps: ['Write your message', 'Personalize each send', 'Deliver at the right moment'],
  },
  'Contact management': {
    eyebrow: 'The people desk',
    title: 'Every relationship, in its right place.',
    body: 'Keep contacts useful and human. Import your audience, enrich their details, and use lists and segments to make every campaign feel relevant instead of broadcast.',
    steps: ['Bring contacts together', 'Organize by intent', 'Reach the right people'],
  },
  'Email templates': {
    eyebrow: 'The template desk',
    title: 'Start with structure, then make it yours.',
    body: 'Turn a blank page into a polished email in minutes. Reusable layouts give your team a reliable starting point without flattening the personality out of the message.',
    steps: ['Choose a starting point', 'Shape the story', 'Reuse what works'],
  },
  'Analytics and reports': {
    eyebrow: 'The signal desk',
    title: 'Know what your message made possible.',
    body: 'See the story after a campaign leaves your desk. Opens, clicks, bounces, and delivery signals arrive in one readable view so your next decision is grounded in what happened.',
    steps: ['Send with confidence', 'Read the signals', 'Improve the next send'],
  },
  Automation: {
    eyebrow: 'The rhythm desk',
    title: 'Let the follow-up feel effortless.',
    body: 'Create dependable campaign rhythms without keeping every date in your head. MailForge gives follow-ups a clear place to live, so momentum continues even on your busiest days.',
    steps: ['Set the starting cue', 'Choose the next step', 'Keep momentum moving'],
  },
  'Security and privacy': {
    eyebrow: 'The trust desk',
    title: 'A careful system for important messages.',
    body: 'Your audience data and provider credentials deserve quiet protection. MailForge keeps access controlled, sensitive values out of the interface, and every campaign inside its intended workspace.',
    steps: ['Protect your workspace', 'Control access', 'Send with peace of mind'],
  },
}

function Logo({ compact = false }) {
  return <span className={`mf-logo ${compact ? 'mf-logo--compact' : ''}`}><svg viewBox="0 0 34 34" aria-hidden="true"><path d="M4.5 9.5 17 19 29.5 9.5v15H4.5z" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round"/><path d="m5 9 12 9 12-9" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"/><path d="M17 19V5" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"/><path d="m13.2 8.8 3.8-3.8 3.8 3.8" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"/></svg><span>{compact ? 'MailForge' : <><strong>MailForge</strong><small>Bulk Email for Gmail</small></>}</span></span>
}

function GoogleIcon() { return <span className="google-g" aria-hidden="true">G</span> }
function ArrowIcon() { return <svg className="arrow-icon" viewBox="0 0 18 18" aria-hidden="true"><path d="M3 9h11M9.5 3.5 15 9l-5.5 5.5" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg> }
function PlayIcon() { return <span className="play-icon" aria-hidden="true"><span /></span> }

function AbstractBackground() {
  return <div className="abstract-background" aria-hidden="true"><div className="glow glow-one" /><div className="glow glow-two" /><svg className="flow-lines" viewBox="0 0 1200 700" preserveAspectRatio="none"><path d="M-40 485C180 265 300 610 490 400s260-190 370-15 210 100 390-140"/><path d="M-80 165c220 190 360-55 540 100s330 255 790-35"/><path d="M-30 585c200-180 320-30 510-140s310-205 750-70"/><path d="M110 0c120 190 250 230 420 120s300-95 620 90"/></svg><div className="orbit orbit-one" /><div className="orbit orbit-two" /><span className="float-dot dot-one" /><span className="float-dot dot-two" /><span className="float-dot dot-three" /><span className="fragment fragment-one">~</span><span className="fragment fragment-two">/</span><span className="fragment fragment-three">+</span></div>
}

function DashboardPreview() {
  const metrics = [['Emails sent', '128,456', '+18.4%', 'up'], ['Open rate', '42.8%', '+5.2%', 'up'], ['Click rate', '11.3%', '+2.1%', 'up'], ['Bounce rate', '1.2%', '-0.4%', 'down']]
  return <div className="dashboard-wrap"><div className="dashboard-window"><div className="dashboard-top"><div className="dashboard-brand"><Logo compact /><span className="dashboard-title">Dashboard</span></div><div className="dashboard-tools"><span className="date-select">May 12 - May 18, 2024</span><span className="bell">●</span><span className="avatar">MF</span></div></div><div className="dashboard-body"><aside className="dashboard-sidebar"><p className="sidebar-label">Workspace</p>{['Compose', 'Inbox', 'Starred', 'Snoozed', 'Sent', 'Drafts'].map((item) => <span key={item} className="sidebar-item">{item}</span>)}<span className="sidebar-divider" />{['Dashboard', 'Campaigns', 'Templates', 'Contacts', 'Reports'].map((item) => <span key={item} className={`sidebar-item ${item === 'Dashboard' ? 'is-active' : ''}`}>{item}</span>)}</aside><div className="dashboard-content"><div className="dashboard-heading"><div><p className="section-kicker">Monday, May 18</p><h3>Good morning, Sofia</h3></div><button className="compose-button">+ Compose</button></div><div className="metric-grid">{metrics.map(([label, value, trend, direction]) => <div className="metric-card" key={label}><span>{label}</span><strong>{value}</strong><small className={direction}>{direction === 'up' ? '↗' : '↘'} {trend} <em>vs last week</em></small></div>)}</div><div className="dashboard-lower"><div className="performance-panel"><div className="panel-heading"><div><span>Campaign performance</span><strong>Emails sent</strong></div><span className="panel-period">Last 7 days⌄</span></div><svg className="campaign-chart" viewBox="0 0 600 190" role="img" aria-label="Campaign performance chart"><g className="chart-grid"><path d="M0 30h600M0 75h600M0 120h600M0 165h600" /></g><path className="chart-fill" d="M0 148 C45 132 55 142 96 116 S160 128 205 97 S266 112 302 78 S363 91 402 54 S465 89 506 48 S555 64 600 27 V190H0Z"/><path className="chart-line" pathLength="1" d="M0 148 C45 132 55 142 96 116 S160 128 205 97 S266 112 302 78 S363 91 402 54 S465 89 506 48 S555 64 600 27"/><circle className="chart-point" cx="506" cy="48" r="5"/><g className="chart-labels"><text x="0" y="188">May 12</text><text x="192" y="188">May 14</text><text x="390" y="188">May 16</text><text x="545" y="188">May 18</text></g></svg></div><div className="devices-panel"><span>Top devices</span><strong>45% <small>Desktop</small></strong><div className="donut-wrap"><div className="donut"><span>128k<small>delivered</small></span></div></div><div className="device-legend"><span><i className="legend-desktop" />Desktop <b>45%</b></span><span><i className="legend-mobile" />Mobile <b>40%</b></span><span><i className="legend-tablet" />Tablet <b>15%</b></span></div></div></div></div></div></div><div className="dashboard-float-note"><span className="note-check">✓</span><span><strong>Campaign delivered</strong><small>Friday digest · just now</small></span></div></div>
}

function FeatureIcon({ type }) { return <span className={`feature-icon feature-icon--${type}`} aria-hidden="true">{type === 'people' ? '••' : type === 'chart' ? '↗' : type === 'spark' ? '*' : type === 'shield' ? '✓' : type === 'paper' ? '◇' : '→'}</span> }

function FeatureBook({ isOpen }) {
  return <div className={`feature-book ${isOpen ? 'is-open' : ''}`} aria-hidden="true"><div className="feature-book-shadow" /><svg viewBox="0 0 360 190" role="presentation"><path className="book-cover" d="M180 151c-43-22-85-25-126-13V47c41-12 83-9 126 13v91Z" /><path className="book-cover book-cover-right" d="M180 151c43-22 85-25 126-13V47c-41-12-83-9-126 13v91Z" /><path className="book-page book-page-left" d="M180 141c-39-19-79-22-115-12V57c37-10 76-7 115 13v71Z" /><path className="book-page book-page-right" d="M180 141c39-19 79-22 115-12V57c-37-10-76-7-115 13v71Z" /><path className="book-seam" d="M180 70v82" /><path className="book-line" d="M88 83c25-5 51-2 73 9M88 101c25-5 51-2 73 9M199 92c22-11 48-14 73-9M199 110c22-11 48-14 73-9" /><path className="book-mail" d="m142 54 38 28 38-28v37h-76z" /><path className="book-mail-fold" d="m143 55 37 28 37-28M143 91l25-20M217 91l-25-20" /></svg><span className="feature-book-label">OPEN THE PLAYBOOK</span></div>
}

function FeatureWorkflow({ steps }) {
  return <svg className="feature-workflow" viewBox="0 0 620 180" role="img" aria-label="Three-step email workflow animation"><path className="workflow-route" d="M80 90h460" /><path className="workflow-dash" d="M80 90h460" /><g className="workflow-node workflow-node-one"><circle cx="80" cy="90" r="31" /><path d="M65 83h30v22H65zM65 83l15 12 15-12" /></g><g className="workflow-node workflow-node-two"><circle cx="310" cy="90" r="31" /><path d="M298 92h24M310 80v24M300 76h20" /></g><g className="workflow-node workflow-node-three"><circle cx="540" cy="90" r="31" /><path d="m524 90 11 11 21-24M525 72h30" /></g><circle className="workflow-pulse" cx="80" cy="90" r="5" /><text x="80" y="145" textAnchor="middle">{steps[0]}</text><text x="310" y="145" textAnchor="middle">{steps[1]}</text><text x="540" y="145" textAnchor="middle">{steps[2]}</text></svg>
}

function FeatureDialog({ feature, onClose }) {
  if (!feature) return null
  return <div className="feature-dialog-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}><section className="feature-dialog" role="dialog" aria-modal="true" aria-labelledby="feature-dialog-title"><button className="feature-dialog-close" type="button" aria-label="Close feature details" onClick={onClose}>×</button><div className="feature-dialog-top"><span className="eyebrow">{feature.eyebrow}</span><span className="feature-dialog-mark">MF / FIELD NOTE</span></div><h2 id="feature-dialog-title">{feature.title}</h2><p className="feature-dialog-body">{feature.body}</p><FeatureWorkflow steps={feature.steps} /><div className="feature-dialog-footer"><span>MAILFORGE / HOW IT WORKS</span><button className="secondary-button" type="button" onClick={onClose}>Back to the desk <ArrowIcon /></button></div></section></div>
}
const emailTemplates = [['Launch note', 'A new chapter starts here.', 'template-lavender'], ['Weekly digest', 'Small updates. Big momentum.', 'template-blue'], ['Product drop', 'Meet the thing worth opening.', 'template-sunrise'], ['Founder letter', 'A note from our desk.', 'template-ink'], ['Event invite', 'Save a seat at the table.', 'template-coral'], ['Customer story', 'Real work, thoughtfully shared.', 'template-mint'], ['Follow-up', 'Just circling back with care.', 'template-paper'], ['Seasonal send', 'A little something for today.', 'template-indigo']]
function TemplatesGallery() {
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined

    let frameId
    let lastAdvance = performance.now()
    const advance = (timestamp) => {
      if (timestamp - lastAdvance >= 4200) {
        setActiveIndex((current) => (current + 1) % emailTemplates.length)
        lastAdvance = timestamp
      }
      frameId = window.requestAnimationFrame(advance)
    }

    frameId = window.requestAnimationFrame(advance)
    return () => window.cancelAnimationFrame(frameId)
  }, [])

  const move = (direction) => {
    setActiveIndex((current) => (current + direction + emailTemplates.length) % emailTemplates.length)
  }

  return <section className="templates-section" id="templates"><div className="section-intro"><span className="eyebrow">The template desk</span><h2>Emails that feel worth opening</h2><p>Eight thoughtful starting points for every kind of conversation.</p></div><div className="templates-carousel"><button className="template-chevron template-chevron--previous" type="button" aria-label="Show previous template" onClick={() => move(-1)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7" /></svg></button><div className="templates-track">{emailTemplates.map(([title, headline, style], index) => { const offset = (index - activeIndex + emailTemplates.length) % emailTemplates.length; const normalizedOffset = offset > emailTemplates.length / 2 ? offset - emailTemplates.length : offset; return <article className={`email-template ${style} ${normalizedOffset === 0 ? 'is-active' : ''} ${Math.abs(normalizedOffset) <= 2 ? 'is-visible' : ''}`} key={title} style={{ '--template-offset': normalizedOffset }} aria-hidden={Math.abs(normalizedOffset) > 2}><div className="template-postmark">MF / {String(index + 1).padStart(2, '0')}</div><div className="template-fold" /><span className="template-type">{title}</span><h3>{headline}</h3><p>Build a clear, memorable message with MailForge.</p><div className="template-lines"><i /><i /><i /></div><footer><span>MAILFORGE</span><b>→</b></footer></article> })}</div><button className="template-chevron template-chevron--next" type="button" aria-label="Show next template" onClick={() => move(1)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg></button></div><div className="templates-dots" role="tablist" aria-label="Choose a template"><button className="template-dot" type="button" role="tab" aria-label="Show template 1" aria-selected={activeIndex === 0} onClick={() => setActiveIndex(0)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 2" aria-selected={activeIndex === 1} onClick={() => setActiveIndex(1)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 3" aria-selected={activeIndex === 2} onClick={() => setActiveIndex(2)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 4" aria-selected={activeIndex === 3} onClick={() => setActiveIndex(3)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 5" aria-selected={activeIndex === 4} onClick={() => setActiveIndex(4)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 6" aria-selected={activeIndex === 5} onClick={() => setActiveIndex(5)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 7" aria-selected={activeIndex === 6} onClick={() => setActiveIndex(6)} /><button className="template-dot" type="button" role="tab" aria-label="Show template 8" aria-selected={activeIndex === 7} onClick={() => setActiveIndex(7)} /></div></section>
}
function MailboxIllustration() { return <svg className="mailbox-svg" viewBox="0 0 360 280" role="img" aria-label="Flat illustration of a MailForge mailbox delivering a letter"><ellipse cx="180" cy="257" rx="106" ry="13" fill="#dcd9f2" opacity=".65"/><path d="M142 172h74v77h-74z" fill="#5a45d8"/><path d="M158 171h40v78h-40z" fill="#7866e8"/><path d="M79 159V91c0-38 31-69 69-69h62c38 0 69 31 69 69v68H79Z" fill="#6748e6"/><path d="M100 145V92c0-27 22-49 49-49h59c27 0 49 22 49 49v53H100Z" fill="#f0edff"/><path d="M100 145h157v16H79v-16z" fill="#5030d9" opacity=".8"/><path d="m183 117 57-45 17 20-72 57-72-57 17-20z" fill="#fff" stroke="#d9d5f4" strokeWidth="3"/><path d="m112 95 71 54 71-54" fill="none" stroke="#c5bff1" strokeWidth="3"/><path d="M266 109V61l24-12v60z" fill="#5030d9"/><path d="M290 49v-20c0-7-6-12-12-12h-21v12h21v20z" fill="#6847ff"/><path d="m181 130 16 11" stroke="#6847ff" strokeWidth="3" strokeLinecap="round"/></svg> }

const testimonials = [['Sophia Martinez', 'Growth Marketer, Acme Inc.', 'MailForge feels like an extension of Gmail. Super easy to use and the results speak for themselves.', '-2deg'], ['Daniel Kim', 'Head of Marketing, Nexora', 'Our open rates improved by 38% after switching to MailForge. The analytics are insanely helpful.', '1deg'], ['Priya Shah', 'Marketing Lead, BrightPath', 'Finally, a bulk email tool that works seamlessly inside Gmail. Saves us time every day.', '-1deg'], ['James Wilson', 'Founder, Loftly', 'The automation and templates are top-notch. MailForge is a game changer for our team.', '2deg']]
function TestimonialLetter({ item, index }) { const letter = <article className="letter" style={{ '--tilt': item[3] }}><div className="letter-top"><span>MAILFORGE</span><span>* {String(index + 1).padStart(2, '0')}</span></div><div className="letter-rule" /><p>“{item[2]}”</p><footer><span className="letter-avatar">{item[0].split(' ').map((part) => part[0]).join('')}</span><span><strong>{item[0]}</strong><small>{item[1]}</small></span><b>*****</b></footer></article>; return index === 3 ? <>{letter}<TemplatesGallery /></> : letter }

export default function LandingPage({ onNavigate }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [selectedFeature, setSelectedFeature] = useState(null)
  const [activeFeatureIndex, setActiveFeatureIndex] = useState(0)
  const navItems = ['Features', 'Templates', 'About']
  const go = (target) => { setMenuOpen(false); onNavigate(target) }
  useEffect(() => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const sections = { Templates: document.getElementById('templates') }
    const sectionLinks = [...document.querySelectorAll('a')].filter((link) => link.textContent.trim() === 'Templates')
    const scrollToSection = (event) => { 
      event.preventDefault()
      const label = event.currentTarget?.textContent.trim() || event.target.closest('a')?.textContent.trim()
      sections[label]?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' })
    }
    const handleTemplateNavigation = (event) => {
      const link = event.target.closest('a')
      if (link && sections[link.textContent.trim()]) scrollToSection(event)
    }
    document.addEventListener('click', handleTemplateNavigation)
    sectionLinks.forEach((link) => {
      link.href = '#templates'
      link.addEventListener('click', scrollToSection)
    })
    return () => {
      sectionLinks.forEach((link) => link.removeEventListener('click', scrollToSection))
      document.removeEventListener('click', handleTemplateNavigation)
    }
  }, [])
  useEffect(() => {
    if (!selectedFeature) return undefined
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setSelectedFeature(null)
    }
    document.addEventListener('keydown', closeOnEscape)
    return () => document.removeEventListener('keydown', closeOnEscape)
  }, [selectedFeature])
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined

    let frameId
    let lastAdvance = performance.now()
    const advance = (timestamp) => {
      if (timestamp - lastAdvance >= 4800) {
        setActiveFeatureIndex((current) => (current + 1) % features.length)
        lastAdvance = timestamp
      }
      frameId = window.requestAnimationFrame(advance)
    }

    frameId = window.requestAnimationFrame(advance)
    return () => window.cancelAnimationFrame(frameId)
  }, [])

  const openFeature = (title) => setSelectedFeature(featureDetails[title])
  const moveFeature = (direction) => setActiveFeatureIndex((current) => (current + direction + features.length) % features.length)

  return <div className="landing-shell premium-landing">
    <header className="site-header"><nav className="site-nav" aria-label="Main navigation"><a className="brand-link" href="#top"><Logo /></a><div className="desktop-nav">{navItems.map((item) => <a key={item} href="#features">{item}</a>)}</div><div className="nav-actions"><button className="sign-in" onClick={() => go('login')}>Sign in</button><button className="nav-cta" onClick={() => go('register')}>Get started free <ArrowIcon /></button></div><button className="menu-toggle" aria-label="Toggle navigation" aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}><span /><span /></button></nav>{menuOpen && <div className="mobile-menu">{navItems.map((item) => <a key={item} href="#features" onClick={() => setMenuOpen(false)}>{item}</a>)}<button onClick={() => go('login')}>Sign in</button><button className="nav-cta" onClick={() => go('register')}>Get started free <ArrowIcon /></button></div>}</header>
    <main id="top">
      <section className="hero-section premium-hero"><AbstractBackground /><div className="hero-copy"><div className="integration-badge"><GoogleIcon /> Built for Gmail. <strong>Powered for growth.</strong></div><h1><span>Send bulk emails</span><span className="accent-blue">from Gmail.</span><span className="accent-violet">Forge real results.</span></h1><p>MailForge helps you create, send, and track powerful email campaigns - right inside your Gmail workspace. No complicated setup. Just results.</p><div className="hero-cta"><button className="primary-button" onClick={() => go('register')}><GoogleIcon /> Connect with Google <ArrowIcon /></button><a className="secondary-button" href="#features"><PlayIcon /> Watch demo</a></div><div className="trust-row"><div><span className="trust-icon">&#10003;</span><span><strong>100% Secure</strong><small>Your data is safe and encrypted</small></span></div><div><span className="trust-icon">G</span><span><strong>Works in Gmail</strong><small>No extra tools or extensions</small></span></div><div><span className="trust-icon">&#8599;</span><span><strong>Track everything</strong><small>Opens, clicks, bounces and more</small></span></div></div></div><DashboardPreview /></section>
      <section className="features-section" id="features"><div className="section-intro"><span className="eyebrow">One calm workspace</span><h2>Everything you need to run successful email campaigns</h2><p>Powerful tools. Seamless experience. Better results.</p></div><FeatureBook isOpen={Boolean(selectedFeature)} /><div className="feature-carousel"><button className="feature-chevron feature-chevron--previous" type="button" aria-label="Show previous feature" onClick={() => moveFeature(-1)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7" /></svg></button><div className="feature-track">{features.map(([number, title, description, icon], index) => { const offset = (index - activeFeatureIndex + features.length) % features.length; const normalizedOffset = offset > features.length / 2 ? offset - features.length : offset; return <article className={`feature-card ${normalizedOffset === 0 ? 'is-active' : ''}`} key={title} style={{ '--feature-offset': normalizedOffset }} aria-hidden={normalizedOffset !== 0} role="button" tabIndex={normalizedOffset === 0 ? 0 : -1} onClick={() => { setActiveFeatureIndex(index); openFeature(title) }} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); setActiveFeatureIndex(index); openFeature(title) } }}><div className="feature-card-top"><span className="feature-number">{number}</span><FeatureIcon type={icon} /></div><h3>{title}</h3><p>{description}</p><span className="feature-card-action" aria-hidden="true"><ArrowIcon /></span></article> })}</div><button className="feature-chevron feature-chevron--next" type="button" aria-label="Show next feature" onClick={() => moveFeature(1)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg></button><div className="feature-progress" role="tablist" aria-label="Choose a feature"><span className="feature-progress-line" aria-hidden="true"><span style={{ height: `${((activeFeatureIndex + 1) / features.length) * 100}%` }} /></span>{features.map(([number, title], index) => <button className="feature-progress-step" key={title} type="button" role="tab" aria-label={`Show feature ${number}`} aria-selected={activeFeatureIndex === index} onClick={() => setActiveFeatureIndex(index)}><span>{number}</span></button>)}</div></div><FeatureDialog feature={selectedFeature} onClose={() => setSelectedFeature(null)} /></section>
      <section className="testimonials-section"><div className="testimonial-heading"><span className="eyebrow">The delivery story</span><h2>Loved by marketers.<br /><span>Delivered by MailForge.</span></h2><p>Good campaigns do more than arrive. They create a moment worth responding to.</p></div><div className="mailbox-scene"><div className="scene-envelope scene-envelope-one">[ ]</div><div className="scene-envelope scene-envelope-two">[ ]</div><MailboxIllustration /><div className="letters-grid">{testimonials.map((item, index) => <TestimonialLetter item={item} index={index} key={item[0]} />)}</div></div></section>
      <section className="final-cta"><span className="cta-paper paper-left">/</span><span className="cta-paper paper-right">*</span><div><span className="eyebrow">Make every send count</span><h2>Ready to forge better connections?</h2><p>Join businesses sending smarter emails with MailForge.</p><button className="light-button" onClick={() => go('register')}>Get started free <ArrowIcon /></button></div></section>
    </main>
    <footer className="site-footer" id="footer"><div className="footer-brand"><Logo /><p>Bulk email, without the complexity.<br />Built for the way modern teams work.</p></div><div className="footer-links"><div><strong>Product</strong><a href="#features">Features</a><a href="#features">How it works</a><a href="#features">Templates</a><a href="#features">Resources</a></div><div><strong>Company</strong><a href="#footer">About</a><a href="#footer">Contact</a><a href="#footer">Security</a><a href="#footer">Privacy</a></div></div><div className="footer-bottom"><span>Copyright 2024 MailForge</span><span>Made for thoughtful senders.</span></div></footer>
  </div>
}
