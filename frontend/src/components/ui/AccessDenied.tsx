'use client'

import * as React from 'react'
import Link from 'next/link'
import { ShieldAlert } from 'lucide-react'

export function AccessDenied() {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[400px] border border-orange-500/20 bg-orange-500/5 rounded-lg max-w-md mx-auto my-12">
      <ShieldAlert className="h-16 w-16 text-orange-500 mb-4" />
      <h1 className="text-2xl font-bold tracking-tight mb-2">Access Denied</h1>
      <p className="text-sm text-muted-foreground mb-6">
        You do not have the required permissions to view this resource or perform this action.
      </p>
      <Link
        href="/dashboard"
        className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md shadow transition-all"
      >
        Go to Dashboard
      </Link>
    </div>
  )
}
