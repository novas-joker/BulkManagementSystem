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
import { getTemplates } from '../services/templateApi'
import { subscribeDashboardUi } from '../services/dashboardUi'
import { ArrowUpRight, BarChart3, Check, CircleHelp, FileText, List, LogOut, Megaphone, Plus, Send, ShieldBan, Sparkles, Tags, Users } from 'lucide-react'

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
  { id: 'overview', label: 'Overview', icon: BarChart3 },
  { id: 'campaigns', label: 'Campaigns', icon: Megaphone },
  { id: 'contacts', label: 'Contacts', icon: Users },
  { id: 'templates', label: 'Templates', icon: FileText },
  { id: 'lists', label: 'Mailing Lists', icon: List },
  { id: 'tags', label: 'Tags', icon: Tags },
  { id: 'segments', label: 'Segments', icon: Users },
  { id: 'suppressions', label: 'Suppressions', icon: ShieldBan },
]

function getDateKey(date) {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}

function buildSmoothPath(points) {
  if (!points.length) return ''

  return points.reduce((path, point, index) => {
    if (index === 0) return `M ${point.x} ${point.y}`

    const previous = points[index - 1]
    const midpoint = (previous.x + point.x) / 2
    return `${path} C ${midpoint} ${previous.y}, ${midpoint} ${point.y}, ${point.x} ${point.y}`
  }, '')
}

