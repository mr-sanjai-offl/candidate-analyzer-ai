'use client'

import React from 'react'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-8rem)] px-6 py-12 text-center">
      <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl mb-6">
        Evaluate Engineering Capabilities with <span className="text-primary bg-clip-text">AI Intelligence</span>
      </h1>
      <p className="max-w-2xl text-lg text-muted-foreground mb-8">
        Deep candidate capability scoring, explainable platform ranking, and context-driven chat dashboards for elite engineering teams.
      </p>
      <div className="flex flex-col sm:flex-row gap-4">
        <Link
          href="/register"
          className="px-6 py-3 text-base font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md shadow transition-all"
        >
          Get Started
        </Link>
        <Link
          href="/login"
          className="px-6 py-3 text-base font-medium border border-input bg-background hover:bg-muted rounded-md transition-all"
        >
          Sign In
        </Link>
      </div>
    </div>
  )
}
