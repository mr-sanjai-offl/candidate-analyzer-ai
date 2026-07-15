'use client'

import * as React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore, UserSession } from '@/store/authStore'

interface AuthContextType {
  user: UserSession | null
  isAuthenticated: boolean
  isLoading: boolean
  logout: () => Promise<void>
}

const AuthContext = React.createContext<AuthContextType | null>(null)

const PUBLIC_ROUTES = ['/', '/login', '/register', '/forgot-password', '/reset-password', '/components-preview']

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const store = useAuthStore()
  const [isLoading, setIsLoading] = React.useState(true)
  const initRef = React.useRef(false)

  // One-time silent auth check on mount
  React.useEffect(() => {
    if (initRef.current) return
    initRef.current = true

    const init = async () => {
      if (store.isAuthenticated && store.accessToken) {
        try {
          await store.initialize()
        } catch {
          store.clearSession()
        }
      }
      setIsLoading(false)
    }
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Multi-tab sync: listen for storage changes
  React.useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'apexguidance-auth-storage') {
        // Zustand persist will auto-rehydrate, but we force a page refresh to sync UI
        window.location.reload()
      }
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  // Route guarding
  React.useEffect(() => {
    if (isLoading) return
    const isPublicRoute = PUBLIC_ROUTES.some((r) => pathname === r || pathname.startsWith(r + '/'))

    if (!store.isAuthenticated && !isPublicRoute) {
      router.replace('/login')
    }
  }, [store.isAuthenticated, pathname, isLoading, router])

  const logout = React.useCallback(async () => {
    await store.logout()
    router.push('/login')
  }, [store, router])

  const value = React.useMemo(
    () => ({
      user: store.user,
      isAuthenticated: store.isAuthenticated,
      isLoading,
      logout,
    }),
    [store.user, store.isAuthenticated, isLoading, logout]
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

export function GuestRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  React.useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (isAuthenticated) return null

  return <>{children}</>
}

export { AuthContext }
