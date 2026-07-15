'use client'

import * as React from 'react'
import { ThemeProvider } from './ThemeProvider'
import { QueryProvider } from './QueryProvider'
import { AuthProvider } from './AuthProvider'
import { Toaster } from 'sonner'
import { AnalyticsTracker } from '@/components/layout/AnalyticsTracker'

export function AppProvider({ children }: { children: React.ReactNode }) {
  return (
    <QueryProvider>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <AuthProvider>
          <React.Suspense fallback={null}>
            <AnalyticsTracker />
          </React.Suspense>
          {children}
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </ThemeProvider>
    </QueryProvider>
  )
}
