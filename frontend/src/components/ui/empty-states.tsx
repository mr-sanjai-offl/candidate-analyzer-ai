import * as React from 'react'
import {
  SearchX,
  ServerCrash,
  WifiOff,
  Upload,
  ShieldAlert,
  Wrench,
  Inbox,
  FileQuestion,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './button'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center text-center p-8 min-h-[300px]', className)}>
      {icon && <div className="text-muted-foreground mb-4">{icon}</div>}
      <h3 className="text-lg font-semibold tracking-tight">{title}</h3>
      {description && <p className="text-sm text-muted-foreground mt-1.5 max-w-sm">{description}</p>}
      {action && (
        <Button onClick={action.onClick} className="mt-4" size="sm">
          {action.label}
        </Button>
      )}
    </div>
  )
}

export function NoData(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<Inbox className="h-12 w-12" />}
      title="No data yet"
      description="There is no data to display at this time."
      {...props}
    />
  )
}

export function NoResults(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<SearchX className="h-12 w-12" />}
      title="No results found"
      description="Try adjusting your search or filter criteria."
      {...props}
    />
  )
}

export function NoInternet(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<WifiOff className="h-12 w-12" />}
      title="No internet connection"
      description="Please check your network and try again."
      {...props}
    />
  )
}

export function UploadEmpty(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<Upload className="h-12 w-12" />}
      title="No files uploaded"
      description="Upload a resume or document to get started."
      {...props}
    />
  )
}

export function SearchEmpty(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<FileQuestion className="h-12 w-12" />}
      title="Start searching"
      description="Enter a query to discover candidates and skills."
      {...props}
    />
  )
}

export function PermissionDenied(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<ShieldAlert className="h-12 w-12 text-orange-500" />}
      title="Permission denied"
      description="You don't have the required access to view this content."
      {...props}
    />
  )
}

export function ServerError(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<ServerCrash className="h-12 w-12 text-destructive" />}
      title="Server error"
      description="Something went wrong. Our team has been notified."
      {...props}
    />
  )
}

export function Maintenance(props: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={<Wrench className="h-12 w-12" />}
      title="Under maintenance"
      description="This feature is temporarily unavailable. Please try again later."
      {...props}
    />
  )
}