export default function DashboardShell({ user, onLogout }) {
  const [currentPage, setCurrentPage] = useState('overview')
  const [stats, setStats] = useState({
    totalContacts: 0,
    activeCampaigns: 0,
    totalTemplates: 0,
    mailingLists: 0,
    campaigns: [],
  })
  const [loading, setLoading] = useState(false)
  const [uiDialog, setUiDialog] = useState(null)

  useEffect(() => subscribeDashboardUi((event) => {
    setUiDialog(event)
  }), [])

  const closeDialog = (value) => {
    uiDialog?.resolve(value)
    setUiDialog(null)
  }

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const [campaigns, contacts, lists, templates] = await Promise.all([
        getCampaigns(),
        getContacts(),
        getMailingLists(),
        getTemplates(),
      ])

      setStats({
        totalContacts: Array.isArray(contacts) ? contacts.length : 0,
        activeCampaigns: Array.isArray(campaigns)
          ? campaigns.filter((c) => c.status === 'sending' || c.status === 'queued').length
          : 0,
        totalTemplates: Array.isArray(templates) ? templates.length : 0,
        mailingLists: Array.isArray(lists) ? lists.length : 0,
        campaigns: Array.isArray(campaigns) ? campaigns : [],
      })
    } catch {
      console.error('Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  const PageComponent = PAGE_COMPONENTS[currentPage]
  const currentNavItem = NAV_ITEMS.find((item) => item.id === currentPage)

  const renderOverview = () => {
    const today = new Date()
    const chartDays = Array.from({ length: 7 }, (_, index) => {
      const date = new Date(today)
      date.setHours(0, 0, 0, 0)
      date.setDate(today.getDate() - (6 - index))
      return date
    })
    const campaignCounts = chartDays.map((day) => stats.campaigns.filter((campaign) => {
      const createdAt = campaign.created_at ? new Date(campaign.created_at) : null
      return createdAt && !Number.isNaN(createdAt.getTime()) && getDateKey(createdAt) === getDateKey(day)
    }).length)
    const chartMax = Math.max(4, Math.ceil(Math.max(...campaignCounts, 0) / 4) * 4)
    const chartPoints = campaignCounts.map((count, index) => ({
      x: index * (700 / (campaignCounts.length - 1)),
      y: 168 - (count / chartMax) * 150,
    }))
    const chartLinePath = buildSmoothPath(chartPoints)
    const chartAreaPath = `${chartLinePath} V 168 H 0 Z`
    const chartGridPath = [0, 1, 2, 3, 4].map((line) => `M0 ${line * 42}H700`).join('')
      + chartPoints.map((point) => `M${point.x} 0V168`).join('')

    return <div className="dashboard-main">
      <header className="dashboard-header">
        <div>
          <span className="eyebrow">Your workspace</span>
          <h1>Good morning, {user?.full_name?.split(' ')[0] || 'there'}.</h1>
          <p className="dashboard-subtitle">Here is the latest from your audience and campaigns.</p>
        </div>
        <button className="primary-button overview-action" onClick={() => setCurrentPage('campaigns')}>
          <Plus size={17} aria-hidden="true" /> Create campaign
        </button>
      </header>

      <section className="stats-row">
        <div className="stat-card stat-card--contacts">
          <span className="stat-card-icon" aria-hidden="true"><Users size={20} /></span>
          <span>Total contacts</span>
          <strong>{stats.totalContacts}</strong>
          <small>Across your audience</small>
        </div>
        <div className="stat-card stat-card--campaigns">
          <span className="stat-card-icon" aria-hidden="true"><Send size={20} /></span>
          <span>Active campaigns</span>
          <strong>{stats.activeCampaigns}</strong>
          <small>Sending or queued</small>
        </div>
        <div className="stat-card stat-card--lists">
          <span className="stat-card-icon" aria-hidden="true"><List size={20} /></span>
          <span>Mailing lists</span>
          <strong>{stats.mailingLists}</strong>
          <small>Ready to organize</small>
        </div>
        <div className="stat-card stat-card--templates">
          <span className="stat-card-icon" aria-hidden="true"><FileText size={20} /></span>
          <span>Email templates</span>
          <strong>{stats.totalTemplates}</strong>
          <small>Reusable designs</small>
        </div>
      </section>

      <section className="overview-grid">
        <div className="panel activity-panel">
          <div className="panel-heading-row">
            <div><span className="panel-kicker">Performance</span><h3>Campaign activity</h3></div>
            <span className="panel-period">Last 7 days</span>
          </div>
          <div className="activity-summary"><strong>{stats.campaigns.length}</strong><span>campaigns created</span><span className="activity-trend">↑ Getting started</span></div>
          <div className="chart-area" aria-label="Campaign activity over the last seven days">
            <span className="chart-axis-title chart-axis-title--y">Campaigns</span>
            <div className="chart-y-axis"><span>{chartMax}</span><span>{Math.round(chartMax * .75)}</span><span>{Math.round(chartMax * .5)}</span><span>{Math.round(chartMax * .25)}</span><span>0</span></div>
            <div className="chart-plot">
              <svg className="activity-chart" viewBox="0 0 700 190" role="img" aria-label="Smooth campaign activity trend from Monday to Sunday" preserveAspectRatio="none">
                <defs><linearGradient id="activity-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#57b7a6" stopOpacity=".34" /><stop offset="100%" stopColor="#57b7a6" stopOpacity=".04" /></linearGradient></defs>
                <path className="activity-chart-grid" d={chartGridPath} />
                <path className="activity-chart-area" d={chartAreaPath} />
                <path className="activity-chart-line" d={chartLinePath} />
                {chartPoints.map((point) => <circle key={`${point.x}-${point.y}`} cx={point.x} cy={point.y} r="4" />)}
              </svg>
              <div className="chart-labels">{chartDays.map((day) => <span key={getDateKey(day)}>{day.toLocaleDateString('en-US', { weekday: 'short' })}</span>)}</div>
              <span className="chart-axis-title chart-axis-title--x">Days</span>
            </div>
          </div>
        </div>

        <div className="panel setup-panel">
          <div className="panel-heading-row"><div><span className="panel-kicker">Next steps</span><h3>Make your first send</h3></div><span className="setup-count">1 / 4</span></div>
          <p className="setup-copy">Build a small foundation for your first campaign.</p>
          <div className="setup-progress"><span /></div>
          <div className="setup-list">
            <button type="button" className="setup-item is-done" onClick={() => setCurrentPage('contacts')}><span><Check size={16} /></span><strong>Add contacts</strong><small>{stats.totalContacts ? 'Audience added' : 'Bring in your audience'}</small></button>
            <button type="button" className="setup-item" onClick={() => setCurrentPage('templates')}><span>2</span><strong>Create a template</strong><small>Give your message a home</small></button>
            <button type="button" className="setup-item" onClick={() => setCurrentPage('lists')}><span>3</span><strong>Organize a list</strong><small>Keep your audience focused</small></button>
          </div>
        </div>
      </section>

      <section className="panel recent-panel">
        <div className="panel-heading-row"><div><span className="panel-kicker">Your work</span><h3>Recent campaigns</h3></div><button type="button" className="text-button" onClick={() => setCurrentPage('campaigns')}>View all <ArrowUpRight size={16} aria-hidden="true" /></button></div>
        {stats.campaigns.length ? <div className="campaign-list">{stats.campaigns.slice(0, 4).map((campaign) => <button type="button" className="campaign-row" key={campaign.id} onClick={() => setCurrentPage('campaigns')}><span className="campaign-row-mark" aria-hidden="true"><Sparkles size={16} /></span><span className="campaign-row-name"><strong>{campaign.name}</strong><small>{campaign.subject || 'No subject'}</small></span><span className={`campaign-status campaign-status--${campaign.status}`}>{campaign.status}</span><span className="campaign-row-arrow" aria-hidden="true"><ArrowUpRight size={16} /></span></button>)}</div> : <div className="empty-campaigns"><span aria-hidden="true"><Sparkles size={18} /></span><div><strong>Your campaign desk is waiting.</strong><p>Create a campaign when you are ready to send your first message.</p></div><button type="button" className="secondary-button" onClick={() => setCurrentPage('campaigns')}>Create campaign</button></div>}
      </section>
    </div>
  }

  return (
    <div className="dashboard-shell">
      {uiDialog && <div className="ui-dialog-backdrop" role="presentation"><div className="ui-dialog" role="dialog" aria-modal="true" aria-labelledby="ui-dialog-title"><div className="ui-dialog-mark">{uiDialog.type === 'prompt' ? <FileText size={20} /> : <CircleHelp size={20} />}</div><h2 id="ui-dialog-title">{uiDialog.title}</h2><p>{uiDialog.message}</p>{uiDialog.type === 'prompt' && <input className="ui-dialog-input" autoFocus defaultValue={uiDialog.defaultValue} id="ui-dialog-input" /> }<div className="ui-dialog-actions"><button type="button" className="secondary-button" onClick={() => closeDialog(uiDialog.type === 'prompt' ? null : false)}>Cancel</button><button type="button" className={`primary-button ${uiDialog.tone === 'danger' ? 'danger-button' : ''}`} onClick={() => closeDialog(uiDialog.type === 'prompt' ? document.getElementById('ui-dialog-input')?.value || null : true)}>{uiDialog.confirmLabel}</button></div></div></div>}
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
              title={item.label}
              aria-label={item.label}
            >
              <item.icon size={19} strokeWidth={1.7} aria-hidden="true" />
              <span>{item.label}</span>
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
          <LogOut size={18} strokeWidth={1.7} aria-hidden="true" />
          <span>Logout</span>
        </button>
      </aside>

      <div className="workspace-canvas">
        <header className="workspace-topbar">
          <div className="workspace-context"><span className="workspace-context-mark"><Sparkles size={16} aria-hidden="true" /></span><div><span>MailForge workspace</span><strong>{currentNavItem?.label || 'Overview'}</strong></div></div>
          <div className="workspace-actions"><span className="workspace-status"><i /> All systems ready</span><span className="workspace-date">Tuesday, 19 August 2026</span><div className="workspace-user"><span className="avatar">{user?.full_name?.charAt(0) || 'U'}</span><span>{user?.full_name?.split(' ')[0] || 'User'}</span></div></div>
        </header>
        <nav className="workspace-breadcrumbs" aria-label="Breadcrumb"><button type="button" onClick={() => setCurrentPage('overview')}>Workspace</button><span>/</span><strong>{currentNavItem?.label || 'Overview'}</strong></nav>
        {currentPage === 'overview' ? (
          renderOverview()
        ) : PageComponent ? (
          <PageComponent />
        ) : (
          <div className="dashboard-main"><p>Page not found</p></div>
        )}
      </div>
    </div>
  )
}
