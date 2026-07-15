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
} from 'lucide-react'

export function Sidebar() {
  const pathname = usePathname()
  const { user } = useAuth()
  const { sidebarOpen, setSidebarOpen } = useUIStore()

  const adminLinks = [
    { href: '/dashboard/admin/users', label: 'Users', icon: Users },
    { href: '/dashboard/admin/prompts', label: 'Prompts', icon: Terminal },
    { href: '/dashboard/admin/models', label: 'Models', icon: Cpu },
  ]

  const recruiterLinks = [
    { href: '/dashboard/recruiter/search', label: 'Search', icon: Search },
    { href: '/dashboard/recruiter/candidates', label: 'Candidates', icon: Users },
  ]

  const candidateLinks = [
    { href: '/dashboard/candidate/profile', label: 'My Profile', icon: User },
    { href: '/dashboard/candidate/evaluation', label: 'Evaluation', icon: FileCode },
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

  const links = [
    { href: '/dashboard', label: 'Overview', icon: LayoutDashboard },
    ...getLinksByRole(),
  ]

  return (
    <>
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 border-r bg-background transition-transform duration-300 md:sticky md:transform-none ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex h-16 items-center justify-between px-6 border-b">
          <Link href="/dashboard" className="font-semibold text-lg">
            Dashboard
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1 rounded hover:bg-muted md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {links.map((link) => {
            const Icon = link.icon
            const isActive = pathname === link.href
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
              >
                <Icon className="h-5 w-5" />
                {link.label}
              </Link>
            )
          })}
        </nav>
      </aside>
    </>
  )
}
