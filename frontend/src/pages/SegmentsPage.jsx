import { useEffect, useState } from 'react'
import { createSegment, deleteSegment, getSegments, previewSegment, updateSegment } from '../services/segmentApi'

export default function SegmentsPage() {
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [previewingId, setPreviewingId] = useState(null)
  const [previewData, setPreviewData] = useState(null)
  const [form, setForm] = useState({
    name: '',
    description: '',
    filter_criteria: '{}',
    is_active: true,
  })

  useEffect(() => {
    loadSegments()
  }, [])

  const loadSegments = async () => {
    try {
      setLoading(true)
      const data = await getSegments()
      setSegments(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load segments')
      setSegments([])
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

  const handleToggle = () => {
    setForm((current) => ({
      ...current,
      is_active: !current.is_active,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = {
        name: form.name,
        description: form.description,
        filter_criteria: form.filter_criteria ? JSON.parse(form.filter_criteria) : {},
        is_active: form.is_active,
      }

      if (editingId) {
        await updateSegment(editingId, payload)
        setSegments((current) =>
          current.map((item) => (item.id === editingId ? { ...item, ...payload } : item))
        )
      } else {
        const created = await createSegment(payload)
        setSegments((current) => [created, ...current])
      }
      setForm({
        name: '',
        description: '',
        filter_criteria: '{}',
        is_active: true,
      })
      setShowForm(false)
      setEditingId(null)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to save segment')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (segment) => {
    setForm({
      name: segment.name,
      description: segment.description,
      filter_criteria: JSON.stringify(segment.filter_criteria || {}),
      is_active: segment.is_active,
    })
    setEditingId(segment.id)
    setShowForm(true)
  }

  const handlePreview = async (segmentId) => {
    try {
      setLoading(true)
      const data = await previewSegment(segmentId)
      setPreviewData(data)
      setPreviewingId(segmentId)
    } catch {
      setError('Failed to preview segment')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (segmentId) => {
    if (!window.confirm('Are you sure you want to delete this segment?')) return

    try {
      await deleteSegment(segmentId)
      setSegments((current) => current.filter((item) => item.id !== segmentId))
    } catch {
      setError('Failed to delete segment')
    }
  }

  const handleCancel = () => {
    setForm({
      name: '',
      description: '',
      filter_criteria: '{}',
      is_active: true,
    })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Segments</h2>
        <button className="primary-button" onClick={() => setShowForm(true)}>
          New Segment
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <label>
              <span>Segment Name</span>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g., Active Users"
                required
              />
            </label>

            <label>
              <span>Description</span>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                placeholder="Optional description"
                rows="2"
              />
            </label>

            <label>
              <span>Filter Criteria (JSON)</span>
              <textarea
                name="filter_criteria"
                value={form.filter_criteria}
                onChange={handleChange}
                placeholder='{"status": "subscribed"}'
                rows="4"
              />
            </label>

            <label>
              <input
                type="checkbox"
                name="is_active"
                checked={form.is_active}
                onChange={handleToggle}
              />
              <span>Active</span>
            </label>

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
          <h3>Segment Preview: {previewData.segment_name}</h3>
          <p>Total contacts: {previewData.total_contacts}</p>
          {previewData.contacts && previewData.contacts.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.contacts.map((contact) => (
                    <tr key={contact.id}>
                      <td>{contact.email}</td>
                      <td>{contact.first_name} {contact.last_name}</td>
                      <td>{contact.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="empty-state">No contacts match this segment.</p>
          )}
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

      {loading && !showForm && !previewingId ? (
        <p>Loading segments...</p>
      ) : segments.length === 0 ? (
        <p className="empty-state">No segments yet. Create one to target specific audiences.</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Contacts</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {segments.map((segment) => (
                <tr key={segment.id}>
                  <td>
                    <strong>{segment.name}</strong>
                  </td>
                  <td>{segment.description || '-'}</td>
                  <td>{segment.contact_count || 0}</td>
                  <td>{segment.is_active ? 'Active' : 'Inactive'}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handlePreview(segment.id)}
                    >
                      Preview
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleEdit(segment)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDelete(segment.id)}
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
