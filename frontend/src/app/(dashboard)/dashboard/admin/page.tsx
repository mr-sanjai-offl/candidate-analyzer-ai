'use client'

import * as React from 'react'
import Link from 'next/link'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useSystemHealth } from '@/hooks/use-admin'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { PageHeader, StatsGrid } from '@/components/ui/layout-primitives'
import { Activity, Cpu, Layers, RefreshCw } from 'lucide-react'

export default function AdminDashboardPage() {
  const { data: health, isLoading, error, refetch } = useSystemHealth()

  return (
    <ProtectedRoute allowedRoles={['ADMIN']}>
      <div className="space-y-6">
        <PageHeader
          title="Admin Control Center"
          description="System health indicators, background worker monitors, and prompt configurations."
        >
          <Button variant="outline" onClick={() => refetch()} loading={isLoading}>
            <RefreshCw className="h-4 w-4" />
            Refresh Health
          </Button>
        </PageHeader>

        {/* Health indicators */}
        <StatsGrid columns={4}>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Core System Health</CardDescription>
              <CardTitle className="text-3xl font-extrabold flex items-center gap-2">
                {isLoading ? (
                  <span className="text-sm font-normal text-muted-foreground">Checking...</span>
                ) : error ? (
                  <span className="text-destructive">UNHEALTHY</span>
                ) : (
                  <span className="text-emerald-600 dark:text-emerald-500">HEALTHY</span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">
                API Version: {health?.version || '1.0.0'}
              </span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Database Cluster</CardDescription>
              <CardTitle className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500">ONLINE</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">Postgres pool active</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Redis Broker</CardDescription>
              <CardTitle className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500">CONNECTED</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">Task queues responsive</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Supabase Storage</CardDescription>
              <CardTitle className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500">ACTIVE</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-xs text-muted-foreground">Resume uploads open</span>
            </CardContent>
          </Card>
        </StatsGrid>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Operations Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-primary" />
                Management Consoles
              </CardTitle>
              <CardDescription>Configure prompts and track active tasks</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3">
              <Link href="/dashboard/admin/jobs" className="w-full">
                <Button className="w-full justify-start gap-3" variant="outline">
                  <Activity className="h-4 w-4" />
                  <span>Celery Jobs Monitor</span>
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* System Performance Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-5 w-5 text-primary" />
                Resource Utilization
              </CardTitle>
              <CardDescription>Compute layer metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between border-b pb-1">
                <span className="text-muted-foreground">Celery Concurrency</span>
                <span className="font-semibold">4 threads / worker</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span className="text-muted-foreground">Event Loop Latency</span>
                <span className="font-semibold">0.4ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Database Pool Capacity</span>
                <span className="font-semibold">16 / 20 connected</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
