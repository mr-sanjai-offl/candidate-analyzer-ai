'use client'

import * as React from 'react'
import { Skeleton } from './skeleton'
import { Card, CardContent, CardHeader } from './card'

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-10 w-48 rounded bg-muted/40 animate-pulse" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-16" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="h-[200px]">
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/5" />
          </CardContent>
        </Card>
        <Card className="h-[200px]">
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/5" />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export function TableSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-10 w-24" />
      </div>
      <Card>
        <CardContent className="p-0">
          <div className="space-y-3 p-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex justify-between items-center border-b pb-3 last:border-0">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-8 w-16" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export function ChatSkeleton() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Skeleton className="h-10 w-64" />
      <div className="grid gap-6 md:grid-cols-4">
        <div className="md:col-span-1">
          <Card className="h-[200px]">
            <CardHeader className="p-4">
              <Skeleton className="h-4 w-28" />
            </CardHeader>
            <CardContent className="p-3 pt-0 space-y-2">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </CardContent>
          </Card>
        </div>
        <Card className="md:col-span-3 h-[500px] flex flex-col justify-between p-4">
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Skeleton className="h-8 w-8 rounded-full" />
              <Skeleton className="h-12 w-2/3" />
            </div>
            <div className="flex items-start gap-3 flex-row-reverse">
              <Skeleton className="h-8 w-8 rounded-full" />
              <Skeleton className="h-10 w-1/2" />
            </div>
          </div>
          <Skeleton className="h-10 w-full" />
        </Card>
      </div>
    </div>
  )
}
