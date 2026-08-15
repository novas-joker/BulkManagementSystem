import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()

  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getMailingLists = async () => {
  const { data } = await api.get('/lists', {
    headers: authHeaders(),
  })

  return data
}

export const getMailingList = async (listId) => {
  const { data } = await api.get(`/lists/${listId}`, {
    headers: authHeaders(),
  })

  return data
}

export const createMailingList = async (payload) => {
  const { data } = await api.post('/lists', payload, {
    headers: authHeaders(),
  })

  return data
}

export const updateMailingList = async (listId, payload) => {
  const { data } = await api.put(`/lists/${listId}`, payload, {
    headers: authHeaders(),
  })

  return data
}

export const deleteMailingList = async (listId) => {
  await api.delete(`/lists/${listId}`, {
    headers: authHeaders(),
  })
}

export const getListContacts = async (listId) => {
  const { data } = await api.get(`/lists/${listId}/contacts`, {
    headers: authHeaders(),
  })

  return data
}

export const addContactToList = async (listId, contactId) => {
  const { data } = await api.post(`/lists/${listId}/contacts/${contactId}`, {}, {
    headers: authHeaders(),
  })

  return data
}

export const removeContactFromList = async (listId, contactId) => {
  await api.delete(`/lists/${listId}/contacts/${contactId}`, {
    headers: authHeaders(),
  })
}
