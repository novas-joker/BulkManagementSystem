import { useEffect, useState } from 'react'
import CampaignsPage from './CampaignsPage'
import ContactsPage from './ContactsPage'
import TemplatesPage from './TemplatesPage'
import ListsPage from './ListsPage'
import TagsPage from './TagsPage'
import SegmentsPage from './SegmentsPage'
import SuppressionPage from './SuppressionPage'
import { getCampaigns } from '../services/campaignApi'
import { getContacts } from '../services/contactApi'
import { getMailingLists } from '../services/listApi'

const PAGE_COMPONENTS = {
  overview: null,
  campaigns: CampaignsPage,
  contacts: ContactsPage,
  templates: TemplatesPage,
  lists: ListsPage,
  tags: TagsPage,
  segments: SegmentsPage,
  suppressions: SuppressionPage,
}

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview' },
  { id: 'campaigns', label: 'Campaigns' },
  { id: 'contacts', label: 'Contacts' },
  { id: 'templates', label: 'Templates' },
  { id: 'lists', label: 'Mailing Lists' },
  { id: 'tags', label: 'Tags' },
  { id: 'segments', label: 'Segments' },
  { id: 'suppressions', label: 'Suppressions' },
]

export default function DashboardShell({ user, onLogout }) {
  const [currentPage, setCurrentPage] = useState('overview')
  const [stats, setStats] = useState({
    totalContacts: 0,
    activeCampaigns: 0,
    totalTemplates: 0,
    mailingLists: 0,
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const [campaigns, contacts, lists] = await Promise.all([
        getCampaigns(),
        getContacts(),
        getMailingLists(),
      ])

      setStats({
        totalContacts: Array.isArray(contacts) ? contacts.length : 0,
        activeCampaigns: Array.isArray(campaigns)
          ? campaigns.filter((c) => c.status === 'sending' || c.status === 'queued').length
          : 0,
        totalTemplates: Array.isArray(campaigns) ? campaigns.length : 0,
        mailingLists: Array.isArray(lists) ? lists.length : 0,
      })
    } catch {
      console.error('Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  const PageComponent = PAGE_COMPONENTS[currentPage]

  const renderOverview = () => (
    <div className="dashboard-main">
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
          <strong>{stats.totalContacts}</strong>
        </div>
        <div className="stat-card">
          <span>Active campaigns</span>
          <strong>{stats.activeCampaigns}</strong>
        </div>
        <div className="stat-card">
          <span>Mailing lists</span>
          <strong>{stats.mailingLists}</strong>
        </div>
        <div className="stat-card">
          <span>Email templates</span>
          <strong>{stats.totalTemplates}</strong>
        </div>
      </section>

      <section className="content-grid">
        <div className="panel">
          <h3>Campaign activity</h3>
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
          <h3>Getting started</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ paddingBottom: '10px' }}>
              <button
                type="button"
                className="text-button"
                onClick={() => setCurrentPage('contacts')}
              >
                → Add your first contacts
              </button>
            </li>
            <li style={{ paddingBottom: '10px' }}>
              <button
                type="button"
                className="text-button"
                onClick={() => setCurrentPage('templates')}
              >
                → Create an email template
              </button>
            </li>
            <li style={{ paddingBottom: '10px' }}>
              <button
                type="button"
                className="text-button"
                onClick={() => setCurrentPage('campaigns')}
              >
                → Launch your first campaign
              </button>
            </li>
            <li style={{ paddingBottom: '10px' }}>
              <button
                type="button"
                className="text-button"
                onClick={() => setCurrentPage('lists')}
              >
                → Organize contacts into lists
              </button>
            </li>
          </ul>
        </div>
      </section>
    </div>
  )

  return (
    <div className="dashboard-shell">
      <aside className="sidebar">
        <div className="brand sidebar-brand">
          <span className="brand-mark">M</span>
          <span>MailForge</span>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={currentPage === item.id ? 'nav-item active' : 'nav-item'}
              onClick={() => setCurrentPage(item.id)}
            >
              {item.label}
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

        <button className="sidebar-logout" onClick={onLogout}>
          Logout
        </button>
      </aside>

      {currentPage === 'overview' ? (
        renderOverview()
      ) : PageComponent ? (
        <PageComponent />
      ) : (
        <div className="dashboard-main">
          <p>Page not found</p>
        </div>
      )}
    </div>
  )
}
