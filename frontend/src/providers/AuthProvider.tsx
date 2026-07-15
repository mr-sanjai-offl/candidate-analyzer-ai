'use client'

import * as React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore, UserSession } from '@/store/authStore'
import { apiClient } from '@/lib/api-client'

interface AuthContextType {
  user: UserSession | null
  isAuthenticated: boolean
  isLoading: boolean
  logout: () => Promise<void>
}

const AuthContext = React.createContext<AuthContextType | null>(null)

const PUBLIC_ROUTES = ['/', '/login', '/register', '/forgot-password', '/reset-password']

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, isAuthenticated, accessToken, refreshToken, clearSession } = useAuthStore()
  const [isLoading, setIsLoading] = React.useState(true)

  React.useEffect(() => {
    const initAuth = async () => {
      if (isAuthenticated && accessToken) {
        try {
          await apiClient.get('/auth/me')
        } catch (error) {
          console.warn('Session verification failed on init:', error)
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [isAuthenticated, accessToken])

  React.useEffect(() => {
    if (isLoading) return

    const isPublicRoute = PUBLIC_ROUTES.includes(pathname)

    if (!isAuthenticated && !isPublicRoute) {
      router.replace('/login')
    } else if (isAuthenticated && isPublicRoute && pathname !== '/') {
      router.replace('/dashboard')
    }
  }, [isAuthenticated, pathname, isLoading, router])

  const logout = React.useCallback(async () => {
    try {
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refresh_token: refreshToken })
      }
    } catch (e) {
      console.error('Logout request failed:', e)
    } finally {
      clearSession()
      router.push('/login')
    }
  }, [refreshToken, clearSession, router])

  const value = React.useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      logout,
    }),
    [user, isAuthenticated, isLoading, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode
  allowedRoles?: Array<'ADMIN' | 'RECRUITER' | 'CANDIDATE'>
}) {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  React.useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.replace('/login')
      } else if (allowedRoles && user && !allowedRoles.includes(user.role)) {
        router.replace('/unauthorized')
      }
    }
  }, [isAuthenticated, user, isLoading, allowedRoles, router])

  if (isLoading || !isAuthenticated || (allowedRoles && user && !allowedRoles.includes(user.role))) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return <>{children}</>
}
export { AuthContext }
