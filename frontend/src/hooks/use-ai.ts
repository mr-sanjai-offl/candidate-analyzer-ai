import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export const aiKeys = {
  chat: (sessionId?: string) => ['chat', sessionId] as const,
  match: (candidateId?: string) => ['match', candidateId] as const,
}

// ── Chat Hooks ──────────────────────────────────────────────────────────────────

export function useChatMessage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (params: {
      candidateId: string
      sessionId?: string
      message: string
    }) => {
      const { data } = await apiClient.post('/chat/message', {
        candidate_id: params.candidateId,
        session_id: params.sessionId || null,
        message: params.message,
      })
      return data
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: aiKeys.chat(data.session_id) })
    },
  })
}

// ── Match Hooks ─────────────────────────────────────────────────────────────────

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

// ── Report Generator Hooks ──────────────────────────────────────────────────────

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
