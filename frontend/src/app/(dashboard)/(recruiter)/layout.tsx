import React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'

export default function RecruiterLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={['RECRUITER', 'ADMIN']}>
      {children}
    </ProtectedRoute>
  )
}
