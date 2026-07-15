'use client'

import * as React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useRecruiterSearch, type SearchParams } from '@/hooks/use-recruiter'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { PageHeader, Section } from '@/components/ui/layout-primitives'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { Search, Users, RefreshCw, AlertCircle } from 'lucide-react'

export default function RecruiterSearchPage() {
  const [skillsInput, setSkillsInput] = React.useState('')
  const [roleInput, setRoleInput] = React.useState('')
  const [minScore, setMinScore] = React.useState('')
  const [searchEnabled, setSearchEnabled] = React.useState(false)

  const params: SearchParams = React.useMemo(() => {
    const p: SearchParams = {}
    if (skillsInput.trim()) p.skills = skillsInput.split(',').map((s) => s.trim()).filter(Boolean)
    if (roleInput.trim()) p.role = roleInput.trim()
    if (minScore) p.min_capability_score = parseFloat(minScore)
    return p
  }, [skillsInput, roleInput, minScore])

  const { data, isLoading, error, refetch } = useRecruiterSearch(params, searchEnabled)

  const handleSearch = () => {
    setSearchEnabled(true)
    refetch()
  }

  return (
    <ProtectedRoute allowedRoles={['RECRUITER', 'ADMIN']}>
      <div className="space-y-6">
        <PageHeader title="Search Candidates" description="Find and evaluate candidates using filters." />

        {/* Search Filters */}
        <Card>
          <CardContent className="p-4 space-y-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <Input
                label="Skills (comma separated)"
                placeholder="React, Python, AWS..."
                value={skillsInput}
                onChange={(e) => setSkillsInput(e.target.value)}
              />
              <Input
                label="Target Role"
                placeholder="backend, frontend, fullstack..."
                value={roleInput}
                onChange={(e) => setRoleInput(e.target.value)}
              />
              <Input
                label="Min Capability Score"
                type="number"
                placeholder="0-100"
                value={minScore}
                onChange={(e) => setMinScore(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => { setSkillsInput(''); setRoleInput(''); setMinScore(''); setSearchEnabled(false) }}>
                Clear
              </Button>
              <Button onClick={handleSearch} loading={isLoading}>
                <Search className="h-4 w-4" />
                Search
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-20 rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-10 w-10 text-destructive mb-3" />
              <p className="text-sm text-muted-foreground mb-3">Search failed. Check your filters.</p>
              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            </CardContent>
          </Card>
        ) : data?.results ? (
          <Section title={`${(data.results as unknown[]).length} Candidates Found`}>
            <div className="space-y-3">
              {(data.results as Array<Record<string, unknown>>).map((candidate, idx) => (
                <Card key={idx} className="hover:border-primary/30 transition-colors">
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="min-w-0">
                      <p className="text-sm font-semibold">
                        {(candidate.full_name as string) || (candidate.email as string) || `Candidate ${idx + 1}`}
                      </p>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        {candidate.overall_score != null && (
                          <Badge variant="default" className="text-[10px]">
                            Score: {(candidate.overall_score as number).toFixed(0)}%
                          </Badge>
                        )}
                        {!!candidate.role && (
                          <Badge variant="outline" className="text-[10px]">
                            {candidate.role as string}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      View Profile
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </Section>
        ) : searchEnabled ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <Users className="h-12 w-12 text-muted-foreground/40 mb-4" />
              <h3 className="font-semibold mb-1">No candidates found</h3>
              <p className="text-sm text-muted-foreground">Try adjusting your search filters.</p>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </ProtectedRoute>
  )
}
