'use client'

import * as React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useJobMatching } from '@/hooks/use-ai'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { PageHeader } from '@/components/ui/layout-primitives'
import { Input } from '@/components/ui/input'
import { Target, AlertCircle, RefreshCw, Sparkles } from 'lucide-react'
import { toast } from 'sonner'

export default function AIJobMatchingPage() {
  const matchMutation = useJobMatching()
  const [candidateId, setCandidateId] = React.useState('')
  const [jobTitle, setJobTitle] = React.useState('')
  const [jobDescription, setJobDescription] = React.useState('')
  const [result, setResult] = React.useState<Record<string, unknown> | null>(null)

  const handleMatch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!candidateId.trim() || !jobTitle.trim() || !jobDescription.trim()) return
    setResult(null)
    try {
      const data = await matchMutation.mutateAsync({
        candidateId,
        jobTitle,
        jobDescription,
      })
      setResult(data)
      toast.success('Job description evaluation complete!')
    } catch {
      toast.error('Matching computation failed.')
    }
  }

  return (
    <ProtectedRoute allowedRoles={['RECRUITER', 'ADMIN']}>
      <div className="space-y-6 max-w-5xl mx-auto">
        <PageHeader
          title="Job Description Matcher"
          description="Evaluate candidate compatibility indicators against raw JD profiles."
        />

        <div className="grid gap-6 md:grid-cols-2">
          {/* Match Form */}
          <Card>
            <CardHeader>
              <CardTitle>JD Parameters</CardTitle>
              <CardDescription>Input target profile details and description text</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleMatch} className="space-y-4">
                <Input
                  label="Candidate Profile UUID"
                  placeholder="00000000-0000-0000-0000-000000000000"
                  value={candidateId}
                  onChange={(e) => setCandidateId(e.target.value)}
                  required
                />
                <Input
                  label="Job Title"
                  placeholder="Senior Python Architect"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  required
                />
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Job Description (JD)</label>
                  <textarea
                    placeholder="We are looking for a Python developer expert in Postgres, FastAPI, and docker..."
                    className="flex min-h-[140px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" loading={matchMutation.isPending}>
                  <Target className="h-4 w-4" />
                  Evaluate Match
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Match Results */}
          <Card>
            <CardHeader>
              <CardTitle>Compatibility Assessment</CardTitle>
              <CardDescription>Generated assessment metrics will appear here</CardDescription>
            </CardHeader>
            <CardContent className="h-[430px] overflow-y-auto flex flex-col justify-center items-center">
              {matchMutation.isPending ? (
                <div className="text-center space-y-3">
                  <RefreshCw className="h-10 w-10 text-primary animate-spin mx-auto" />
                  <p className="text-sm text-muted-foreground">Analyzing profile capabilities against JD requirements...</p>
                </div>
              ) : result ? (
                <div className="w-full space-y-6 self-start text-left">
                  <div className="flex items-center justify-between border-b pb-3">
                    <div>
                      <h4 className="font-bold text-lg">{(result.job_title as string) || jobTitle}</h4>
                      <p className="text-xs text-muted-foreground">Assessment generated successfully</p>
                    </div>
                    {result.match_score != null && (
                      <Badge variant="success" className="text-lg py-1 px-3">
                        {String(result.match_score)}% Match
                      </Badge>
                    )}
                  </div>

                  {Array.isArray(result.missing_skills) && (result.missing_skills as string[]).length > 0 && (
                    <div className="space-y-2">
                      <h5 className="font-semibold text-sm flex items-center gap-1.5 text-amber-600 dark:text-amber-500">
                        <AlertCircle className="h-4 w-4" />
                        Missing Required Skills
                      </h5>
                      <div className="flex flex-wrap gap-1.5">
                        {(result.missing_skills as string[]).map((skill) => (
                          <Badge key={skill} variant="destructive" className="text-[10px]">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {!!result.explanation && (
                    <div className="space-y-1.5">
                      <h5 className="font-semibold text-sm flex items-center gap-1.5">
                        <Sparkles className="h-4 w-4 text-primary animate-pulse" />
                        Assessment Analysis
                      </h5>
                      <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-line bg-muted/30 p-2.5 rounded-lg border border-muted">
                        {result.explanation as string}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-muted-foreground max-w-xs">
                  <Target className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="text-sm">Click &quot;Evaluate Match&quot; to begin candidate assessment against the job parameters.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
