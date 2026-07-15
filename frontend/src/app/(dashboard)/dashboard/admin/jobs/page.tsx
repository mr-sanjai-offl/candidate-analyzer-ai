'use client'

import * as React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useAdminJobs, useDeleteAdminJob } from '@/hooks/use-admin'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { PageHeader } from '@/components/ui/layout-primitives'
import { Skeleton } from '@/components/ui/skeleton'
import { Trash2, RefreshCw, AlertCircle, Activity, Search } from 'lucide-react'
import { toast } from 'sonner'

type JobStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | string

function statusVariant(status: JobStatus) {
  switch (status) {
    case 'COMPLETED':
      return 'success' as const
    case 'RUNNING':
      return 'default' as const
    case 'FAILED':
      return 'destructive' as const
    default:
      return 'secondary' as const
  }
}

export default function AdminJobsPage() {
  const [searchTerm, setSearchTerm] = React.useState('')
  const { data: jobs, isLoading, error, refetch } = useAdminJobs()
  const deleteMutation = useDeleteAdminJob()

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Job record deleted and task cancelled.')
    } catch {
      toast.error('Failed to delete job.')
    }
  }

  const filteredJobs = React.useMemo(() => {
    if (!jobs || !Array.isArray(jobs)) return []
    if (!searchTerm.trim()) return jobs
    const term = searchTerm.toLowerCase()
    return (jobs as Array<Record<string, unknown>>).filter((job) => {
      const name = ((job.job_type as string) || '').toLowerCase()
      const status = ((job.status as string) || '').toLowerCase()
      const id = ((job.id as string) || '').toLowerCase()
      return name.includes(term) || status.includes(term) || id.includes(term)
    })
  }, [jobs, searchTerm])

  return (
    <ProtectedRoute allowedRoles={['ADMIN']}>
      <div className="space-y-6">
        <PageHeader
          title="Background Jobs Monitor"
          description="Track and manage Celery background task execution."
        >
          <Button variant="outline" onClick={() => refetch()} loading={isLoading}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </PageHeader>

        {/* Search */}
        <Card>
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by job type, status, or ID..."
                className="flex h-9 w-full rounded-md border border-input bg-transparent pl-10 pr-3 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Jobs Table */}
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-14 rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-10 w-10 text-destructive mb-3" />
              <p className="text-sm text-muted-foreground mb-3">Failed to load jobs. Ensure you have admin privileges.</p>
              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            </CardContent>
          </Card>
        ) : filteredJobs.length > 0 ? (
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left font-medium">Job Type</th>
                      <th className="px-4 py-3 text-left font-medium">Status</th>
                      <th className="px-4 py-3 text-left font-medium">Created</th>
                      <th className="px-4 py-3 text-left font-medium">Celery Task</th>
                      <th className="px-4 py-3 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredJobs.map((job: Record<string, unknown>) => (
                      <tr key={job.id as string} className="border-b last:border-0 hover:bg-muted/10 transition-colors">
                        <td className="px-4 py-3">
                          <p className="font-semibold text-sm">{(job.job_type as string) || 'Unknown'}</p>
                          <p className="text-[10px] text-muted-foreground font-mono truncate max-w-[200px]">
                            {job.id as string}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={statusVariant((job.status as string) || '')}>
                            {(job.status as string) || 'UNKNOWN'}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-xs text-muted-foreground">
                          {job.created_at
                            ? new Date(job.created_at as string).toLocaleString()
                            : '—'}
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-[10px] font-mono text-muted-foreground truncate max-w-[140px] inline-block">
                            {(job.celery_task_id as string) || '—'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(job.id as string)}
                            loading={deleteMutation.isPending}
                            aria-label="Delete job"
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <Activity className="h-12 w-12 text-muted-foreground/40 mb-4" />
              <h3 className="font-semibold mb-1">No background jobs</h3>
              <p className="text-sm text-muted-foreground">
                {searchTerm ? 'No jobs match your search criteria.' : 'No background jobs found in the system.'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </ProtectedRoute>
  )
}
