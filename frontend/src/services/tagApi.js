import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()

  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getTags = async () => {
  const { data } = await api.get('/tags', {
    headers: authHeaders(),
  })

  return data
}

export const getTag = async (tagId) => {
  const { data } = await api.get(`/tags/${tagId}`, {
    headers: authHeaders(),
  })

  return data
}

export const createTag = async (payload) => {
  const { data } = await api.post('/tags', payload, {
    headers: authHeaders(),
  })

  return data
}

export const updateTag = async (tagId, payload) => {
  const { data } = await api.put(`/tags/${tagId}`, payload, {
    headers: authHeaders(),
  })

  return data
}

export const deleteTag = async (tagId) => {
  await api.delete(`/tags/${tagId}`, {
    headers: authHeaders(),
  })
}

export const assignTagToContact = async (tagId, contactId) => {
  const { data } = await api.post(`/tags/${tagId}/contacts/${contactId}`, {}, {
    headers: authHeaders(),
  })

  return data
}

export const removeTagFromContact = async (tagId, contactId) => {
  await api.delete(`/tags/${tagId}/contacts/${contactId}`, {
    headers: authHeaders(),
  })
}
