'use client'

import * as React from 'react'
import { AlertTriangle, RefreshCw, Home, WifiOff, ShieldX, Lock, FileQuestion, ServerCrash } from 'lucide-react'
import { Button } from '@/components/ui/button'

// ── Shared Layout ───────────────────────────────────────────────────────────────

interface ErrorLayoutProps {
  icon: React.ReactNode
  title: string
  description: string
  children?: React.ReactNode
}

function ErrorLayout({ icon, title, description, children }: ErrorLayoutProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center p-8 text-center" role="alert">
      <div className="mb-6 text-muted-foreground/40">{icon}</div>
      <h2 className="text-xl font-bold mb-2">{title}</h2>
      <p className="text-sm text-muted-foreground mb-6 max-w-md">{description}</p>
      <div className="flex gap-3">{children}</div>
    </div>
  )
}

// ── Retry Button ────────────────────────────────────────────────────────────────

export function RetryButton({ onRetry, label = 'Try Again' }: { onRetry: () => void; label?: string }) {
  return (
    <Button variant="outline" onClick={onRetry}>
      <RefreshCw className="h-4 w-4" />
      {label}
    </Button>
  )
}

export function HomeButton() {
  return (
    <Button variant="ghost" onClick={() => (window.location.href = '/dashboard')}>
      <Home className="h-4 w-4" />
      Go Home
    </Button>
  )
}

// ── Error Fallback (generic) ────────────────────────────────────────────────────

export function ErrorFallback({
  error,
  resetErrorBoundary,
}: {
  error?: Error
  resetErrorBoundary?: () => void
}) {
  return (
    <ErrorLayout
      icon={<AlertTriangle className="h-16 w-16" />}
      title="Something went wrong"
      description={error?.message || 'An unexpected error occurred. Please try again.'}
    >
      {resetErrorBoundary && <RetryButton onRetry={resetErrorBoundary} />}
      <HomeButton />
    </ErrorLayout>
  )
}

// ── API Error ───────────────────────────────────────────────────────────────────

export function ApiError({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <ErrorLayout
      icon={<ServerCrash className="h-16 w-16" />}
      title="API Error"
      description={message || 'Failed to communicate with the server. Please check your connection and try again.'}
    >
      {onRetry && <RetryButton onRetry={onRetry} />}
      <HomeButton />
    </ErrorLayout>
  )
}

// ── Network Error ───────────────────────────────────────────────────────────────

export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorLayout
      icon={<WifiOff className="h-16 w-16" />}
      title="No Internet Connection"
      description="Please check your network connection and try again."
    >
      {onRetry && <RetryButton onRetry={onRetry} />}
    </ErrorLayout>
  )
}

// ── Unauthorized ────────────────────────────────────────────────────────────────

export function UnauthorizedError() {
  return (
    <ErrorLayout
      icon={<Lock className="h-16 w-16" />}
      title="Unauthorized"
      description="You need to sign in to access this page."
    >
      <Button onClick={() => (window.location.href = '/login')}>Sign In</Button>
    </ErrorLayout>
  )
}

// ── Forbidden ───────────────────────────────────────────────────────────────────

export function ForbiddenError() {
  return (
    <ErrorLayout
      icon={<ShieldX className="h-16 w-16" />}
      title="Access Denied"
      description="You do not have permission to view this resource."
    >
      <HomeButton />
    </ErrorLayout>
  )
}

// ── 404 ─────────────────────────────────────────────────────────────────────────

export function NotFoundError() {
  return (
    <ErrorLayout
      icon={<FileQuestion className="h-16 w-16" />}
      title="Page Not Found"
      description="The page you are looking for does not exist or has been moved."
    >
      <HomeButton />
    </ErrorLayout>
  )
}

// ── 500 ─────────────────────────────────────────────────────────────────────────

export function InternalServerError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorLayout
      icon={<ServerCrash className="h-16 w-16" />}
      title="Internal Server Error"
      description="Our servers encountered an unexpected problem. Our team has been notified."
    >
      {onRetry && <RetryButton onRetry={onRetry} />}
      <HomeButton />
    </ErrorLayout>
  )
}

// ── Empty State ─────────────────────────────────────────────────────────────────

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="mb-4 text-muted-foreground/30">{icon}</div>}
      <h3 className="font-semibold mb-1">{title}</h3>
      {description && <p className="text-sm text-muted-foreground mb-4 max-w-sm">{description}</p>}
      {action}
    </div>
  )
}

// ── Global Error Boundary ───────────────────────────────────────────────────────

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class GlobalErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      // Sentry.captureException(error, { extra: info })
    }
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback
      return (
        <ErrorFallback
          error={this.state.error ?? undefined}
          resetErrorBoundary={() => this.setState({ hasError: false, error: null })}
        />
      )
    }
    return this.props.children
  }
}
