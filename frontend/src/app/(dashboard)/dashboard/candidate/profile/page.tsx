'use client'

import * as React from 'react'
import { ProtectedRoute } from '@/providers/AuthProvider'
import { useResumes, useUploadResume, useDeleteResume } from '@/hooks/use-candidate'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/primitives'
import { PageHeader } from '@/components/ui/layout-primitives'
import { Skeleton } from '@/components/ui/skeleton'
import { FileUp, Trash2, RefreshCw, FileText, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'

export default function CandidateResumePage() {
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const { data: resumes, isLoading, error, refetch } = useResumes()
  const uploadMutation = useUploadResume()
  const deleteMutation = useDeleteResume()

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      await uploadMutation.mutateAsync(file)
      toast.success('Resume uploaded! Parsing will begin shortly.')
    } catch {
      toast.error('Upload failed. Please try again.')
    }
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Resume deleted.')
    } catch {
      toast.error('Failed to delete resume.')
    }
  }

  return (
    <ProtectedRoute allowedRoles={['CANDIDATE']}>
      <div className="space-y-6">
        <PageHeader title="My Resumes" description="Upload, manage, and track your resume documents.">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            className="hidden"
            onChange={handleUpload}
          />
          <Button onClick={() => fileInputRef.current?.click()} loading={uploadMutation.isPending}>
            <FileUp className="h-4 w-4" />
            Upload Resume
          </Button>
        </PageHeader>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-10 w-10 text-destructive mb-3" />
              <p className="text-sm text-muted-foreground mb-3">Failed to load resumes.</p>
              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            </CardContent>
          </Card>
        ) : !resumes || resumes.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <FileText className="h-12 w-12 text-muted-foreground/40 mb-4" />
              <h3 className="font-semibold mb-1">No resumes yet</h3>
              <p className="text-sm text-muted-foreground mb-4">Upload your first resume to get started with AI evaluation.</p>
              <Button onClick={() => fileInputRef.current?.click()}>
                <FileUp className="h-4 w-4" />
                Upload Resume
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {resumes.map((resume: Record<string, unknown>) => (
              <Card key={resume.id as string} className="hover:border-primary/30 transition-colors">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="p-2.5 bg-primary/10 rounded-lg">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold truncate">
                        {resume.original_filename as string}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge
                          variant={
                            (resume.parsing_status as string) === 'SUCCESS'
                              ? 'success'
                              : (resume.parsing_status as string) === 'FAILED'
                                ? 'destructive'
                                : 'secondary'
                          }
                          className="text-[10px]"
                        >
                          {(resume.parsing_status as string) || 'PENDING'}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {resume.created_at
                            ? new Date(resume.created_at as string).toLocaleDateString()
                            : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(resume.id as string)}
                      loading={deleteMutation.isPending}
                      aria-label="Delete resume"
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
