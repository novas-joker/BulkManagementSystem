import { useEffect, useState } from 'react'
import { getCampaigns, createCampaign, deleteCampaign, sendCampaign, sendCampaignTestEmail, updateCampaign } from '../services/campaignApi'
import { getTemplates } from '../services/templateApi'
import { getMailingLists } from '../services/listApi'
import { getSegments } from '../services/segmentApi'
import { confirmDialog, getApiErrorMessage, showToast } from '../services/dashboardUi'

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([])
  const [templates, setTemplates] = useState([])
  const [mailingLists, setMailingLists] = useState([])
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showBuilder, setShowBuilder] = useState(false)
  const [builderStep, setBuilderStep] = useState(1)
  const [editingId, setEditingId] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [form, setForm] = useState({
    name: '',
    subject: '',
    template_id: '',
    campaign_type: 'bulk',
    audience_criteria: { list_ids: [], segment_ids: [] },
    send_time: '',
    scheduled: false,
  })
  const [testForm, setTestForm] = useState({ recipient_email: '', campaignId: null })

  useEffect(() => {
    loadCampaigns()
    loadTemplates()
    loadMailingLists()
    loadSegments()
  }, [])

  const loadCampaigns = async () => {
    try {
      setLoading(true)
      const data = await getCampaigns()
      setCampaigns(Array.isArray(data) ? data : [])
    } catch {
      setError('Failed to load campaigns')
      setCampaigns([])
    } finally {
      setLoading(false)
    }
  }

  const loadTemplates = async () => {
    try {
      const data = await getTemplates()
      setTemplates(Array.isArray(data) ? data : [])
    } catch {
      setError('Failed to load templates')
      setTemplates([])
    }
  }

  const loadMailingLists = async () => {
    try {
      const data = await getMailingLists()
      setMailingLists(Array.isArray(data) ? data : [])
    } catch {
      console.error('Failed to load mailing lists')
      setMailingLists([])
    }
  }

  const loadSegments = async () => {
    try {
      const data = await getSegments()
      setSegments(Array.isArray(data) ? data : [])
    } catch {
      console.error('Failed to load segments')
      setSegments([])
    }
  }

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target
    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleListToggle = (listId) => {
    setForm((current) => {
      const currentList = current.audience_criteria.list_ids || []
      return {
        ...current,
        audience_criteria: {
          ...current.audience_criteria,
          list_ids: currentList.includes(listId)
            ? currentList.filter((id) => id !== listId)
            : [...currentList, listId],
        },
      }
    })
  }

  const handleSegmentToggle = (segmentId) => {
    setForm((current) => {
      const currentSegments = current.audience_criteria.segment_ids || []
      return {
        ...current,
        audience_criteria: {
          ...current.audience_criteria,
          segment_ids: currentSegments.includes(segmentId)
            ? currentSegments.filter((id) => id !== segmentId)
            : [...currentSegments, segmentId],
        },
      }
    })
  }

  const openBuilder = () => {
    setEditingId(null)
    setForm({
      name: '',
      subject: '',
      template_id: '',
      campaign_type: 'bulk',
      audience_criteria: { list_ids: [], segment_ids: [] },
      send_time: '',
      scheduled: false,
    })
    setBuilderStep(1)
    setShowBuilder(true)
  }

  const closeBuilder = () => {
    setShowBuilder(false)
    setBuilderStep(1)
    setEditingId(null)
  }

  const handleNextStep = () => {
    if (builderStep < 4) {
      setBuilderStep(builderStep + 1)
    }
  }

  const handlePrevStep = () => {
    if (builderStep > 1) {
      setBuilderStep(builderStep - 1)
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = {
        name: form.name,
        subject: form.subject,
        template_id: form.template_id || null,
        campaign_type: form.campaign_type,
        audience_criteria: form.audience_criteria || { list_ids: [], segment_ids: [] },
        scheduled_at: form.scheduled && form.send_time ? form.send_time : null,
      }

      if (editingId) {
        await updateCampaign(editingId, payload)
        setCampaigns((current) =>
          current.map((item) => (item.id === editingId ? { ...item, ...payload } : item))
        )
      } else {
        const created = await createCampaign(payload)
        setCampaigns((current) => [created, ...current])
      }

      closeBuilder()
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save campaign'))
    } finally {
      setLoading(false)
    }
  }

  const renderBuilderStep = () => {
    switch (builderStep) {
      case 1:
        return (
          <div className="builder-step">
            <h3>Step 1: Campaign Details</h3>
            <label htmlFor="campaign-name">
              <span>Campaign Name *</span>
              <input
                id="campaign-name"
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g., Summer Promotion 2024"
                autoComplete="off"
                required
              />
            </label>

            <label htmlFor="campaign-subject">
              <span>Subject Line *</span>
              <input
                id="campaign-subject"
                type="text"
                name="subject"
                value={form.subject}
                onChange={handleChange}
                placeholder="e.g., Don't miss our summer sale!"
                autoComplete="off"
                required
              />
            </label>

            <label htmlFor="campaign-type">
              <span>Campaign Type</span>
              <select id="campaign-type" name="campaign_type" value={form.campaign_type} onChange={handleChange}>
                <option value="bulk">Bulk / Marketing</option>
                <option value="transactional">Transactional</option>
              </select>
            </label>
          </div>
        )

      case 2:
        return (
          <div className="builder-step">
            <h3>Step 2: Choose Template</h3>
            <label htmlFor="campaign-template">
              <span>Email Template *</span>
              <select id="campaign-template" name="template_id" value={form.template_id} onChange={handleChange} required>
                <option value="">-- Select a template --</option>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </label>
            {templates.length === 0 && (
              <p style={{ color: '#f59e0b' }}>
                No templates available. Create one first in the Templates section.
              </p>
            )}
          </div>
        )

      case 3:
        return (
          <div className="builder-step">
            <h3>Step 3: Select Audience</h3>

            {mailingLists.length > 0 && (
              <div>
                <div style={{ display: 'block', marginBottom: '10px' }}>
                  <strong>Mailing Lists</strong>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
                  {mailingLists.map((list) => (
                    <label key={list.id} style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={(form.audience_criteria.list_ids || []).includes(list.id)}
                        onChange={() => handleListToggle(list.id)}
                      />
                      <span style={{ marginLeft: '8px' }}>{list.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {segments.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <div style={{ display: 'block', marginBottom: '10px' }}>
                  <strong>Segments</strong>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
                  {segments.map((segment) => (
                    <label key={segment.id} style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={(form.audience_criteria.segment_ids || []).includes(segment.id)}
                        onChange={() => handleSegmentToggle(segment.id)}
                      />
                      <span style={{ marginLeft: '8px' }}>{segment.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {mailingLists.length === 0 && segments.length === 0 && (
              <p style={{ color: '#f59e0b' }}>
                No audience available. Create mailing lists or segments first.
              </p>
            )}
          </div>
        )

      case 4:
        return (
          <div className="builder-step">
            <h3>Step 4: Schedule (Optional)</h3>

            <label htmlFor="campaign-scheduled">
              <input
                id="campaign-scheduled"
                type="checkbox"
                name="scheduled"
                checked={form.scheduled}
                onChange={handleChange}
              />
              <span>Schedule this campaign for later</span>
            </label>

            {form.scheduled && (
              <label htmlFor="campaign-send-time" style={{ marginTop: '15px' }}>
                <span>Send Date & Time</span>
                <input
                  id="campaign-send-time"
                  type="datetime-local"
                  name="send_time"
                  value={form.send_time}
                  onChange={handleChange}
                  required={form.scheduled}
                />
              </label>
            )}

            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f3f4f6', borderRadius: '8px' }}>
              <h4>Campaign Summary</h4>
              <p><strong>Name:</strong> {form.name}</p>
              <p><strong>Subject:</strong> {form.subject}</p>
              <p><strong>Type:</strong> {form.campaign_type}</p>
              <p><strong>Template:</strong> {templates.find((t) => t.id === form.template_id)?.name || 'Not selected'}</p>
              <p>
                <strong>Lists:</strong> {form.audience_criteria.list_ids?.length || 0} selected
              </p>
              <p>
                <strong>Segments:</strong> {form.audience_criteria.segment_ids?.length || 0} selected
              </p>
              {form.scheduled && <p><strong>Scheduled for:</strong> {form.send_time}</p>}
            </div>
          </div>
        )

      default:
        return null
    }
  }


  const handleDelete = async (campaignId) => {
    if (!await confirmDialog({ title: 'Delete campaign?', message: 'This campaign will be removed from your workspace.', confirmLabel: 'Delete campaign' })) return

    try {
      await deleteCampaign(campaignId)
      setCampaigns((current) => current.filter((item) => item.id !== campaignId))
      showToast('Campaign deleted.')
    } catch {
      setError('Failed to delete campaign')
    }
  }

  const handleTestEmail = async () => {
    if (!testForm.campaignId || !testForm.recipient_email) {
      setError('Select a campaign and enter a recipient email')
      return
    }

    try {
      setLoading(true)
      const response = await sendCampaignTestEmail(testForm.campaignId, testForm.recipient_email)
      showToast(response?.message || 'Test email sent successfully.')
      setTestForm({ recipient_email: '', campaignId: null })
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to send test email'))
    } finally {
      setLoading(false)
    }
  }

  const handleSendCampaign = async (campaignId) => {
    if (!await confirmDialog({ title: 'Send campaign now?', message: 'MailForge will send this campaign to every eligible contact.', confirmLabel: 'Send campaign', tone: 'primary' })) return

    try {
      setLoading(true)
      setError('')
      const result = await sendCampaign(campaignId)
      await loadCampaigns()
      showToast(`Campaign sent. Sent: ${result.sent}, Failed: ${result.failed}.`)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to send campaign'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Campaigns</h2>
        <button className="primary-button" onClick={openBuilder}>
          New Campaign
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showBuilder && (
        <div className="form-card">
          <div className="builder-header">
            <h2>Campaign Builder</h2>
            <div className="builder-steps">
              {[1, 2, 3, 4].map((step) => (
                <div
                  key={step}
                  className={`step-indicator ${step === builderStep ? 'active' : ''} ${
                    step < builderStep ? 'completed' : ''
                  }`}
                  onClick={() => setBuilderStep(step)}
                >
                  {step}
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {renderBuilderStep()}

            <div className="builder-actions" style={{ marginTop: '30px', display: 'flex', gap: '10px' }}>
              {builderStep > 1 && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handlePrevStep}
                  disabled={loading}
                >
                  ← Previous
                </button>
              )}

              {builderStep < 4 && (
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleNextStep}
                  disabled={loading}
                >
                  Next →
                </button>
              )}

              {builderStep === 4 && (
                <button type="submit" className="primary-button" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Campaign'}
                </button>
              )}

              <button type="button" className="secondary-button" onClick={closeBuilder}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="list-grid">
        {campaigns.length === 0 ? (
          <div className="empty-state">No campaigns yet. Click "New Campaign" to get started.</div>
        ) : (
          campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="panel"
              style={{ cursor: 'pointer' }}
              onClick={() => setExpandedId(expandedId === campaign.id ? null : campaign.id)}
            >
              <div className="list-header">
                <div>
                  <h3>{campaign.name}</h3>
                  <small>Status: {campaign.status || 'Draft'}</small>
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <button
                    className="secondary-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      setExpandedId(expandedId === campaign.id ? null : campaign.id)
                    }}
                  >
                    {expandedId === campaign.id ? '▼' : '▶'}
                  </button>
                  <button
                    className="danger-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(campaign.id)
                    }}
                  >
                    Delete
                  </button>
                  {(campaign.status === 'draft' || campaign.status === 'scheduled') && (
                    <button
                      className="primary-button"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleSendCampaign(campaign.id)
                      }}
                      disabled={loading}
                    >
                      Send Campaign
                    </button>
                  )}
                </div>
              </div>

              {expandedId === campaign.id && (
                <div style={{ marginTop: '15px' }}>
                  <p>
                    <strong>Subject:</strong> {campaign.subject}
                  </p>
                  <p>
                    <strong>Template:</strong> {campaign.template_id || 'Not assigned'}
                  </p>
                  <p>
                    <strong>Type:</strong> {campaign.campaign_type}
                  </p>

                  <div style={{ marginTop: '15px' }}>
                    <label htmlFor={`test-email-${campaign.id}`} style={{ display: 'flex', gap: '8px' }}>
                      <input
                        id={`test-email-${campaign.id}`}
                        type="email"
                        value={testForm.campaignId === campaign.id ? testForm.recipient_email : ''}
                        onChange={(event) =>
                          setTestForm({
                            campaignId: campaign.id,
                            recipient_email: event.target.value,
                          })
                        }
                        onClick={(e) => e.stopPropagation()}
                        placeholder="Test email address"
                        autoComplete="email"
                        style={{ flex: 1 }}
                      />
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleTestEmail()
                        }}
                        disabled={loading}
                      >
                        Send Test
                      </button>
                    </label>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

