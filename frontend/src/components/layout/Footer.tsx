'use client'

import * as React from 'react'
import Link from 'next/link'

export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0 bg-background/50">
      <div className="flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row px-6">
        <p className="text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} ApexGuidance AI. All rights reserved.
        </p>
        <div className="flex gap-4 text-sm text-muted-foreground">
          <Link href="/terms" className="hover:text-foreground">
            Terms
          </Link>
          <Link href="/privacy" className="hover:text-foreground">
            Privacy
          </Link>
        </div>
      </div>
    </footer>
  )
}
