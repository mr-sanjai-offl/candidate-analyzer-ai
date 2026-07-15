'use client'

import * as React from 'react'
import { useAuth } from '@/providers/AuthProvider'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { Section, PageHeader, StatsGrid } from '@/components/ui/layout-primitives'
import { Sparkles, FileText, PlusCircle, Cpu, ShieldAlert } from 'lucide-react'

export default function DashboardPage() {
  const { user } = useAuth()

  const renderCandidateDashboard = () => (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome back, ${user?.fullName}!`}
        description="Here is the status of your resume assessment and evaluation."
      />

      <StatsGrid columns={3}>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Evaluation Score</CardDescription>
            <CardTitle className="text-3xl font-extrabold text-primary">85/100</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="success">High Readiness</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Profile</CardDescription>
            <CardTitle className="text-xl font-bold truncate">{user?.email}</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">LinkedIn Connected</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Assessments Run</CardDescription>
            <CardTitle className="text-3xl font-extrabold">2</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">Last checked today</span>
          </CardContent>
        </Card>
      </StatsGrid>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Resume Documents
            </CardTitle>
            <CardDescription>Manage and update your uploaded files</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/10">
              <div className="min-w-0">
                <p className="text-sm font-semibold truncate">Jane_Doe_Resume_2026.pdf</p>
                <p className="text-xs text-muted-foreground">Uploaded 2 days ago</p>
              </div>
              <Badge variant="success">Analyzed</Badge>
            </div>
            <Button className="w-full">
              <PlusCircle className="h-4 w-4" />
              Upload New Resume
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary animate-pulse" />
              AI Recommendations
            </CardTitle>
            <CardDescription>Top suggested roles based on your experience</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 border rounded-lg hover:border-primary/40 transition-colors">
              <h5 className="font-semibold text-sm">Senior Full Stack Engineer</h5>
              <p className="text-xs text-muted-foreground mt-1">94% match probability</p>
            </div>
            <div className="p-3 border rounded-lg hover:border-primary/40 transition-colors">
              <h5 className="font-semibold text-sm">DevOps Architect</h5>
              <p className="text-xs text-muted-foreground mt-1">82% match probability</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderRecruiterDashboard = () => (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome back, ${user?.fullName}!`}
        description="Recruiter overview panel and candidate analytics."
      />

      <StatsGrid columns={3}>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Candidates</CardDescription>
            <CardTitle className="text-3xl font-extrabold text-primary">1,248</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">+12.5% from last week</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Assessments Done</CardDescription>
            <CardTitle className="text-3xl font-extrabold">342</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">98% pipeline completion rate</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Average Score</CardDescription>
            <CardTitle className="text-3xl font-extrabold">78.4%</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">Qualified candidate benchmark</span>
          </CardContent>
        </Card>
      </StatsGrid>

      <Section title="Recent Activity" description="Assessments processed recently.">
        <Card>
          <CardContent className="p-0">
            <div className="divide-y">
              {[
                { name: 'Alice Smith', role: 'React Developer', score: 92, time: '2 hours ago' },
                { name: 'Bob Jones', role: 'Backend Engineer', score: 78, time: '5 hours ago' },
                { name: 'Charlie Brown', role: 'Security Engineer', score: 85, time: '1 day ago' },
              ].map((c) => (
                <div key={c.name} className="flex items-center justify-between p-4 hover:bg-muted/10 transition-colors">
                  <div>
                    <p className="text-sm font-semibold">{c.name}</p>
                    <p className="text-xs text-muted-foreground">{c.role} • {c.time}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{c.score}% Match</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </Section>
    </div>
  )

  const renderAdminDashboard = () => (
    <div className="space-y-6">
      <PageHeader
        title="Admin Overview"
        description="System management and platform metrics."
      />

      <StatsGrid columns={3}>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Registered Users</CardDescription>
            <CardTitle className="text-3xl font-extrabold text-primary">1,624</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">1,248 Candidates, 376 Recruiters</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>System Status</CardDescription>
            <CardTitle className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500">HEALTHY</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">All server systems online</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Evaluation Queue</CardDescription>
            <CardTitle className="text-3xl font-extrabold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-muted-foreground">0 pending tasks in rabbitmq</span>
          </CardContent>
        </Card>
      </StatsGrid>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-primary" />
              Platform Performance
            </CardTitle>
            <CardDescription>API latency statistics and compute details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm py-1 border-b">
              <span className="text-muted-foreground">Database Latency</span>
              <span className="font-semibold">4.8ms</span>
            </div>
            <div className="flex justify-between text-sm py-1 border-b">
              <span className="text-muted-foreground">RabbitMQ State</span>
              <span className="font-semibold text-emerald-600">Active</span>
            </div>
            <div className="flex justify-between text-sm py-1">
              <span className="text-muted-foreground">Celery Worker Health</span>
              <span className="font-semibold text-emerald-600">Idle (0/4 busy)</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-amber-500" />
              Security Audit logs
            </CardTitle>
            <CardDescription>Recent system events and checks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="p-2.5 border rounded-lg bg-muted/20">
              <p className="font-semibold">JWT token rotation success</p>
              <p className="text-muted-foreground mt-0.5">User alice@domain.com rotated token • 2 minutes ago</p>
            </div>
            <div className="p-2.5 border rounded-lg bg-muted/20">
              <p className="font-semibold">Database backup complete</p>
              <p className="text-muted-foreground mt-0.5">System auto-backup to local postgres snapshot • 1 hour ago</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  switch (user?.role) {
    case 'CANDIDATE':
      return renderCandidateDashboard()
    case 'RECRUITER':
      return renderRecruiterDashboard()
    case 'ADMIN':
      return renderAdminDashboard()
    default:
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <h2 className="text-lg font-bold">Session loading...</h2>
        </div>
      )
  }
}
