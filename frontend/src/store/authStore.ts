import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export interface UserSession {
  id: string
  email: string
  fullName: string
  role: 'ADMIN' | 'RECRUITER' | 'CANDIDATE'
}

interface AuthState {
  user: UserSession | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  loading: boolean
  setSession: (user: UserSession, accessToken: string, refreshToken: string) => void
  clearSession: () => void
  login: (email: string, password: string) => Promise<UserSession>
  registerUser: (email: string, password: string, fullName: string, role: 'CANDIDATE' | 'RECRUITER') => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<string>
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,

      setSession: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),

      clearSession: () =>
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false }),

      login: async (email, password) => {
        set({ loading: true })
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/login`, { email, password })
          const { access_token, refresh_token } = response.data

          // Fetch user details using the newly fetched access token
          const userResponse = await axios.get(`${API_BASE_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${access_token}` },
          })

          const userData = userResponse.data
          const userSession: UserSession = {
            id: userData.id,
            email: userData.email,
            fullName: userData.full_name,
            role: userData.role,
          }

          set({
            user: userSession,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            loading: false,
          })

          return userSession
        } catch (error) {
          set({ loading: false })
          throw error
        }
      },

      registerUser: async (email, password, fullName, role) => {
        set({ loading: true })
        try {
          await axios.post(`${API_BASE_URL}/auth/register`, {
            email,
            password,
            full_name: fullName,
            role,
          })
          set({ loading: false })
        } catch (error) {
          set({ loading: false })
          throw error
        }
      },

      logout: async () => {
        const { refreshToken } = get()
        if (refreshToken) {
          try {
            await axios.post(`${API_BASE_URL}/auth/logout`, { refresh_token: refreshToken })
          } catch (e) {
            console.error('Logout request failed:', e)
          }
        }
        get().clearSession()
      },

      refresh: async () => {
        const { refreshToken } = get()
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token } = response.data

        set({
          accessToken: access_token,
          refreshToken: refresh_token,
        })

        return access_token
      },

      initialize: async () => {
        const { accessToken, isAuthenticated } = get()
        if (isAuthenticated && accessToken) {
          try {
            const userResponse = await axios.get(`${API_BASE_URL}/auth/me`, {
              headers: { Authorization: `Bearer ${accessToken}` },
            })
            const userData = userResponse.data
            set({
              user: {
                id: userData.id,
                email: userData.email,
                fullName: userData.full_name,
                role: userData.role,
              },
            })
          } catch (error) {
            console.error('Session restoration failed:', error)
            get().clearSession()
          }
        }
      },
    }),
    {
      name: 'apexguidance-auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
