'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/providers/AuthProvider'
import { useUIStore } from '@/store/uiStore'
import {
  LayoutDashboard,
  User,
  Users,
  Search,
  X,
  FileCode,
  Terminal,
  Cpu,
  Brain,
  FileBarChart,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const { sidebarOpen, setSidebarOpen, sidebarCollapsed, setSidebarCollapsed } = useUIStore()

  // Load persistent collapse state
  React.useEffect(() => {
    const val = localStorage.getItem('apexguidance-sidebar-collapsed')
    if (val !== null) {
      setSidebarCollapsed(val === 'true')
    }
  }, [setSidebarCollapsed])

  const toggleCollapsed = () => {
    const nextVal = !sidebarCollapsed
    setSidebarCollapsed(nextVal)
    localStorage.setItem('apexguidance-sidebar-collapsed', String(nextVal))
  }

  const commonLinks = [
    { href: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  ]

  const adminLinks = [
    { href: '/dashboard/admin/users', label: 'Users', icon: Users },
    { href: '/dashboard/admin/prompts', label: 'Prompts', icon: Terminal },
    { href: '/dashboard/admin/models', label: 'Models', icon: Cpu },
  ]

  const recruiterLinks = [
    { href: '/dashboard/recruiter/search', label: 'Search Candidates', icon: Search },
    { href: '/dashboard/recruiter/candidates', label: 'Candidates List', icon: Users },
    { href: '/dashboard/ai-analytics', label: 'AI Evaluation', icon: Brain },
    { href: '/dashboard/reports', label: 'Hiring Reports', icon: FileBarChart },
  ]

  const candidateLinks = [
    { href: '/dashboard/candidate/profile', label: 'My Resume', icon: User },
    { href: '/dashboard/candidate/evaluation', label: 'AI Evaluation', icon: FileCode },
  ]

  const getLinksByRole = () => {
    switch (user?.role) {
      case 'ADMIN':
        return adminLinks
      case 'RECRUITER':
        return recruiterLinks
      case 'CANDIDATE':
        return candidateLinks
      default:
        return []
    }
  }

  const footerLinks = [
    { href: '/dashboard/settings', label: 'Settings', icon: Settings },
  ]

  const roleLinks = getLinksByRole()

  return (
    <>
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden animate-in fade-in-0"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={cn(
          'fixed top-0 bottom-0 left-0 z-50 flex flex-col border-r bg-card transition-all duration-300 md:sticky md:transform-none h-screen',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b">
          <Link href="/dashboard" className="flex items-center gap-2 font-bold tracking-tight">
            <span className="text-primary text-lg">ApexGuidance</span>
            {!sidebarCollapsed && <span className="text-muted-foreground font-light text-xs">AI</span>}
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-md hover:bg-muted md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation Area */}
        <div className="flex-1 overflow-y-auto p-3 space-y-6">
          <div className="space-y-1">
            {commonLinks.map((link) => {
              const Icon = link.icon
              const isActive = pathname === link.href
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-all',
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  )}
                  title={sidebarCollapsed ? link.label : undefined}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {!sidebarCollapsed && <span>{link.label}</span>}
                </Link>
              )
            })}
          </div>

          {roleLinks.length > 0 && (
            <div className="space-y-1">
              {!sidebarCollapsed && (
                <p className="text-[10px] font-bold text-muted-foreground/60 uppercase tracking-wider px-3 mb-2">
                  {user?.role} Workspace
                </p>
              )}
              {roleLinks.map((link) => {
                const Icon = link.icon
                const isActive = pathname === link.href
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setSidebarOpen(false)}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-all',
                      isActive
                        ? 'bg-primary text-primary-foreground shadow-sm'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    )}
                    title={sidebarCollapsed ? link.label : undefined}
                  >
                    <Icon className="h-5 w-5 shrink-0" />
                    {!sidebarCollapsed && <span>{link.label}</span>}
                  </Link>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="p-3 border-t space-y-1 bg-card">
          {footerLinks.map((link) => {
            const Icon = link.icon
            const isActive = pathname === link.href
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-all',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
                title={sidebarCollapsed ? link.label : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!sidebarCollapsed && <span>{link.label}</span>}
              </Link>
            )
          })}

          <button
            onClick={() => {
              setSidebarOpen(false)
              logout()
            }}
            className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-all w-full text-left text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
            title={sidebarCollapsed ? 'Logout' : undefined}
          >
            <LogOut className="h-5 w-5 shrink-0" />
            {!sidebarCollapsed && <span>Logout</span>}
          </button>

          {/* Sidebar Collapse Toggle (Desktop only) */}
          <button
            onClick={toggleCollapsed}
            className="hidden md:flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md w-full text-left text-muted-foreground hover:bg-muted hover:text-foreground transition-all mt-4 border-t pt-3"
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-5 w-5 shrink-0" />
            ) : (
              <>
                <ChevronLeft className="h-5 w-5 shrink-0" />
                <span>Collapse Menu</span>
              </>
            )}
          </button>
        </div>
      </aside>
    </>
  )
}
