'use client'

import * as React from 'react'
import { WifiOff, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function OfflinePage() {
  const handleReload = () => {
    window.location.reload()
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-6 text-center" role="alert">
      <div className="mb-6 rounded-full bg-muted p-4 text-muted-foreground">
        <WifiOff className="h-12 w-12" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        You are offline
      </h1>
      <p className="mt-3 text-muted-foreground max-w-sm">
        Please check your network settings. Once you are back online, click below to refresh the page.
      </p>
      <div className="mt-8">
        <Button onClick={handleReload} className="gap-2">
          <RotateCcw className="h-4 w-4" />
          Refresh Connection
        </Button>
      </div>
    </div>
  )
}
