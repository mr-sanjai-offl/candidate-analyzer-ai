'use client'

import * as React from 'react'
import { useAuth } from '@/providers/AuthProvider'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useCapabilityScores, useReadiness, useCandidateSkills, useGapAnalysis, useTriggerAnalysis } from '@/hooks/use-candidate'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge, Progress } from '@/components/ui/primitives'
import { PageHeader, Section } from '@/components/ui/layout-primitives'
import { Skeleton } from '@/components/ui/skeleton'
import { Brain, Zap } from 'lucide-react'
import { toast } from 'sonner'

export default function CandidateEvaluationPage() {
  const { user } = useAuth()
  // For now we use a placeholder candidateId — in production this would come from a profile lookup
  const candidateId = user?.id || ''

  const scores = useCapabilityScores(candidateId)
  const readiness = useReadiness(candidateId)
  const skills = useCandidateSkills(candidateId)
  const gap = useGapAnalysis(candidateId)
  const triggerAnalysis = useTriggerAnalysis()

  const handleTriggerAnalysis = async () => {
    try {
      await triggerAnalysis.mutateAsync(candidateId)
      toast.success('Analysis triggered! This may take a few minutes.')
    } catch {
      toast.error('Failed to trigger analysis.')
    }
  }

  const hasData = scores.data || readiness.data
  const isLoading = scores.isLoading || readiness.isLoading

  return (
    <ProtectedRoute allowedRoles={['CANDIDATE']}>
      <div className="space-y-6">
        <PageHeader title="AI Evaluation" description="View your capability scores, role readiness, and skill analysis.">
          <Button onClick={handleTriggerAnalysis} loading={triggerAnalysis.isPending}>
            <Zap className="h-4 w-4" />
            Run Analysis
          </Button>
        </PageHeader>

        {isLoading ? (
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-28 rounded-lg" />
              ))}
            </div>
          </div>
        ) : !hasData ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <Brain className="h-12 w-12 text-muted-foreground/40 mb-4" />
              <h3 className="font-semibold mb-1">No evaluation data yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Upload a resume and connect your coding platforms, then run an AI analysis.
              </p>
              <Button onClick={handleTriggerAnalysis} loading={triggerAnalysis.isPending}>
                <Zap className="h-4 w-4" />
                Run First Analysis
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Role Readiness */}
            {readiness.data && (
              <Section title="Role Readiness" description="AI-assessed readiness for different engineering roles.">
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {[
                    { label: 'Backend', score: readiness.data.backend_score },
                    { label: 'Frontend', score: readiness.data.frontend_score },
                    { label: 'Full Stack', score: readiness.data.fullstack_score },
                    { label: 'AI / ML', score: readiness.data.ai_score },
                    { label: 'Data Engineering', score: readiness.data.data_score },
                    { label: 'DevOps', score: readiness.data.devops_score },
                    { label: 'Cloud', score: readiness.data.cloud_score },
                    { label: 'Cybersecurity', score: readiness.data.cybersecurity_score },
                    { label: 'Embedded', score: readiness.data.embedded_score },
                  ].map((item) => (
                    <Card key={item.label}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">{item.label}</span>
                          <span className="text-sm font-bold text-primary">{item.score ?? 0}%</span>
                        </div>
                        <Progress value={item.score ?? 0} className="h-2" />
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </Section>
            )}

            {/* Capability Scores */}
            {scores.data?.scores && (
              <Section title="Capability Scores" description="Detailed breakdown across 20 technical categories.">
                <div className="grid gap-3 sm:grid-cols-2">
                  {(scores.data.scores as Array<Record<string, unknown>>).map((s) => (
                    <Card key={s.category as string} className="hover:border-primary/30 transition-colors">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-semibold">{s.category as string}</span>
                          <Badge variant="outline" className="text-[10px]">
                            {s.proficiency as string}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-2 mt-2 text-xs text-muted-foreground">
                          <div>
                            <p className="font-medium text-foreground">{(s.confidence_score as number)?.toFixed(0)}%</p>
                            <p>Confidence</p>
                          </div>
                          <div>
                            <p className="font-medium text-foreground">{(s.experience_score as number)?.toFixed(0)}%</p>
                            <p>Experience</p>
                          </div>
                          <div>
                            <p className="font-medium text-foreground">{(s.depth_score as number)?.toFixed(0)}%</p>
                            <p>Depth</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </Section>
            )}

            {/* Skills */}
            {skills.data?.skills && (
              <Section title="Extracted Skills" description="Skills identified from your resume and platform activity.">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex flex-wrap gap-2">
                      {(skills.data.skills as Array<Record<string, unknown>>).map((skill) => (
                        <Badge key={skill.skill_name as string} variant="secondary" className="text-xs">
                          {skill.skill_name as string}
                          <span className="ml-1 text-muted-foreground">
                            ({(skill.proficiency_score as number)?.toFixed(0)}%)
                          </span>
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </Section>
            )}

            {/* Gap Analysis */}
            {gap.data && (
              <Section title="Gap Analysis" description="Areas for improvement and recommendations.">
                <Card>
                  <CardContent className="p-6">
                    {typeof gap.data === 'object' ? (
                      <pre className="text-xs text-muted-foreground whitespace-pre-wrap overflow-auto max-h-80">
                        {JSON.stringify(gap.data, null, 2)}
                      </pre>
                    ) : (
                      <p className="text-sm text-muted-foreground">Gap analysis data will appear here after evaluation.</p>
                    )}
                  </CardContent>
                </Card>
              </Section>
            )}
          </>
        )}
      </div>
    </ProtectedRoute>
  )
}
