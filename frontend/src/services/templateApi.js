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

export const getTemplate = async (templateId) => {
  const { data } = await api.get(`/templates/${templateId}`, {
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

export const duplicateTemplate = async (templateId, newName) => {
  const { data } = await api.post(`/templates/${templateId}/duplicate`,
    { new_name: newName },
    {
      headers: authHeaders(),
    }
  )

  return data
}

export const previewTemplate = async (templateId) => {
  const { data } = await api.post(`/templates/${templateId}/preview`, {}, {
    headers: authHeaders(),
  })

  return data
}

export const sendTestEmail = async (templateId, recipientEmail) => {
  const { data } = await api.post(`/templates/${templateId}/test-email`,
    { recipient_email: recipientEmail },
    {
      headers: authHeaders(),
    }
  )

  return data
}

