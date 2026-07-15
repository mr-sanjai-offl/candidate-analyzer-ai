import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: unknown
  ) {
    super(message)
    this.name = 'APIError'
  }
}

export class UnauthorizedError extends APIError {
  constructor(message = 'Unauthorized access') {
    super(message, 401, 'UNAUTHORIZED')
    this.name = 'UnauthorizedError'
  }
}

export class ForbiddenError extends APIError {
  constructor(message = 'Forbidden access') {
    super(message, 403, 'FORBIDDEN')
    this.name = 'ForbiddenError'
  }
}

export class NotFoundError extends APIError {
  constructor(message = 'Resource not found') {
    super(message, 404, 'NOT_FOUND')
    this.name = 'NotFoundError'
  }
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor: Attach JWT Bearer Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

interface ErrorDetail {
  detail?: string
  message?: string
  code?: string
}

// Response Interceptor: Auto Refresh JWT & Mapping Errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (!error.response) {
      return Promise.reject(new APIError('Network error or server unreachable', 0, 'NETWORK_ERROR'))
    }

    const { status, data } = error.response
    const responseData = data as ErrorDetail

    // Handle 401 Unauthorized - attempt Token Refresh
    if (status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login')) {
        useAuthStore.getState().clearSession()
        return Promise.reject(new UnauthorizedError(responseData?.detail || 'Session expired'))
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return apiClient(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const { refreshToken } = useAuthStore.getState()
        if (!refreshToken) {
          throw new UnauthorizedError('No refresh token available')
        }

        // Call the absolute path endpoint directly
        const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = refreshResponse.data
        useAuthStore.setState({
          accessToken: access_token,
          refreshToken: refresh_token,
        })

        isRefreshing = false
        processQueue(null, access_token)

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        isRefreshing = false
        processQueue(refreshError, null)
        useAuthStore.getState().clearSession()
        return Promise.reject(new UnauthorizedError('Session validation failed. Please login again.'))
      }
    }

    // Map other HTTP errors
    const errorMessage = responseData?.detail || responseData?.message || error.message
    if (status === 403) {
      return Promise.reject(new ForbiddenError(errorMessage))
    }
    if (status === 404) {
      return Promise.reject(new NotFoundError(errorMessage))
    }

    return Promise.reject(new APIError(errorMessage, status, responseData?.code || 'UNKNOWN_ERROR', responseData))
  }
)
