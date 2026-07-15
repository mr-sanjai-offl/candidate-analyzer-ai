'use client'

import React from 'react'
import { useAuth } from '@/providers/AuthProvider'

export default function DashboardOverviewPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="text-muted-foreground">Welcome back, {user?.fullName}!</p>
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 bg-card border rounded-lg shadow-sm">
          <h3 className="font-semibold text-lg mb-2">Capabilities Platform</h3>
          <p className="text-sm text-muted-foreground">
            ApexGuidance AI foundation initialized. Features will load corresponding to your role: {user?.role}.
          </p>
        </div>
      </div>
    </div>
  )
}
