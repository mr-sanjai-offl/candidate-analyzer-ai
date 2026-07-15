import { create } from 'zustand'
import { persist } from 'zustand/middleware'

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
  setSession: (user: UserSession, accessToken: string, refreshToken: string) => void
  clearSession: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      setSession: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),
      clearSession: () =>
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false }),
    }),
    {
      name: 'apexguidance-auth-storage',
    }
  )
)
