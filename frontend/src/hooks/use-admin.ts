import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export const adminKeys = {
  health: ['system-health'] as const,
  jobs: (skip = 0, limit = 100) => ['admin-jobs', skip, limit] as const,
}

// ── System Health Hook ──────────────────────────────────────────────────────────

export function useSystemHealth() {
  return useQuery({
    queryKey: adminKeys.health,
    queryFn: async () => {
      const { data } = await apiClient.get('/health')
      return data as { status: string; version: string }
    },
    refetchInterval: 10000, // Poll health every 10 seconds
  })
}

// ── Background Jobs Hooks ───────────────────────────────────────────────────────

export function useAdminJobs(skip = 0, limit = 100) {
  return useQuery({
    queryKey: adminKeys.jobs(skip, limit),
    queryFn: async () => {
      const { data } = await apiClient.get('/jobs/', {
        params: { skip, limit },
      })
      return data
    },
  })
}

export function useDeleteAdminJob() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/jobs/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-jobs'] })
    },
  })
}
