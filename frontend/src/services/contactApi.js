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

export const createContact = async (payload) => {
  const { data } = await api.post('/contacts', payload, {
    headers: authHeaders(),
  })

  return data
}

export const deleteContact = async (contactId) => {
  await api.delete(`/contacts/${contactId}`, {
    headers: authHeaders(),
  })
}
