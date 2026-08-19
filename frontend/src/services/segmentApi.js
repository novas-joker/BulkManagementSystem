import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()

  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getSegments = async () => {
  const { data } = await api.get('/segments', {
    headers: authHeaders(),
  })

  return data
}

export const getSegment = async (segmentId) => {
  const { data } = await api.get(`/segments/${segmentId}`, {
    headers: authHeaders(),
  })

  return data
}

export const createSegment = async (payload) => {
  const { data } = await api.post('/segments', payload, {
    headers: authHeaders(),
  })

  return data
}

export const updateSegment = async (segmentId, payload) => {
  const { data } = await api.put(`/segments/${segmentId}`, payload, {
    headers: authHeaders(),
  })

  return data
}

export const deleteSegment = async (segmentId) => {
  await api.delete(`/segments/${segmentId}`, {
    headers: authHeaders(),
  })
}

export const previewSegment = async (segmentId) => {
  const { data } = await api.post(`/segments/${segmentId}/preview`, {}, {
    headers: authHeaders(),
  })

  return data
}
