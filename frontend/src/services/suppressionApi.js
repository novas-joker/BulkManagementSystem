import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()

  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getSuppressions = async () => {
  const { data } = await api.get('/suppressions', {
    headers: authHeaders(),
  })

  return data
}

export const createSuppression = async (payload) => {
  const { data } = await api.post('/suppressions', payload, {
    headers: authHeaders(),
  })

  return data
}

export const bulkCreateSuppressions = async (emails, reason, source = 'manual') => {
  const { data } = await api.post('/suppressions/bulk', 
    { emails, reason, source },
    {
      headers: authHeaders(),
    }
  )

  return data
}

export const deleteSuppression = async (suppressionId) => {
  await api.delete(`/suppressions/${suppressionId}`, {
    headers: authHeaders(),
  })
}
