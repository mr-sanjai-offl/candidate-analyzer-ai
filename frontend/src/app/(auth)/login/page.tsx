'use client'

import React from 'react'
import Link from 'next/link'

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Login to your account</h1>
        <p className="text-sm text-muted-foreground">Enter your credentials to continue</p>
      </div>
      <div className="space-y-4">
        <div className="p-4 bg-muted/50 rounded-md text-sm text-center border text-muted-foreground">
          Auth infrastructure complete. Sign in functionality will be added in Phase 2.
        </div>
      </div>
      <div className="text-center text-sm">
        Don&apos;t have an account?{' '}
        <Link href="/register" className="underline hover:text-primary">
          Register
        </Link>
      </div>
    </div>
  )
}
