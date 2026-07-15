import * as React from 'react'
import { cn } from '@/lib/utils'
import { Skeleton } from './skeleton'

// ── Loading Spinner ─────────────────────────────────────────────────────────────
export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn('h-6 w-6 border-2 border-primary border-t-transparent rounded-full animate-spin', className)}
      role="status"
      aria-label="Loading"
    />
  )
}

// ── Circular Progress ───────────────────────────────────────────────────────────
export function CircularProgress({
  value,
  size = 64,
  strokeWidth = 6,
  className,
}: {
  value: number
  size?: number
  strokeWidth?: number
  className?: string
}) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} strokeWidth={strokeWidth} stroke="hsl(var(--muted))" fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          stroke="hsl(var(--primary))"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-xs font-semibold">{Math.round(value)}%</span>
    </div>
  )
}

// ── Loading Card ────────────────────────────────────────────────────────────────
export function LoadingCard() {
  return (
    <div className="rounded-lg border bg-card p-6 space-y-4 animate-pulse">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-8 w-16" />
      <Skeleton className="h-3 w-32" />
    </div>
  )
}

// ── Loading Table ───────────────────────────────────────────────────────────────
export function LoadingTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-md border bg-card overflow-hidden">
      <div className="p-4 border-b bg-muted/50">
        <div className="flex gap-4">
          {Array.from({ length: cols }).map((_, i) => (
            <Skeleton key={i} className="h-4 flex-1" />
          ))}
        </div>
      </div>
      {Array.from({ length: rows }).map((_, rIdx) => (
        <div key={rIdx} className="p-4 border-b last:border-0">
          <div className="flex gap-4">
            {Array.from({ length: cols }).map((_, cIdx) => (
              <Skeleton key={cIdx} className="h-4 flex-1" />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Loading Chart ───────────────────────────────────────────────────────────────
export function LoadingChart({ height = 300 }: { height?: number }) {
  return (
    <div className="rounded-lg border bg-card p-6 animate-pulse" style={{ height }}>
      <Skeleton className="h-4 w-24 mb-4" />
      <div className="flex items-end gap-2 h-[calc(100%-40px)]">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton
            key={i}
            className="flex-1 rounded-t"
            style={{ height: `${35 + (i * 12) % 55}%` }}
          />
        ))}
      </div>
    </div>
  )
}

// ── Loading Dashboard ───────────────────────────────────────────────────────────
export function LoadingDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <LoadingCard key={i} />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <LoadingChart />
        <LoadingChart />
      </div>
      <LoadingTable />
    </div>
  )
}
