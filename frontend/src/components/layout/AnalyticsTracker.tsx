'use client'

import * as React from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { analytics } from '@/lib/analytics'

export function AnalyticsTracker() {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  React.useEffect(() => {
    analytics.init()
  }, [])

  React.useEffect(() => {
    const url = `${pathname}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    analytics.trackPageView(url)
  }, [pathname, searchParams])

  return null
}
