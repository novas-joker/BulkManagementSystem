import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const saveAuthState = (token, user) => {
  localStorage.setItem('mailforge_token', token)
  localStorage.setItem('mailforge_user', JSON.stringify(user))
}

export const clearAuthState = () => {
  localStorage.removeItem('mailforge_token')
  localStorage.removeItem('mailforge_user')
}

export const getAuthToken = () => localStorage.getItem('mailforge_token')

export const getStoredUser = () => {
  const rawUser = localStorage.getItem('mailforge_user')
  if (!rawUser) return null

  try {
    return JSON.parse(rawUser)
  } catch {
    return null
  }
}

export const loginUser = async ({ email, password }) => {
  const { data } = await api.post('/auth/login', { email, password })
  saveAuthState(data.access_token, data.user)
  return data
}

export const registerUser = async ({ full_name, email, password }) => {
  const { data } = await api.post('/auth/register', { full_name, email, password })
  saveAuthState(data.access_token, data.user)
  return data
}

export const getCurrentUserProfile = async () => {
  const token = getAuthToken()

  if (!token) {
    return null
  }

  const { data } = await api.get('/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  saveAuthState(token, data)
  return data
}

export default api
