import { useEffect, useState } from 'react'
import {
  bulkSubscribe,
  bulkUnsubscribe,
  createContact,
  deleteContact,
  getContacts,
  importCSV,
  previewCSVImport,
  updateContact,
  validateCSV,
} from '../services/contactApi'
import { confirmDialog, getApiErrorMessage, showToast } from '../services/dashboardUi'

export default function ContactsPage() {
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [showImport, setShowImport] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [selectedContacts, setSelectedContacts] = useState(new Set())
  const [form, setForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    status: 'subscribed',
  })
  const [csvForm, setCsvForm] = useState({
    csvContent: '',
    validationResult: null,
    previewResult: null,
    columnMapping: {},
    dedupStrategy: 'skip',
    step: 'upload',
  })

  useEffect(() => {
    loadContacts()
  }, [])

  const loadContacts = async () => {
    try {
      setLoading(true)
      const data = await getContacts()
      setContacts(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load contacts')
      setContacts([])
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

  const handleCsvChange = (event) => {
    setCsvForm((current) => ({
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
        await updateContact(editingId, form)
        setContacts((current) =>
          current.map((item) => (item.id === editingId ? { ...item, ...form } : item))
        )
      } else {
        const created = await createContact(form)
        setContacts((current) => [created, ...current])
      }
      setForm({ email: '', first_name: '', last_name: '', status: 'subscribed' })
      setShowForm(false)
      setEditingId(null)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save contact'))
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (contact) => {
    setForm({
      email: contact.email,
      first_name: contact.first_name,
      last_name: contact.last_name,
      status: contact.status,
    })
    setEditingId(contact.id)
    setShowForm(true)
  }

  const handleDelete = async (contactId) => {
    if (!await confirmDialog({ title: 'Delete contact?', message: 'This contact will be removed from your audience.', confirmLabel: 'Delete contact' })) return

    try {
      await deleteContact(contactId)
      setContacts((current) => current.filter((item) => item.id !== contactId))
      showToast('Contact deleted.')
    } catch {
      setError('Failed to delete contact')
    }
  }

  const handleCancel = () => {
    setForm({ email: '', first_name: '', last_name: '', status: 'subscribed' })
    setEditingId(null)
    setShowForm(false)
  }

  // CSV Import handlers
  const handleValidateCSV = async () => {
    if (!csvForm.csvContent) {
      setError('Please paste CSV content')
      return
    }

    try {
      setLoading(true)
      const result = await validateCSV(csvForm.csvContent)
      const fieldAliases = {
        email: 'email',
        email_address: 'email',
        first_name: 'first_name',
        firstname: 'first_name',
        last_name: 'last_name',
        lastname: 'last_name',
        status: 'status',
      }
      const columnMapping = Object.fromEntries(
        (Array.isArray(result.columns) ? result.columns : [])
          .map((column) => [column, fieldAliases[column.trim().toLowerCase().replace(/\s+/g, '_')]])
          .filter(([, field]) => field)
      )

      setCsvForm((current) => ({
        ...current,
        validationResult: {
          ...result,
          columns: Array.isArray(result?.columns) ? result.columns : [],
          preview: Array.isArray(result?.preview) ? result.preview : [],
          errors: Array.isArray(result?.errors) ? result.errors : [],
        },
        columnMapping,
        step: result?.valid ? 'mapping' : 'upload',
      }))
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to validate CSV'))
    } finally {
      setLoading(false)
    }
  }

  const handlePreviewImport = async () => {
    try {
      setLoading(true)
      const result = await previewCSVImport(csvForm.csvContent, csvForm.columnMapping)
      const previewRows = Array.isArray(result) ? result : result?.preview

      setCsvForm((current) => ({
        ...current,
        previewResult: Array.isArray(previewRows) ? previewRows : [],
        step: 'preview',
      }))
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to preview import'))
    } finally {
      setLoading(false)
    }
  }

  const handleImportCSV = async () => {
    try {
      setLoading(true)
      const result = await importCSV(
        csvForm.csvContent,
        csvForm.columnMapping,
        csvForm.dedupStrategy
      )
      await loadContacts()
      setCsvForm({
        csvContent: '',
        validationResult: null,
        previewResult: null,
        columnMapping: {},
        dedupStrategy: 'skip',
        step: 'upload',
      })
      setShowImport(false)
      // Show import result
      showToast(`Import complete. Imported: ${result.imported}, skipped: ${result.skipped}, errors: ${result.errors}.`)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to import CSV'))
    } finally {
      setLoading(false)
    }
  }

  const handleToggleContact = (contactId) => {
    setSelectedContacts((current) => {
      const updated = new Set(current)
      if (updated.has(contactId)) {
        updated.delete(contactId)
      } else {
        updated.add(contactId)
      }
      return updated
    })
  }

  const handleBulkSubscribe = async () => {
    if (selectedContacts.size === 0) {
      setError('Please select at least one contact')
      return
    }

    try {
      setLoading(true)
      await bulkSubscribe(Array.from(selectedContacts))
      await loadContacts()
      setSelectedContacts(new Set())
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to update contacts'))
    } finally {
      setLoading(false)
    }
  }

  const handleBulkUnsubscribe = async () => {
    if (selectedContacts.size === 0) {
      setError('Please select at least one contact')
      return
    }

    if (!await confirmDialog({ title: 'Unsubscribe contacts?', message: 'Selected contacts will stop receiving campaigns.', confirmLabel: 'Unsubscribe' })) return

    try {
      setLoading(true)
      await bulkUnsubscribe(Array.from(selectedContacts))
      await loadContacts()
      setSelectedContacts(new Set())
      showToast('Contacts unsubscribed.')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to update contacts'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Contacts</h2>
        <div>
          <button className="primary-button" onClick={() => setShowForm(true)}>
            New Contact
          </button>
          <button className="primary-button" onClick={() => setShowImport(true)}>
            Import CSV
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {selectedContacts.size > 0 && (
        <div className="bulk-actions">
          <p>{selectedContacts.size} selected</p>
          <button className="primary-button" onClick={handleBulkSubscribe}>
            Subscribe
          </button>
          <button className="secondary-button" onClick={handleBulkUnsubscribe}>
            Unsubscribe
          </button>
        </div>
      )}

      {showForm && (
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <label>
              <span>Email</span>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="user@example.com"
                required
              />
            </label>

            <label>
              <span>First Name</span>
              <input
                type="text"
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                placeholder="John"
              />
            </label>

            <label>
              <span>Last Name</span>
              <input
                type="text"
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                placeholder="Doe"
              />
            </label>

            <label>
              <span>Status</span>
              <select name="status" value={form.status} onChange={handleChange}>
                <option value="subscribed">Subscribed</option>
                <option value="unsubscribed">Unsubscribed</option>
                <option value="bounced">Bounced</option>
              </select>
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

      {showImport && (
        <div className="form-card">
          <div className="csv-import-header">
            <h2>Import Contacts via CSV</h2>
            <div className="csv-step-indicators">
              <div className={`csv-step ${csvForm.step === 'upload' ? 'active' : csvForm.validationResult ? 'completed' : ''}`}>
                <span className="step-number">1</span>
                <span className="step-label">Upload</span>
              </div>
              <div className="csv-step-line" />
              <div className={`csv-step ${csvForm.step === 'mapping' ? 'active' : csvForm.previewResult ? 'completed' : ''}`}>
                <span className="step-number">2</span>
                <span className="step-label">Map & Configure</span>
              </div>
              <div className="csv-step-line" />
              <div className={`csv-step ${csvForm.step === 'preview' ? 'active' : ''}`}>
                <span className="step-number">3</span>
                <span className="step-label">Review & Import</span>
              </div>
            </div>
          </div>

          {csvForm.step === 'upload' && (
            <>
              <label>
                <span>Paste CSV Content</span>
                <textarea
                  name="csvContent"
                  value={csvForm.csvContent}
                  onChange={handleCsvChange}
                  placeholder="email,first_name,last_name&#10;user@example.com,John,Doe"
                  rows="6"
                />
              </label>
              <div className="form-actions">
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleValidateCSV}
                  disabled={loading}
                >
                  {loading ? 'Validating...' : 'Validate CSV'}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowImport(false)}
                >
                  Cancel
                </button>
              </div>
            </>
          )}

          {csvForm.validationResult && csvForm.step === 'mapping' && (
            <>
              <div className="csv-section">
                <h3>Detected Columns</h3>
                <div className="columns-detected">
                  {csvForm.validationResult.columns.map((col) => (
                    <span key={col} className="column-tag">{col}</span>
                  ))}
                </div>
              </div>

              {csvForm.validationResult.preview && (
                <div className="csv-section">
                  <h3>Preview (First 5 Rows)</h3>
                  <div className="preview-table-container">
                    <table className="preview-table">
                      <thead>
                        <tr>
                          {csvForm.validationResult.columns.map((col) => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {csvForm.validationResult.preview.map((row, idx) => (
                          <tr key={idx}>
                            {csvForm.validationResult.columns.map((col) => (
                              <td key={`${idx}-${col}`}>{row[col] || '-'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="csv-section">
                <label>
                  <span>Deduplication Strategy</span>
                  <select
                    name="dedupStrategy"
                    value={csvForm.dedupStrategy}
                    onChange={handleCsvChange}
                  >
                    <option value="skip">Skip duplicate emails</option>
                    <option value="merge">Merge with existing records</option>
                    <option value="overwrite">Overwrite existing records</option>
                  </select>
                </label>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="primary-button"
                  onClick={handlePreviewImport}
                  disabled={loading}
                >
                  {loading ? 'Previewing...' : 'Continue to Review'}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setCsvForm({
                      csvContent: '',
                      validationResult: null,
                      previewResult: null,
                      columnMapping: {},
                      dedupStrategy: 'skip',
                      step: 'upload',
                    })
                    setShowImport(false)
                  }}
                >
                  Cancel
                </button>
              </div>
            </>
          )}

          {csvForm.previewResult && csvForm.step === 'preview' && (
            <>
              <div className="csv-section">
                <h3>Ready to import {csvForm.previewResult.length} contacts</h3>
                <p>Strategy: <strong>{csvForm.dedupStrategy === 'skip' ? 'Skip duplicates' : csvForm.dedupStrategy === 'merge' ? 'Merge with existing' : 'Overwrite existing'}</strong></p>
              </div>

              <div className="csv-section">
                <h3>Import Preview</h3>
                <div className="preview-table-container">
                  <table className="preview-table">
                    <thead>
                      <tr>
                        <th>Email</th>
                        <th>First Name</th>
                        <th>Last Name</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {csvForm.previewResult.slice(0, 10).map((row, idx) => (
                        <tr key={idx}>
                          <td>{row.email || '-'}</td>
                          <td>{row.first_name || '-'}</td>
                          <td>{row.last_name || '-'}</td>
                          <td><span className="status-badge">{row.status || 'subscribed'}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {csvForm.previewResult.length > 10 && (
                  <p style={{ marginTop: '10px', fontSize: '0.9em', color: '#666' }}>
                    Showing first 10 of {csvForm.previewResult.length} contacts
                  </p>
                )}
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleImportCSV}
                  disabled={loading}
                >
                  {loading ? 'Importing...' : 'Complete Import'}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setCsvForm((current) => ({
                      ...current,
                      step: 'mapping',
                    }))
                  }
                >
                  Back
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {loading && !showForm && !showImport ? (
        <p>Loading contacts...</p>
      ) : contacts.length === 0 ? (
        <p className="empty-state">No contacts yet. Add your first contact to get started.</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    checked={selectedContacts.size === contacts.length && contacts.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedContacts(new Set(contacts.map((c) => c.id)))
                      } else {
                        setSelectedContacts(new Set())
                      }
                    }}
                  />
                </th>
                <th>Email</th>
                <th>Name</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {contacts.map((contact) => (
                <tr key={contact.id}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedContacts.has(contact.id)}
                      onChange={() => handleToggleContact(contact.id)}
                    />
                  </td>
                  <td>{contact.email}</td>
                  <td>
                    {contact.first_name} {contact.last_name}
                  </td>
                  <td>{contact.status}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleEdit(contact)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleDelete(contact.id)}
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
