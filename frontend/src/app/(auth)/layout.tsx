import React from 'react'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/30">
      <div className="w-full max-w-md p-6 bg-card border rounded-lg shadow-sm">
        {children}
      </div>
    </div>
  )
}
