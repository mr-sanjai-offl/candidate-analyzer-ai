'use client'

import * as React from 'react'
import { useDropzone, FileRejection } from 'react-dropzone'
import { UploadCloud, File, Trash2, CheckCircle2, AlertCircle } from 'lucide-react'
import { Button } from './button'
import { Progress } from './primitives'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  onFileSelect?: (file: File) => void
  maxSize?: number // in bytes
  accept?: Record<string, string[]>
}

export function FileUpload({
  onFileSelect,
  maxSize = 10 * 1024 * 1024, // 10MB default
  accept = { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = React.useState(0)
  const [status, setStatus] = React.useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = React.useState('')

  const onDrop = React.useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      if (rejectedFiles.length > 0) {
        setStatus('error')
        const rej = rejectedFiles[0]
        if (rej.errors[0]?.code === 'file-too-large') {
          setErrorMessage('File size exceeds the 10MB limit.')
        } else {
          setErrorMessage('Invalid file type. Only PDF and DOCX files are allowed.')
        }
        return
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        setSelectedFile(file)
        setStatus('uploading')
        setUploadProgress(0)
        setErrorMessage('')

        // Simulate mock upload progress
        const interval = setInterval(() => {
          setUploadProgress((prev) => {
            if (prev >= 100) {
              clearInterval(interval)
              setStatus('success')
              if (onFileSelect) onFileSelect(file)
              return 100
            }
            return prev + 10
          })
        }, 150)
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize,
    accept,
    multiple: false,
  })

  const removeFile = () => {
    setSelectedFile(null)
    setStatus('idle')
    setUploadProgress(0)
    setErrorMessage('')
  }

  return (
    <div className="w-full space-y-4">
      {status === 'idle' && (
        <div
          {...getRootProps()}
          className={cn(
            'flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-6 cursor-pointer bg-card hover:bg-muted/30 transition-colors',
            isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/20'
          )}
        >
          <input {...getInputProps()} />
          <UploadCloud className="h-10 w-10 text-muted-foreground mb-3" />
          <p className="text-sm font-medium">
            {isDragActive ? 'Drop your file here' : 'Drag & drop file here or click to browse'}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Supports PDF or DOCX up to 10MB
          </p>
        </div>
      )}

      {selectedFile && (
        <div className="border rounded-lg p-4 bg-card flex flex-col space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <File className="h-8 w-8 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>

            {status !== 'uploading' && (
              <Button variant="ghost" size="icon" onClick={removeFile} className="text-destructive hover:bg-destructive/10">
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>

          {status === 'uploading' && (
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-medium">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} />
            </div>
          )}

          {status === 'success' && (
            <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-500 text-sm">
              <CheckCircle2 className="h-4 w-4" />
              <span>Resume uploaded successfully! Ready for AI evaluation.</span>
            </div>
          )}
        </div>
      )}

      {status === 'error' && (
        <div className="flex items-center gap-2 border border-destructive/20 bg-destructive/5 text-destructive p-3 rounded-md text-sm">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage || 'Something went wrong during upload.'}</span>
          <Button variant="link" size="xs" onClick={removeFile} className="ml-auto text-destructive p-0 h-auto">
            Try Again
          </Button>
        </div>
      )}
    </div>
  )
}
