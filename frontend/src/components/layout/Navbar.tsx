'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/providers/AuthProvider'
import { ThemeToggle } from './ThemeToggle'
import { Menu, LogOut, Bell, Search, User, Shield, ChevronDown } from 'lucide-react'
import { useUIStore } from '@/store/uiStore'
import { useNotificationStore } from '@/store/notificationStore'
import { Breadcrumb } from '@/components/ui/layout-primitives'
import { Badge, Avatar, AvatarFallback } from '@/components/ui/primitives'

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const { toggleSidebar } = useUIStore()
  const { unreadCount } = useNotificationStore()
  const pathname = usePathname()
  const [profileOpen, setProfileOpen] = React.useState(false)

  // Auto-generate breadcrumb items based on URL path segments
  const breadcrumbItems = React.useMemo(() => {
    const segments = pathname.split('/').filter(Boolean)
    if (segments.length <= 1) return []

    return segments.slice(1).map((segment, index) => {
      const href = '/' + segments.slice(0, index + 2).join('/')
      const label = segment
        .replace(/-/g, ' ')
        .replace(/\b\w/g, (char) => char.toUpperCase())
      return { label, href }
    })
  }, [pathname])

  const initials = React.useMemo(() => {
    if (!user?.fullName) return 'U'
    return user.fullName
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase()
  }, [user])

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 md:px-6 justify-between">
        <div className="flex items-center gap-4 flex-1">
          {isAuthenticated && (
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-md md:hidden hover:bg-muted transition-colors"
              aria-label="Toggle Sidebar"
            >
              <Menu className="h-5 w-5" />
            </button>
          )}

          {/* Breadcrumb section */}
          {isAuthenticated && breadcrumbItems.length > 0 ? (
            <Breadcrumb items={breadcrumbItems} className="hidden md:flex" />
          ) : (
            <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight">
              <span className="text-primary">ApexGuidance</span>
              <span className="text-muted-foreground font-light text-sm">AI</span>
            </Link>
          )}
        </div>

        {/* Action controls */}
        <div className="flex items-center gap-4">
          {/* Quick Search placeholder */}
          {isAuthenticated && (
            <div className="relative w-40 sm:w-60 hidden md:block">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Quick search..."
                className="w-full h-9 pl-9 pr-4 rounded-md border border-input bg-transparent text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                disabled
              />
            </div>
          )}

          <ThemeToggle />

          {isAuthenticated ? (
            <div className="flex items-center gap-3 relative">
              {/* Notification icon */}
              <button className="relative p-2 rounded-full hover:bg-muted transition-colors animate-in" aria-label="Notifications">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive animate-pulse" />
                )}
              </button>

              {/* Profile Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  onBlur={() => setTimeout(() => setProfileOpen(false), 200)}
                  className="flex items-center gap-2 p-1 rounded-full hover:bg-muted transition-colors border text-left"
                  aria-label="User profile dropdown"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  <ChevronDown className="h-4 w-4 text-muted-foreground pr-1 hidden sm:block" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-md border bg-popover p-2 text-popover-foreground shadow-md animate-in fade-in-0 slide-in-from-top-1 z-50">
                    <div className="px-2 py-1.5 border-b mb-1">
                      <p className="text-sm font-semibold truncate">{user?.fullName}</p>
                      <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                      <div className="mt-1 flex items-center gap-1.5">
                        <Shield className="h-3 w-3 text-primary" />
                        <Badge variant="secondary" className="text-[9px] uppercase px-1 py-0 h-auto">
                          {user?.role}
                        </Badge>
                      </div>
                    </div>
                    <Link
                      href="/dashboard/settings"
                      className="flex items-center gap-2 px-2 py-1.5 text-sm rounded hover:bg-muted transition-colors w-full"
                    >
                      <User className="h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                    <button
                      onClick={logout}
                      className="flex items-center gap-2 px-2 py-1.5 text-sm rounded hover:bg-destructive/10 text-destructive transition-colors w-full text-left mt-1 border-t pt-2"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors shadow-sm"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
