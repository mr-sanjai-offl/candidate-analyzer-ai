'use client'

import React from 'react'
import Link from 'next/link'

export default function RegisterPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
        <p className="text-sm text-muted-foreground">Register details to get started</p>
      </div>
      <div className="space-y-4">
        <div className="p-4 bg-muted/50 rounded-md text-sm text-center border text-muted-foreground">
          Auth infrastructure complete. Signup functionality will be added in Phase 2.
        </div>
      </div>
      <div className="text-center text-sm">
        Already have an account?{' '}
        <Link href="/login" className="underline hover:text-primary">
          Login
        </Link>
      </div>
    </div>
  )
}
