import { useEffect, useState } from 'react'
import { createMailingList, deleteMailingList, getMailingLists, updateMailingList } from '../services/listApi'
import { confirmDialog, getApiErrorMessage, showToast } from '../services/dashboardUi'

export default function ListsPage() {
  const [lists, setLists] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({
    name: '',
    description: '',
  })

  useEffect(() => {
    loadLists()
  }, [])

  const loadLists = async () => {
    try {
      setLoading(true)
      const data = await getMailingLists()
      setLists(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load mailing lists')
      setLists([])
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
        await updateMailingList(editingId, form)
        setLists((current) =>
          current.map((item) => (item.id === editingId ? { ...item, ...form } : item))
        )
      } else {
        const created = await createMailingList(form)
        setLists((current) => [created, ...current])
      }
      setForm({ name: '', description: '' })
      setShowForm(false)
      setEditingId(null)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save mailing list'))
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (list) => {
    setForm({ name: list.name, description: list.description })
    setEditingId(list.id)
    setShowForm(true)
  }

  const handleDelete = async (listId) => {
    if (!await confirmDialog({ title: 'Delete mailing list?', message: 'Contacts remain safe, but this list will be removed.', confirmLabel: 'Delete list' })) return

    try {
      await deleteMailingList(listId)
      setLists((current) => current.filter((item) => item.id !== listId))
      showToast('Mailing list deleted.')
    } catch {
      setError('Failed to delete mailing list')
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
        <h2>Mailing Lists</h2>
        <button className="primary-button" onClick={() => setShowForm(true)}>
          New List
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <label>
              <span>List Name</span>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g., Newsletter subscribers"
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
        <p>Loading mailing lists...</p>
      ) : lists.length === 0 ? (
        <p className="empty-state">No mailing lists yet. Create one to get started.</p>
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
              {lists.map((list) => (
                <tr key={list.id}>
                  <td>
                    <strong>{list.name}</strong>
                  </td>
                  <td>{list.description || '-'}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleEdit(list)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDelete(list.id)}
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
