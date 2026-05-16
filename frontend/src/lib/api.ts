import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 15000,
})

// Attach token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_URL}/api/v1/auth/refresh`, { refresh_token: refresh })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          err.config.headers.Authorization = `Bearer ${data.access_token}`
          return api.request(err.config)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api
