import { create } from 'zustand'
import api from '@/lib/api'

interface User {
  id: number
  username: string
  email?: string
  first_name: string
  last_name?: string
  is_admin: boolean
  is_banned: boolean
  language: string
  referral_code: string
  balance?: number
}

interface AuthState {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,

  login: async (username, password) => {
    const { data } = await api.post('/auth/login', { username, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const me = await api.get('/users/me')
    const bal = await api.get('/users/me/balance')
    set({ user: { ...me.data, balance: bal.data.amount } })
  },

  register: async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const me = await api.get('/users/me')
    const bal = await api.get('/users/me/balance')
    set({ user: { ...me.data, balance: bal.data.amount } })
  },

  logout: () => {
    localStorage.clear()
    set({ user: null })
    window.location.href = '/login'
  },

  fetchMe: async () => {
    set({ loading: true })
    try {
      const [me, bal] = await Promise.all([api.get('/users/me'), api.get('/users/me/balance')])
      set({ user: { ...me.data, balance: bal.data.amount } })
    } catch {
      localStorage.clear()
    } finally {
      set({ loading: false })
    }
  },
}))
