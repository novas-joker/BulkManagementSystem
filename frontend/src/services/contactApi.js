import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()

  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getContacts = async () => {
  const { data } = await api.get('/contacts', {
    headers: authHeaders(),
  })

  return data
}

export const getContact = async (contactId) => {
  const { data } = await api.get(`/contacts/${contactId}`, {
    headers: authHeaders(),
  })

  return data
}

export const createContact = async (payload) => {
  const { data } = await api.post('/contacts', payload, {
    headers: authHeaders(),
  })

  return data
}

export const updateContact = async (contactId, payload) => {
  const { data } = await api.put(`/contacts/${contactId}`, payload, {
    headers: authHeaders(),
  })

  return data
}

export const deleteContact = async (contactId) => {
  await api.delete(`/contacts/${contactId}`, {
    headers: authHeaders(),
  })
}

// CSV Import endpoints
export const validateCSV = async (csvContent) => {
  const { data } = await api.post('/contacts/import/validate', 
    { csv_content: csvContent },
    {
      headers: authHeaders(),
    }
  )

  return data
}

export const previewCSVImport = async (csvContent, columnMapping) => {
  const { data } = await api.post('/contacts/import/preview',
    { csv_content: csvContent, column_mapping: columnMapping },
    {
      headers: authHeaders(),
    }
  )

  return data
}

export const importCSV = async (csvContent, columnMapping, dedupStrategy = 'skip') => {
  const { data } = await api.post('/contacts/import',
    { csv_content: csvContent, column_mapping: columnMapping, dedup_strategy: dedupStrategy },
    {
      headers: authHeaders(),
    }
  )

  return data
}

// Bulk operations
export const bulkSubscribe = async (contactIds) => {
  const { data } = await api.post('/contacts/bulk-subscribe',
    { contact_ids: contactIds },
    {
      headers: authHeaders(),
    }
  )

  return data
}

export const bulkUnsubscribe = async (contactIds) => {
  const { data } = await api.post('/contacts/bulk-unsubscribe',
    { contact_ids: contactIds },
    {
      headers: authHeaders(),
    }
  )

  return data
}

