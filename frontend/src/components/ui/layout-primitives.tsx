import * as React from 'react'
import Link from 'next/link'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

// ── Breadcrumb ──────────────────────────────────────────────────────────────────
interface BreadcrumbItem {
  label: string
  href?: string
}

export function Breadcrumb({ items, className }: { items: BreadcrumbItem[]; className?: string }) {
  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center gap-1.5 text-sm text-muted-foreground', className)}>
      <Link href="/dashboard" className="hover:text-foreground transition-colors">
        <Home className="h-4 w-4" />
      </Link>
      {items.map((item, i) => (
        <React.Fragment key={i}>
          <ChevronRight className="h-3.5 w-3.5" />
          {item.href ? (
            <Link href={item.href} className="hover:text-foreground transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
}

// ── Page Header ─────────────────────────────────────────────────────────────────
export function PageHeader({
  title,
  description,
  children,
  className,
}: {
  title: string
  description?: string
  children?: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn('flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4', className)}>
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  )
}

// ── Section ─────────────────────────────────────────────────────────────────────
export function Section({
  title,
  description,
  children,
  className,
}: {
  title?: string
  description?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <section className={cn('space-y-4', className)}>
      {title && (
        <div>
          <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}
      {children}
    </section>
  )
}

// ── Stats Grid ──────────────────────────────────────────────────────────────────
export function StatsGrid({
  children,
  columns = 4,
  className,
}: {
  children: React.ReactNode
  columns?: 2 | 3 | 4
  className?: string
}) {
  const gridClass = {
    2: 'sm:grid-cols-2',
    3: 'sm:grid-cols-2 lg:grid-cols-3',
    4: 'sm:grid-cols-2 lg:grid-cols-4',
  }

  return <div className={cn('grid gap-4', gridClass[columns], className)}>{children}</div>
}

// ── Toolbar ─────────────────────────────────────────────────────────────────────
export function Toolbar({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn('flex flex-wrap items-center gap-2 p-2 bg-muted/30 rounded-lg border', className)}>
      {children}
    </div>
  )
}

// ── Stepper ─────────────────────────────────────────────────────────────────────
interface Step {
  label: string
  description?: string
}

export function Stepper({
  steps,
  currentStep,
  className,
}: {
  steps: Step[]
  currentStep: number
  className?: string
}) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      {steps.map((step, i) => (
        <React.Fragment key={i}>
          <div className="flex items-center gap-2">
            <div
              className={cn(
                'flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold border-2 transition-colors',
                i < currentStep
                  ? 'bg-primary text-primary-foreground border-primary'
                  : i === currentStep
                    ? 'border-primary text-primary'
                    : 'border-muted-foreground/30 text-muted-foreground'
              )}
            >
              {i < currentStep ? '✓' : i + 1}
            </div>
            <div className="hidden sm:block">
              <p className={cn('text-sm font-medium', i <= currentStep ? 'text-foreground' : 'text-muted-foreground')}>
                {step.label}
              </p>
              {step.description && (
                <p className="text-xs text-muted-foreground">{step.description}</p>
              )}
            </div>
          </div>
          {i < steps.length - 1 && (
            <div
              className={cn(
                'flex-1 h-0.5 rounded',
                i < currentStep ? 'bg-primary' : 'bg-muted-foreground/20'
              )}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}
