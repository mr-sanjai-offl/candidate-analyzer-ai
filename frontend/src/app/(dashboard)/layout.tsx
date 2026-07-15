'use client'

import * as React from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { Navbar } from '@/components/layout/Navbar'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useUIStore } from '@/store/uiStore'
import { cn } from '@/lib/utils'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { sidebarCollapsed } = useUIStore()

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-muted/20">
        <Sidebar />
        <div
          className={cn(
            'flex-1 flex flex-col min-w-0 transition-all duration-300',
            sidebarCollapsed ? 'md:pl-0' : 'md:pl-0'
          )}
        >
          <Navbar />
          <main className="flex-1 p-6 md:p-8 overflow-y-auto">
            <div className="mx-auto max-w-7xl">
              {children}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
