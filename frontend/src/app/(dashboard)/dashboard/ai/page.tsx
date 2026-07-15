'use client'

import * as React from 'react'
import Link from 'next/link'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { PageHeader, StatsGrid } from '@/components/ui/layout-primitives'
import { MessageSquare, Target, Activity, Sparkles } from 'lucide-react'

export default function AIDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={['CANDIDATE', 'RECRUITER', 'ADMIN']}>
      <div className="space-y-6">
        <PageHeader
          title="AI Workspace"
          description="Explore assessment analytics, chat with the evaluation helper, and evaluate job fits."
        />

        <StatsGrid columns={4}>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Today&apos;s Queries</CardDescription>
              <CardTitle className="text-3xl font-extrabold text-primary">48</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">Within system rate bounds</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Model Usage</CardDescription>
              <CardTitle className="text-xl font-bold truncate">GPT-4o / Claude 3.5</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="outline">Enterprise Tier</Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Average Latency</CardDescription>
              <CardTitle className="text-3xl font-extrabold">1.4s</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">Optimized token streaming</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Engine Status</CardDescription>
              <CardTitle className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500">READY</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">Evaluation workers active</span>
            </CardContent>
          </Card>
        </StatsGrid>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Quick Actions
              </CardTitle>
              <CardDescription>Select an AI capability module to launch</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3">
              <Link href="/dashboard/ai/chat" className="w-full">
                <Button className="w-full justify-start gap-3" variant="outline">
                  <MessageSquare className="h-4 w-4" />
                  <span>Q&A Chat Assistant</span>
                </Button>
              </Link>
              <Link href="/dashboard/ai/match" className="w-full">
                <Button className="w-full justify-start gap-3" variant="outline">
                  <Target className="h-4 w-4" />
                  <span>Job Description Matcher</span>
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Model Statistics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Capabilities Mapping
              </CardTitle>
              <CardDescription>Summary of LLM extraction details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between border-b pb-1">
                <span className="text-muted-foreground">Resume Parsing</span>
                <span className="font-semibold">Gemini 1.5 Flash (OCR + Extraction)</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span className="text-muted-foreground">Confidence Grading</span>
                <span className="font-semibold">Multi-criteria grading algorithm</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Security Sandbox</span>
                <span className="font-semibold text-emerald-600">Active</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
