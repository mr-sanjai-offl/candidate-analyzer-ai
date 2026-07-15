'use client'

import * as React from 'react'
import { Button, IconButton } from '@/components/ui/button'
import { Input, Textarea } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, StatCard } from '@/components/ui/card'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { FileUpload } from '@/components/ui/file-upload'
import { DataTable, ColumnDef } from '@/components/ui/data-table'
import { CapabilityRadar, ReadinessBar, LanguageDistribution } from '@/components/ui/charts'
import { KnowledgeGraph } from '@/components/ui/knowledge-graph'
import { ChatWindow, Message } from '@/components/ui/chat'
import { Badge, Separator } from '@/components/ui/primitives'
import { Info, Sparkles, Trash } from 'lucide-react'
import { Node, Edge } from '@xyflow/react'

interface UserRow {
  id: string
  name: string
  role: string
  status: string
}

export default function ComponentsPreviewPage() {
  const [chatMessages, setChatMessages] = React.useState<Message[]>([
    { id: '1', sender: 'assistant', text: 'Hi! I can help you evaluate candidate capabilities. Ask me anything.', timestamp: new Date().toISOString() },
  ])
  const [chatLoading, setChatLoading] = React.useState(false)

  const columns: ColumnDef<UserRow>[] = [
    { id: 'name', header: 'Name', accessorKey: 'name', sortable: true },
    { id: 'role', header: 'Role', accessorKey: 'role', sortable: true },
    {
      id: 'status',
      header: 'Status',
      accessorKey: 'status',
      cell: ({ value }) => (
        <Badge variant={value === 'Active' ? 'success' : 'secondary'}>{String(value)}</Badge>
      ),
    },
  ]

  const tableData: UserRow[] = [
    { id: '1', name: 'Alice Smith', role: 'Developer', status: 'Active' },
    { id: '2', name: 'Bob Jones', role: 'Designer', status: 'Inactive' },
    { id: '3', name: 'Charlie Brown', role: 'Recruiter', status: 'Active' },
  ]

  const radarData = [
    { subject: 'Backend', score: 85 },
    { subject: 'Frontend', score: 90 },
    { subject: 'Database', score: 75 },
    { subject: 'DevOps', score: 80 },
    { subject: 'Testing', score: 70 },
  ]

  const barData = [
    { name: 'Senior Python', score: 88 },
    { name: 'DevOps Expert', score: 76 },
    { name: 'Lead Architect', score: 92 },
  ]

  const pieData = [
    { name: 'Python', value: 45 },
    { name: 'JavaScript', value: 30 },
    { name: 'Go', value: 15 },
    { name: 'Rust', value: 10 },
  ]

  const graphNodes: Node[] = [
    { id: 's1', type: 'skillNode', data: { label: 'Python', category: 'Language' }, position: { x: 100, y: 100 } },
    { id: 'e1', type: 'evidenceNode', data: { label: 'GitHub commits count: 48', confidence: 95 }, position: { x: 100, y: 250 } },
  ]

  const graphEdges: Edge[] = [
    { id: 'edge-1', source: 'e1', target: 's1', animated: true },
  ]

  const handleSendMessage = (text: string) => {
    const userMsg: Message = { id: Date.now().toString(), sender: 'user', text, timestamp: new Date().toISOString() }
    setChatMessages((prev) => [...prev, userMsg])
    setChatLoading(true)
    setTimeout(() => {
      const botMsg: Message = { id: (Date.now() + 1).toString(), sender: 'assistant', text: `This is a mock response from the preview interface for: "${text}"`, timestamp: new Date().toISOString() }
      setChatMessages((prev) => [...prev, botMsg])
      setChatLoading(false)
    }, 1000)
  }

  return (
    <div className="container mx-auto p-8 space-y-12 max-w-5xl">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">Design System & UI Library</h1>
        <p className="text-muted-foreground">Preview of all reusable UI components built for ApexGuidance AI.</p>
      </div>

      <Separator />

      {/* Buttons */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Buttons</h2>
        <div className="flex flex-wrap gap-2 items-center">
          <Button variant="default">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="success">Success</Button>
          <Button variant="warning">Warning</Button>
          <Button variant="link">Link</Button>
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <Button size="xs">Extra Small</Button>
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
          <Button size="xl">Extra Large</Button>
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <Button loading>Loading State</Button>
          <IconButton icon={<Sparkles className="h-4 w-4" />} aria-label="Sparkles" />
        </div>
      </section>

      <Separator />

      {/* Inputs */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Inputs & Textarea</h2>
        <div className="grid gap-6 md:grid-cols-2">
          <Input label="Name" placeholder="Enter your name" required />
          <Input label="Email" type="email" placeholder="you@domain.com" helperText="We will never share your email." />
          <Input label="Search" placeholder="Search entries..." prefix={<Info className="h-4 w-4" />} />
          <Input label="Error State" error="This field is required." placeholder="Invalid entry" />
          <Textarea label="Bio" placeholder="Describe yourself..." />
        </div>
      </section>

      <Separator />

      {/* Cards */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Cards & Stats</h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard title="Total Candidates" value="1,248" description="Syncing from linked profiles" trend={{ value: 12.5, label: "from last week" }} />
          <StatCard title="Overall Readiness" value="84%" description="Weighted evaluation score" trend={{ value: -2.3, label: "from yesterday" }} />
          <Card>
            <CardHeader>
              <CardTitle>Standard Card</CardTitle>
              <CardDescription>Reusable card body wrapper</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm">This is standard content inside the card.</p>
            </CardContent>
          </Card>
        </div>
      </section>

      <Separator />

      {/* Alerts */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Alert Banners</h2>
        <div className="space-y-3">
          <Alert variant="info">
            <Info className="h-4 w-4" />
            <AlertTitle>System Update</AlertTitle>
            <AlertDescription>The skill analysis engine has updated successfully.</AlertDescription>
          </Alert>
          <Alert variant="destructive">
            <Info className="h-4 w-4" />
            <AlertTitle>Error Detected</AlertTitle>
            <AlertDescription>Failed to fetch platform metrics. Please re-authenticate.</AlertDescription>
          </Alert>
        </div>
      </section>

      <Separator />

      {/* Data Table */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Data Table</h2>
        <DataTable columns={columns} data={tableData} bulkActions={() => <Button size="xs" variant="destructive"><Trash className="h-3 w-3 mr-1" /> Delete</Button>} />
      </section>

      <Separator />

      {/* File Upload */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">File Upload</h2>
        <FileUpload />
      </section>

      <Separator />

      {/* Charts */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Data Visualization Charts</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardContent className="pt-6">
              <CapabilityRadar data={radarData} title="Capability Radar" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <ReadinessBar data={barData} title="Role Readiness Bar" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <LanguageDistribution data={pieData} title="Language Distribution" />
            </CardContent>
          </Card>
        </div>
      </section>

      <Separator />

      {/* Knowledge Graph */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">React Flow Knowledge Graph</h2>
        <KnowledgeGraph nodes={graphNodes} edges={graphEdges} />
      </section>

      <Separator />

      {/* Chat Window */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">AI Chat Window</h2>
        <ChatWindow messages={chatMessages} onSendMessage={handleSendMessage} loading={chatLoading} />
      </section>
    </div>
  )
}
