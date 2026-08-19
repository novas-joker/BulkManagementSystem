import api, { getAuthToken } from './authApi'

const authHeaders = () => {
  const token = getAuthToken()
  return {
    Authorization: `Bearer ${token}`,
  }
}

export const getCampaigns = async () => {
  const { data } = await api.get('/campaigns', {
    headers: authHeaders(),
  })
  return data
}

export const createCampaign = async (payload) => {
  const { data } = await api.post('/campaigns', payload, {
    headers: authHeaders(),
  })
  return data
}

export const updateCampaign = async (campaignId, payload) => {
  const { data } = await api.put(`/campaigns/${campaignId}`, payload, {
    headers: authHeaders(),
  })
  return data
}

export const deleteCampaign = async (campaignId) => {
  await api.delete(`/campaigns/${campaignId}`, {
    headers: authHeaders(),
  })
}

export const sendCampaignTestEmail = async (campaignId, recipientEmail) => {
  const { data } = await api.post(`/campaigns/${campaignId}/test-email`, {
    recipient_email: recipientEmail,
  }, {
    headers: authHeaders(),
  })
  return data
}
