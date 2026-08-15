import { useEffect, useState } from 'react'
import {
  bulkCreateSuppressions,
  createSuppression,
  deleteSuppression,
  getSuppressions,
} from '../services/suppressionApi'

export default function SuppressionPage() {
  const [suppressions, setSuppressions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [isBulk, setIsBulk] = useState(false)
  const [form, setForm] = useState({
    email: '',
    emails: '',
    reason: '',
    source: 'manual',
  })

  useEffect(() => {
    loadSuppressions()
  }, [])

  const loadSuppressions = async () => {
    try {
      setLoading(true)
      const data = await getSuppressions()
      setSuppressions(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load suppressions')
      setSuppressions([])
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

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (isBulk) {
        const emails = form.emails
          .split('\n')
          .map((email) => email.trim())
          .filter((email) => email.length > 0)

        if (emails.length === 0) {
          setError('Please enter at least one email address')
          setLoading(false)
          return
        }

        await bulkCreateSuppressions(emails, form.reason, form.source)
        await loadSuppressions()
      } else {
        await createSuppression({
          email: form.email,
          reason: form.reason,
          source: form.source,
        })
        await loadSuppressions()
      }

      setForm({ email: '', emails: '', reason: '', source: 'manual' })
      setShowForm(false)
      setIsBulk(false)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to add suppression')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (suppressionId) => {
    if (!window.confirm('Are you sure you want to remove this suppression?')) return

    try {
      await deleteSuppression(suppressionId)
      setSuppressions((current) => current.filter((item) => item.id !== suppressionId))
    } catch {
      setError('Failed to delete suppression')
    }
  }

  const handleCancel = () => {
    setForm({ email: '', emails: '', reason: '', source: 'manual' })
    setShowForm(false)
    setIsBulk(false)
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Email Suppressions</h2>
        <button className="primary-button" onClick={() => setShowForm(true)}>
          Add to Blocklist
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="form-card">
          <div style={{ marginBottom: '20px' }}>
            <label>
              <input
                type="checkbox"
                checked={isBulk}
                onChange={(e) => setIsBulk(e.target.checked)}
              />
              <span>Bulk Import (Multiple emails)</span>
            </label>
          </div>

          <form onSubmit={handleSubmit}>
            {isBulk ? (
              <label>
                <span>Email Addresses (one per line)</span>
                <textarea
                  name="emails"
                  value={form.emails}
                  onChange={handleChange}
                  placeholder="user1@example.com&#10;user2@example.com&#10;user3@example.com"
                  rows="6"
                  required
                />
              </label>
            ) : (
              <label>
                <span>Email Address</span>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="user@example.com"
                  required
                />
              </label>
            )}

            <label>
              <span>Reason</span>
              <textarea
                name="reason"
                value={form.reason}
                onChange={handleChange}
                placeholder="e.g., Bounced email, Unsubscribe request"
                rows="2"
              />
            </label>

            <label>
              <span>Source</span>
              <select name="source" value={form.source} onChange={handleChange}>
                <option value="manual">Manual</option>
                <option value="bounce">Bounce</option>
                <option value="complaint">Complaint</option>
                <option value="unsubscribe">Unsubscribe</option>
              </select>
            </label>

            <div className="form-actions">
              <button type="submit" className="primary-button" disabled={loading}>
                {loading ? 'Adding...' : 'Add to Blocklist'}
              </button>
              <button type="button" className="secondary-button" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {loading && !showForm ? (
        <p>Loading suppressions...</p>
      ) : suppressions.length === 0 ? (
        <p className="empty-state">No suppressed emails. Good to go!</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Reason</th>
                <th>Source</th>
                <th>Date Added</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {suppressions.map((suppression) => (
                <tr key={suppression.id}>
                  <td>{suppression.email}</td>
                  <td>{suppression.reason || '-'}</td>
                  <td>{suppression.source}</td>
                  <td>{new Date(suppression.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDelete(suppression.id)}
                    >
                      Remove
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
