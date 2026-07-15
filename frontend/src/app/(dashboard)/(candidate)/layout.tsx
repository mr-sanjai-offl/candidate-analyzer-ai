import React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'

export default function CandidateLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={['CANDIDATE', 'ADMIN']}>
      {children}
    </ProtectedRoute>
  )
}
