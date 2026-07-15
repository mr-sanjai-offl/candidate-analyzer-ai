'use client'

import * as React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useRecruiterSearch } from '@/hooks/use-recruiter'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { PageHeader } from '@/components/ui/layout-primitives'
import { Skeleton } from '@/components/ui/skeleton'
import { Users, Eye, RefreshCw, AlertCircle } from 'lucide-react'

export default function RecruiterCandidatesPage() {
  // Load all candidates with no filters
  const { data, isLoading, error, refetch } = useRecruiterSearch({}, true)

  return (
    <ProtectedRoute allowedRoles={['RECRUITER', 'ADMIN']}>
      <div className="space-y-6">
        <PageHeader title="Candidates List" description="Browse all evaluated candidates in the system.">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </PageHeader>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-10 w-10 text-destructive mb-3" />
              <p className="text-sm text-muted-foreground mb-3">Failed to load candidates.</p>
              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            </CardContent>
          </Card>
        ) : data?.results && (data.results as unknown[]).length > 0 ? (
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left font-medium">Candidate</th>
                      <th className="px-4 py-3 text-left font-medium">Score</th>
                      <th className="px-4 py-3 text-left font-medium">Role</th>
                      <th className="px-4 py-3 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data.results as Array<Record<string, unknown>>).map((candidate, idx) => (
                      <tr key={idx} className="border-b last:border-0 hover:bg-muted/10 transition-colors">
                        <td className="px-4 py-3">
                          <div>
                            <p className="font-semibold text-sm">
                              {(candidate.full_name as string) || `Candidate ${idx + 1}`}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {candidate.email as string}
                            </p>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {candidate.overall_score != null ? (
                            <Badge
                              variant={
                                (candidate.overall_score as number) >= 80
                                  ? 'success'
                                  : (candidate.overall_score as number) >= 50
                                    ? 'secondary'
                                    : 'destructive'
                              }
                            >
                              {(candidate.overall_score as number).toFixed(0)}%
                            </Badge>
                          ) : (
                            <span className="text-xs text-muted-foreground">N/A</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="outline" className="text-[10px]">
                            {(candidate.role as string) || 'General'}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
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
              <Users className="h-12 w-12 text-muted-foreground/40 mb-4" />
              <h3 className="font-semibold mb-1">No candidates</h3>
              <p className="text-sm text-muted-foreground">No candidate profiles found in the system.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </ProtectedRoute>
  )
}
