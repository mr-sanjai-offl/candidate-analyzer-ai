/**
 * React Query hooks for all recruiter-facing API operations.
 *
 * Covers search, job matching, report generation, and exports.
 */

import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ── Keys ────────────────────────────────────────────────────────────────────────
export const recruiterKeys = {
  search: (params: Record<string, unknown>) => ['recruiter-search', params] as const,
  jobMatch: (candidateId: string) => ['job-match', candidateId] as const,
}

// ── Search Hook ─────────────────────────────────────────────────────────────────

export interface SearchParams {
  skills?: string[]
  min_readiness?: number
  role?: string
  min_capability_score?: number
}

export function useRecruiterSearch(params: SearchParams, enabled = true) {
  return useQuery({
    queryKey: recruiterKeys.search(params as Record<string, unknown>),
    queryFn: async () => {
      const { data } = await apiClient.get('/search', { params })
      return data
    },
    enabled,
  })
}

// ── Job Matching Hook ───────────────────────────────────────────────────────────

export function useJobMatching() {
  return useMutation({
    mutationFn: async (params: {
      candidateId: string
      jobTitle: string
      jobDescription: string
    }) => {
      const { data } = await apiClient.post('/jobs/match', {
        candidate_id: params.candidateId,
        job_title: params.jobTitle,
        job_description: params.jobDescription,
      })
      return data
    },
  })
}

// ── Report Generation Hooks ─────────────────────────────────────────────────────

export function useGenerateRecruiterReport() {
  return useMutation({
    mutationFn: async (params: { candidateId: string; analysisId: string }) => {
      const { data } = await apiClient.post('/reports/recruiter', {
        candidate_id: params.candidateId,
        analysis_id: params.analysisId,
      })
      return data
    },
  })
}

// ── Export Hook ──────────────────────────────────────────────────────────────────

export function useRecruiterExport() {
  return useMutation({
    mutationFn: async (params: { analysisId: string; format: 'json' | 'csv' | 'pdf' | 'docx' }) => {
      const { data } = await apiClient.get(`/exports/${params.analysisId}`, {
        params: { format: params.format },
        responseType: 'blob',
      })
      return data
    },
  })
}
