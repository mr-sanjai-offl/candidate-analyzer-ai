'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { X } from 'lucide-react'

// ── Sheet / Drawer ──────────────────────────────────────────────────────────────
interface SheetProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  side?: 'left' | 'right'
  className?: string
  title?: string
}

export function Sheet({ open, onClose, children, side = 'right', className, title }: SheetProps) {
  // Close on Escape key
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (open) document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, onClose])

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/80 animate-in fade-in-0"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Panel */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title || 'Panel'}
        className={cn(
          'fixed z-50 flex flex-col bg-background shadow-lg border',
          side === 'right' && 'inset-y-0 right-0 w-full sm:w-[400px] animate-in slide-in-from-right',
          side === 'left' && 'inset-y-0 left-0 w-full sm:w-[400px] animate-in slide-in-from-left',
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">{title || 'Details'}</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-muted transition-colors"
            aria-label="Close panel"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">{children}</div>
      </div>
    </>
  )
}
