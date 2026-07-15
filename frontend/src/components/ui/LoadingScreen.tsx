'use client'

import * as React from 'react'

export function LoadingSpinner({ className = 'h-8 w-8' }: { className?: string }) {
  return (
    <div
      className={`border-4 border-primary border-t-transparent rounded-full animate-spin ${className}`}
      role="status"
      aria-label="Loading"
    />
  )
}

export function LoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <LoadingSpinner className="h-12 w-12" />
        <p className="text-sm font-medium text-muted-foreground animate-pulse">
          Loading ApexGuidance AI...
        </p>
      </div>
    </div>
  )
}
