import * as React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { useAuthStore } from '../src/store/authStore'
import { ProtectedRoute, GuestRoute, AuthContext } from '../src/providers/AuthProvider'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: vi.fn(),
      replace: vi.fn(),
    }
  },
  usePathname() {
    return '/dashboard'
  },
}))

describe('Auth Zustand Store', () => {
  beforeEach(() => {
    useAuthStore.getState().clearSession()
  })

  it('should initialize with authenticated false', () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
  })

  it('should set session correctly', () => {
    useAuthStore.getState().setSession(
      { id: '1', email: 'test@domain.com', fullName: 'Test User', role: 'CANDIDATE' },
      'access',
      'refresh'
    )
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
    expect(state.user?.fullName).toBe('Test User')
    expect(state.accessToken).toBe('access')
  })
})

describe('GuestRoute Guard', () => {
  it('should render children if unauthenticated', () => {
    render(
      <AuthContext.Provider
        value={{
          user: null,
          isAuthenticated: false,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <GuestRoute>
          <div>Guest Content</div>
        </GuestRoute>
      </AuthContext.Provider>
    )
    expect(screen.getByText('Guest Content')).toBeInTheDocument()
  })
})

describe('ProtectedRoute Guard', () => {
  it('should render children if authenticated and role matches', () => {
    render(
      <AuthContext.Provider
        value={{
          user: { id: '1', email: 'test@domain.com', fullName: 'Test User', role: 'CANDIDATE' },
          isAuthenticated: true,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <ProtectedRoute allowedRoles={['CANDIDATE']}>
          <div>Protected Candidate Area</div>
        </ProtectedRoute>
      </AuthContext.Provider>
    )
    expect(screen.getByText('Protected Candidate Area')).toBeInTheDocument()
  })
})
