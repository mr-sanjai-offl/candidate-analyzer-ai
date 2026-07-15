import * as React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AuthContext } from '../src/providers/AuthProvider'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter() {
    return { push: vi.fn(), replace: vi.fn() }
  },
  usePathname() {
    return '/dashboard/ai'
  },
}))

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) =>
    React.createElement('a', { href }, children),
}))

// Mock React Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: () => ({ data: null, isLoading: false, error: null, refetch: vi.fn() }),
  useMutation: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
  }),
  useQueryClient: () => ({ invalidateQueries: vi.fn() }),
}))

// ── AI Workspace Tests ──────────────────────────────────────────────────────────

describe('AI Dashboard Page', () => {
  it('should render AI workspace for ADMIN user', async () => {
    // Dynamic import to ensure mocks are applied first
    const { default: AIDashboardPage } = await import(
      '../src/app/(dashboard)/dashboard/ai/page'
    )

    render(
      <AuthContext.Provider
        value={{
          user: { id: '1', email: 'admin@test.com', fullName: 'Admin', role: 'ADMIN' },
          isAuthenticated: true,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <AIDashboardPage />
      </AuthContext.Provider>
    )

    expect(screen.getByText('AI Workspace')).toBeInTheDocument()
    expect(screen.getByText('Q&A Chat Assistant')).toBeInTheDocument()
    expect(screen.getByText('Job Description Matcher')).toBeInTheDocument()
  })
})

describe('AI Chat Page', () => {
  it('should render the chat interface with welcome message', async () => {
    const { default: AIChatPage } = await import(
      '../src/app/(dashboard)/dashboard/ai/chat/page'
    )

    render(
      <AuthContext.Provider
        value={{
          user: { id: '1', email: 'rec@test.com', fullName: 'Recruiter', role: 'RECRUITER' },
          isAuthenticated: true,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <AIChatPage />
      </AuthContext.Provider>
    )

    expect(screen.getByText('Q&A Chat Assistant')).toBeInTheDocument()
    expect(
      screen.getByText(/Hello! I am your candidate assessment assistant/)
    ).toBeInTheDocument()
  })
})

// ── Admin Panel Tests ───────────────────────────────────────────────────────────

describe('Admin Dashboard Page', () => {
  it('should render admin dashboard for ADMIN user', async () => {
    const { default: AdminDashboardPage } = await import(
      '../src/app/(dashboard)/dashboard/admin/page'
    )

    render(
      <AuthContext.Provider
        value={{
          user: { id: '1', email: 'admin@test.com', fullName: 'Admin', role: 'ADMIN' },
          isAuthenticated: true,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <AdminDashboardPage />
      </AuthContext.Provider>
    )

    expect(screen.getByText('Admin Control Center')).toBeInTheDocument()
    expect(screen.getByText('Celery Jobs Monitor')).toBeInTheDocument()
  })
})

describe('Admin Role Guard', () => {
  it('should NOT render admin dashboard for CANDIDATE user', async () => {
    const { default: AdminDashboardPage } = await import(
      '../src/app/(dashboard)/dashboard/admin/page'
    )

    render(
      <AuthContext.Provider
        value={{
          user: { id: '2', email: 'user@test.com', fullName: 'Cand', role: 'CANDIDATE' },
          isAuthenticated: true,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <AdminDashboardPage />
      </AuthContext.Provider>
    )

    // Admin Control Center should NOT appear for CANDIDATE role
    expect(screen.queryByText('Admin Control Center')).not.toBeInTheDocument()
  })
})

describe('Admin Jobs Monitor Page', () => {
  it('should render background jobs monitor for ADMIN user', async () => {
    const { default: AdminJobsPage } = await import(
      '../src/app/(dashboard)/dashboard/admin/jobs/page'
    )

    render(
      <AuthContext.Provider
        value={{
          user: { id: '1', email: 'admin@test.com', fullName: 'Admin', role: 'ADMIN' },
          isAuthenticated: true,
          isLoading: false,
          logout: async () => {},
        }}
      >
        <AdminJobsPage />
      </AuthContext.Provider>
    )

    expect(screen.getByText('Background Jobs Monitor')).toBeInTheDocument()
    expect(screen.getByText('No background jobs')).toBeInTheDocument()
  })
})
