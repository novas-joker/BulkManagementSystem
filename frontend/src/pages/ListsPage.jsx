import { useEffect, useState } from 'react'
import { createMailingList, deleteMailingList, getListContacts, getMailingLists, addContactToList, removeContactFromList, updateMailingList } from '../services/listApi'
import { getContacts } from '../services/contactApi'
import { confirmDialog, getApiErrorMessage, showToast } from '../services/dashboardUi'
import { ArrowLeft, Users } from 'lucide-react'

export default function ListsPage() {
  const [lists, setLists] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [selectedList, setSelectedList] = useState(null)
  const [listContacts, setListContacts] = useState([])
  const [allContacts, setAllContacts] = useState([])
  const [contactToAdd, setContactToAdd] = useState('')
  const [form, setForm] = useState({
    name: '',
    description: '',
  })

  const loadLists = async () => {
    try {
      setLoading(true)
      const data = await getMailingLists()
      setLists(Array.isArray(data) ? data : [])
    } catch {
      setError('Failed to load mailing lists')
      setLists([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      await loadLists()
    }
    fetchData()
  }, [])

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

  const handleOpenList = async (list) => {
    try {
      setLoading(true)
      const [members, contacts] = await Promise.all([getListContacts(list.id), getContacts()])
      setSelectedList(list)
      setListContacts(Array.isArray(members) ? members : [])
      setAllContacts(Array.isArray(contacts) ? contacts : [])
      setContactToAdd('')
      setError('')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load list contacts'))
    } finally {
      setLoading(false)
    }
  }

  const handleAddContact = async () => {
    if (!contactToAdd || !selectedList) return
    try {
      setLoading(true)
      await addContactToList(selectedList.id, contactToAdd)
      const contact = allContacts.find((item) => item.id === contactToAdd)
      if (contact) setListContacts((current) => [...current, contact])
      setSelectedList((current) => ({ ...current, contact_count: (current.contact_count || 0) + 1 }))
      setLists((current) => current.map((item) => item.id === selectedList.id ? { ...item, contact_count: (item.contact_count || 0) + 1 } : item))
      setContactToAdd('')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to add contact to list'))
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveContact = async (contactId) => {
    if (!selectedList) return
    try {
      setLoading(true)
      await removeContactFromList(selectedList.id, contactId)
      setListContacts((current) => current.filter((item) => item.id !== contactId))
      setSelectedList((current) => ({ ...current, contact_count: Math.max((current.contact_count || 1) - 1, 0) }))
      setLists((current) => current.map((item) => item.id === selectedList.id ? { ...item, contact_count: Math.max((item.contact_count || 1) - 1, 0) } : item))
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to remove contact from list'))
    } finally {
      setLoading(false)
    }
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

  const handleEdit = (list) => {
    setForm({ name: list.name, description: list.description || '' })
    setEditingId(list.id)
    setShowForm(true)
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

      {selectedList && (
        <section className="list-detail-panel">
          <div className="list-detail-header"><div><button type="button" className="back-link" onClick={() => setSelectedList(null)}><ArrowLeft size={15} aria-hidden="true" /> All mailing lists</button><span className="panel-kicker">List audience</span><h3>{selectedList.name}</h3><p>{selectedList.description || 'Contacts collected for this audience.'}</p></div><span className="list-member-count"><strong>{listContacts.length}</strong> contacts</span></div>
          <div className="list-member-toolbar"><label><span>Add a contact to this list</span><select value={contactToAdd} onChange={(event) => setContactToAdd(event.target.value)}><option value="">Choose a contact</option>{allContacts.filter((contact) => !listContacts.some((member) => member.id === contact.id)).map((contact) => <option key={contact.id} value={contact.id}>{contact.email}</option>)}</select></label><button type="button" className="primary-button" onClick={handleAddContact} disabled={!contactToAdd || loading}>Add contact</button></div>
          {listContacts.length === 0 ? <div className="list-empty-members"><span aria-hidden="true"><Users size={22} /></span><strong>This list is ready for contacts.</strong><p>Add contacts here, or choose this list while building a campaign.</p></div> : <div className="list-members-table"><div className="list-member-row list-member-row--heading"><span>Contact</span><span>Status</span><span /></div>{listContacts.map((contact) => <div className="list-member-row" key={contact.id}><span><strong>{contact.first_name || contact.last_name ? `${contact.first_name || ''} ${contact.last_name || ''}`.trim() : 'Unnamed contact'}</strong><small>{contact.email}</small></span><span className="status-badge">{contact.status}</span><button type="button" className="text-button list-remove-button" onClick={() => handleRemoveContact(contact.id)}>Remove</button></div>)}</div>}
        </section>
      )}

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
      {selectedList ? null : loading && !showForm ? (
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
                    <button type="button" className="list-name-button" onClick={() => handleOpenList(list)}><strong>{list.name}</strong><small>{list.contact_count || 0} contacts</small></button>
                  </td>
                  <td>{list.description || '-'}</td>
                  <td className="list-actions-cell">
                    <div className="list-row-actions">
                      <div className="list-edit-actions">
                        <button type="button" className="secondary-button" onClick={() => handleEdit(list)}>Edit</button>
                        <button type="button" className="secondary-button" onClick={() => handleDelete(list.id)}>Delete</button>
                      </div>
                      <div className="list-manage-action">
                        <button type="button" className="primary-button list-manage-button" onClick={() => handleOpenList(list)}>Manage contacts</button>
                      </div>
                    </div>
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
