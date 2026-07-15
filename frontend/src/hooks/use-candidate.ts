/**
 * React Query hooks for all candidate-facing API operations.
 *
 * Every hook wraps the Axios apiClient so components never call
 * Axios directly. Server state lives in React Query; Zustand is
 * only for UI state.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ── Keys ────────────────────────────────────────────────────────────────────────
export const candidateKeys = {
  resumes: ['resumes'] as const,
  resume: (id: string) => ['resume', id] as const,
  skills: (candidateId: string) => ['skills', candidateId] as const,
  scores: (candidateId: string) => ['scores', candidateId] as const,
  readiness: (candidateId: string) => ['readiness', candidateId] as const,
  gapAnalysis: (candidateId: string) => ['gap-analysis', candidateId] as const,
  syncStatus: (jobId: string) => ['sync-status', jobId] as const,
  analysis: (id: string) => ['analysis', id] as const,
  report: (analysisId: string) => ['report', analysisId] as const,
}

// ── Resume Hooks ────────────────────────────────────────────────────────────────

export function useResumes() {
  return useQuery({
    queryKey: candidateKeys.resumes,
    queryFn: async () => {
      const { data } = await apiClient.get('/files/')
      return data
    },
  })
}

export function useResume(id: string) {
  return useQuery({
    queryKey: candidateKeys.resume(id),
    queryFn: async () => {
      const { data } = await apiClient.get(`/files/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useUploadResume() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post('/files/upload-resume', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: candidateKeys.resumes }),
  })
}

export function useReplaceResume() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, file }: { id: string; file: File }) => {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post(`/files/${id}/replace`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: candidateKeys.resumes }),
  })
}

export function useDeleteResume() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/files/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: candidateKeys.resumes }),
  })
}

export function useResumeDownloadUrl(id: string) {
  return useQuery({
    queryKey: ['resume-download', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/files/${id}/download-url`)
      return data as { signed_url: string; expires_in_seconds: string }
    },
    enabled: !!id,
  })
}

// ── Platform Sync Hooks ─────────────────────────────────────────────────────────

export function usePlatformSync() {
  return useMutation({
    mutationFn: async (params: {
      platform: 'github' | 'leetcode' | 'codeforces'
      candidateId: string
      username: string
      force?: boolean
    }) => {
      const { data } = await apiClient.post(`/collect/${params.platform}`, {
        candidate_id: params.candidateId,
        username: params.username,
        force: params.force ?? false,
      })
      return data
    },
  })
}

export function useSyncAll() {
  return useMutation({
    mutationFn: async (params: {
      candidateId: string
      githubUsername?: string
      leetcodeUsername?: string
      codeforcesUsername?: string
      force?: boolean
    }) => {
      const { data } = await apiClient.post('/collect/all', {
        candidate_id: params.candidateId,
        github_username: params.githubUsername,
        leetcode_username: params.leetcodeUsername,
        codeforces_username: params.codeforcesUsername,
        force: params.force ?? false,
      })
      return data
    },
  })
}

export function useSyncStatus(jobId: string) {
  return useQuery({
    queryKey: candidateKeys.syncStatus(jobId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/collect/status/${jobId}`)
      return data
    },
    enabled: !!jobId,
    refetchInterval: 3000,
  })
}

export function usePlatformProfile(platform: 'github' | 'leetcode' | 'codeforces', username: string) {
  return useQuery({
    queryKey: ['platform-profile', platform, username],
    queryFn: async () => {
      const { data } = await apiClient.get(`/profile/${platform}/${username}`)
      return data
    },
    enabled: !!username,
  })
}

// ── Evaluation Hooks ────────────────────────────────────────────────────────────

export function useTriggerAnalysis() {
  return useMutation({
    mutationFn: async (candidateId: string) => {
      const { data } = await apiClient.post('/analyze/skills', {
        candidate_id: candidateId,
      })
      return data
    },
  })
}

export function useCandidateSkills(candidateId: string) {
  return useQuery({
    queryKey: candidateKeys.skills(candidateId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/skills/${candidateId}`)
      return data
    },
    enabled: !!candidateId,
  })
}

export function useCapabilityScores(candidateId: string) {
  return useQuery({
    queryKey: candidateKeys.scores(candidateId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/scores/${candidateId}`)
      return data
    },
    enabled: !!candidateId,
  })
}

export function useReadiness(candidateId: string) {
  return useQuery({
    queryKey: candidateKeys.readiness(candidateId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/readiness/${candidateId}`)
      return data
    },
    enabled: !!candidateId,
  })
}

export function useGapAnalysis(candidateId: string) {
  return useQuery({
    queryKey: candidateKeys.gapAnalysis(candidateId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/gap-analysis/${candidateId}`)
      return data
    },
    enabled: !!candidateId,
  })
}

// ── Analysis Hooks ──────────────────────────────────────────────────────────────

export function useAnalysis(id: string) {
  return useQuery({
    queryKey: candidateKeys.analysis(id),
    queryFn: async () => {
      const { data } = await apiClient.get(`/analysis/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useStartAnalysis() {
  return useMutation({
    mutationFn: async (candidateProfileId: string) => {
      const { data } = await apiClient.post('/analysis/start', {
        candidate_profile_id: candidateProfileId,
      })
      return data
    },
  })
}

// ── Reports Hooks ───────────────────────────────────────────────────────────────

export function useReport(analysisId: string) {
  return useQuery({
    queryKey: candidateKeys.report(analysisId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/reports/${analysisId}`)
      return data
    },
    enabled: !!analysisId,
  })
}

export function useGenerateCandidateFeedback() {
  return useMutation({
    mutationFn: async (params: { candidateId: string; analysisId: string }) => {
      const { data } = await apiClient.post('/reports/candidate', {
        candidate_id: params.candidateId,
        analysis_id: params.analysisId,
      })
      return data
    },
  })
}

// ── Export Hook ──────────────────────────────────────────────────────────────────

export function useExportReport() {
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
