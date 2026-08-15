import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()

  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getTemplates = async () => {
  const { data } = await api.get('/templates', {
    headers: authHeaders(),
  })

  return data
}

export const createTemplate = async (payload) => {
  const { data } = await api.post('/templates', payload, {
    headers: authHeaders(),
  })

  return data
}

export const updateTemplate = async (templateId, payload) => {
  const { data } = await api.put(`/templates/${templateId}`, payload, {
    headers: authHeaders(),
  })

  return data
}

export const deleteTemplate = async (templateId) => {
  await api.delete(`/templates/${templateId}`, {
    headers: authHeaders(),
  })
}
