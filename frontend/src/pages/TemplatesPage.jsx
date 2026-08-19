import { useEffect, useState } from 'react'
import {
  createTemplate,
  deleteTemplate,
  duplicateTemplate,
  getTemplates,
  previewTemplate,
  sendTestEmail,
  updateTemplate,
} from '../services/templateApi'

export default function TemplatesPage() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [previewingId, setPreviewingId] = useState(null)
  const [previewData, setPreviewData] = useState(null)
  const [testEmailModal, setTestEmailModal] = useState({ visible: false, templateId: null })
  const [testForm, setTestForm] = useState({ recipient_email: '' })
  const [expandedId, setExpandedId] = useState(null)
  const [form, setForm] = useState({
    name: '',
    subject: '',
    html_content: '<p>Hello {{first_name}},</p>',
    plain_text_content: 'Hello {{first_name}}',
    preview_text: '',
    template_type: 'standard',
  })
  
  const TEMPLATE_VARIABLES = [
    { name: 'first_name', example: 'John' },
    { name: 'last_name', example: 'Doe' },
    { name: 'email', example: 'john@example.com' },
  ]
  
  const insertVariable = (varName) => {
    const textarea = document.querySelector('textarea[name="html_content"]')
    if (textarea) {
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const before = form.html_content.substring(0, start)
      const after = form.html_content.substring(end)
      const varPlaceholder = `{{${varName}}}`
      setForm((current) => ({
        ...current,
        html_content: before + varPlaceholder + after,
      }))
    }
  }

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      setLoading(true)
      const data = await getTemplates()
      setTemplates(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load templates')
      setTemplates([])
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }))
  }

  const handleTestEmailChange = (event) => {
    setTestForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = {
        name: form.name,
        subject: form.subject,
        html_content: form.html_content,
        plain_text_content: form.plain_text_content,
        preview_text: form.preview_text,
        template_type: form.template_type,
        template_variables: ['first_name', 'email', 'last_name'],
      }

      if (editingId) {
        await updateTemplate(editingId, payload)
        setTemplates((current) =>
          current.map((item) => (item.id === editingId ? { ...item, ...payload } : item))
        )
      } else {
        const created = await createTemplate(payload)
        setTemplates((current) => [created, ...current])
      }
      setForm({
        name: '',
        subject: '',
        html_content: '<p>Hello {{first_name}},</p>',
        plain_text_content: 'Hello {{first_name}}',
        preview_text: '',
        template_type: 'standard',
      })
      setShowForm(false)
      setEditingId(null)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to save template')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (template) => {
    setForm({
      name: template.name,
      subject: template.subject,
      html_content: template.html_content,
      plain_text_content: template.plain_text_content,
      preview_text: template.preview_text,
      template_type: template.template_type,
    })
    setEditingId(template.id)
    setShowForm(true)
  }

  const handlePreview = async (templateId) => {
    try {
      setLoading(true)
      const data = await previewTemplate(templateId)
      setPreviewData(data)
      setPreviewingId(templateId)
    } catch {
      setError('Failed to preview template')
    } finally {
      setLoading(false)
    }
  }

  const handleTestEmail = async () => {
    if (!testForm.recipient_email) {
      setError('Please enter a recipient email')
      return
    }

    try {
      setLoading(true)
      await sendTestEmail(testEmailModal.templateId, testForm.recipient_email)
      alert('Test email sent! Check your inbox.')
      setTestEmailModal({ visible: false, templateId: null })
      setTestForm({ recipient_email: '' })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send test email')
    } finally {
      setLoading(false)
    }
  }

  const handleDuplicate = async (template) => {
    const newName = window.prompt('Enter name for duplicated template:', `${template.name} (Copy)`)
    if (!newName) return

    try {
      setLoading(true)
      const duplicated = await duplicateTemplate(template.id, newName)
      setTemplates((current) => [duplicated, ...current])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to duplicate template')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) return

    try {
      await deleteTemplate(templateId)
      setTemplates((current) => current.filter((item) => item.id !== templateId))
    } catch {
      setError('Failed to delete template')
    }
  }

  const handleCancel = () => {
    setForm({
      name: '',
      subject: '',
      html_content: '<p>Hello {{first_name}},</p>',
      plain_text_content: 'Hello {{first_name}}',
      preview_text: '',
      template_type: 'standard',
    })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Email Templates</h2>
        <button className="primary-button" onClick={() => setShowForm(true)}>
          New Template
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <label>
              <span>Template Name</span>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g., Welcome Email"
                required
              />
            </label>

            <label>
              <span>Subject Line</span>
              <input
                type="text"
                name="subject"
                value={form.subject}
                onChange={handleChange}
                placeholder="Welcome to {{company_name}}"
                required
              />
            </label>

            <label>
              <span>Preview Text</span>
              <input
                type="text"
                name="preview_text"
                value={form.preview_text}
                onChange={handleChange}
                placeholder="Shown in email preview"
              />
            </label>

            <div style={{ marginTop: '20px', marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '10px' }}>
                <strong>Quick Insert Variables</strong>
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {TEMPLATE_VARIABLES.map((variable) => (
                  <button
                    key={variable.name}
                    type="button"
                    className="secondary-button"
                    onClick={() => insertVariable(variable.name)}
                    style={{ padding: '0.5rem 0.8rem', fontSize: '0.85rem' }}
                  >
                    +{'{{'} {variable.name} {'}}'}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div>
                <label>
                  <span>HTML Content</span>
                  <textarea
                    name="html_content"
                    value={form.html_content}
                    onChange={handleChange}
                    placeholder="<p>Hello {{first_name}},</p><p>Welcome!</p>"
                    rows="12"
                    required
                  />
                </label>
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  <span>Live Preview</span>
                </label>
                <div
                  style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.5rem',
                    padding: '1rem',
                    backgroundColor: '#f8fafc',
                    minHeight: '300px',
                    overflow: 'auto',
                  }}
                  dangerouslySetInnerHTML={{ __html: form.html_content || '<p>Preview will appear here...</p>' }}
                />
              </div>
            </div>

            <label>
              <span>Plain Text Content</span>
              <textarea
                name="plain_text_content"
                value={form.plain_text_content}
                onChange={handleChange}
                placeholder="Hello {{first_name}}, welcome!"
                rows="4"
                required
              />
            </label>

            <label>
              <span>Template Type</span>
              <select name="template_type" value={form.template_type} onChange={handleChange}>
                <option value="standard">Standard</option>
                <option value="promotional">Promotional</option>
                <option value="transactional">Transactional</option>
                <option value="newsletter">Newsletter</option>
              </select>
            </label>

            <div className="info-box">
              <p>
                <strong>Available variables:</strong> {TEMPLATE_VARIABLES.map((v) => `{{${v.name}}} (e.g., ${v.example})`).join(', ')}
              </p>
            </div>

            <div className="form-actions">
              <button type="submit" className="primary-button" disabled={loading}>
                {loading ? 'Saving...' : editingId ? 'Update' : 'Create'}
              </button>
              <button type="button" className="secondary-button" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {previewingId && previewData && (
        <div className="form-card">
          <h3>Template Preview: {previewData.template_name}</h3>
          <div className="preview-container">
            <h4>Subject: {previewData.rendered_subject}</h4>
            <div className="preview-html" dangerouslySetInnerHTML={{ __html: previewData.rendered_html }} />
          </div>
          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setPreviewingId(null)
              setPreviewData(null)
            }}
          >
            Close Preview
          </button>
        </div>
      )}

      {testEmailModal.visible && (
        <div className="form-card">
          <h3>Send Test Email</h3>
          <label>
            <span>Recipient Email</span>
            <input
              type="email"
              name="recipient_email"
              value={testForm.recipient_email}
              onChange={handleTestEmailChange}
              placeholder="your@example.com"
              required
            />
          </label>
          <div className="form-actions">
            <button type="button" className="primary-button" onClick={handleTestEmail} disabled={loading}>
              {loading ? 'Sending...' : 'Send Test Email'}
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setTestEmailModal({ visible: false, templateId: null })
                setTestForm({ recipient_email: '' })
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {loading && !showForm && !previewingId && !testEmailModal.visible ? (
        <p>Loading templates...</p>
      ) : templates.length === 0 ? (
        <p className="empty-state">No templates yet. Create one to get started.</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Subject</th>
                <th>Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {templates.map((template) => (
                <tr key={template.id}>
                  <td>
                    <strong>{template.name}</strong>
                  </td>
                  <td>{template.subject}</td>
                  <td>{template.template_type}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handlePreview(template.id)}
                    >
                      Preview
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDuplicate(template)}
                    >
                      Duplicate
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => {
                        setTestEmailModal({ visible: true, templateId: template.id })
                        setTestForm({ recipient_email: '' })
                      }}
                    >
                      Test Email
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleEdit(template)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDelete(template.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
