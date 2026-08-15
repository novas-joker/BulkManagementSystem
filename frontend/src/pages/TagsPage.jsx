import { useEffect, useState } from 'react'
import { createTag, deleteTag, getTags, updateTag } from '../services/tagApi'

export default function TagsPage() {
  const [tags, setTags] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({
    name: '',
    description: '',
  })

  useEffect(() => {
    loadTags()
  }, [])

  const loadTags = async () => {
    try {
      setLoading(true)
      const data = await getTags()
      setTags(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load tags')
      setTags([])
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
      if (editingId) {
        await updateTag(editingId, form)
        setTags((current) =>
          current.map((item) => (item.id === editingId ? { ...item, ...form } : item))
        )
      } else {
        const created = await createTag(form)
        setTags((current) => [created, ...current])
      }
      setForm({ name: '', description: '' })
      setShowForm(false)
      setEditingId(null)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to save tag')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (tag) => {
    setForm({ name: tag.name, description: tag.description })
    setEditingId(tag.id)
    setShowForm(true)
  }

  const handleDelete = async (tagId) => {
    if (!window.confirm('Are you sure you want to delete this tag?')) return

    try {
      await deleteTag(tagId)
      setTags((current) => current.filter((item) => item.id !== tagId))
    } catch {
      setError('Failed to delete tag')
    }
  }

  const handleCancel = () => {
    setForm({ name: '', description: '' })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Tags</h2>
        <button className="primary-button" onClick={() => setShowForm(true)}>
          New Tag
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <label>
              <span>Tag Name</span>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g., High priority, VIP customer"
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
                rows="3"
              />
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

      {loading && !showForm ? (
        <p>Loading tags...</p>
      ) : tags.length === 0 ? (
        <p className="empty-state">No tags yet. Create one to organize your contacts.</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tags.map((tag) => (
                <tr key={tag.id}>
                  <td>
                    <strong>{tag.name}</strong>
                  </td>
                  <td>{tag.description || '-'}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleEdit(tag)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDelete(tag.id)}
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
