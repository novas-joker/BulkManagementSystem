export default function LandingPage({ onNavigate }) {
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
