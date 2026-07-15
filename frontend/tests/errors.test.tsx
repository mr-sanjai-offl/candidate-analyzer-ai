import * as React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  ErrorFallback,
  ApiError,
  NetworkError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError,
  InternalServerError,
} from '../src/components/errors'

describe('Error Components Render Integrity', () => {
  it('should render generic ErrorFallback correctly', () => {
    render(<ErrorFallback error={new Error('Custom Fallback Error')} />)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Custom Fallback Error')).toBeInTheDocument()
  })

  it('should render ApiError message', () => {
    render(<ApiError message="Target API Host Offline" />)
    expect(screen.getByText('API Error')).toBeInTheDocument()
    expect(screen.getByText('Target API Host Offline')).toBeInTheDocument()
  })

  it('should render NetworkError', () => {
    render(<NetworkError />)
    expect(screen.getByText('No Internet Connection')).toBeInTheDocument()
  })

  it('should render UnauthorizedError', () => {
    render(<UnauthorizedError />)
    expect(screen.getByText('Unauthorized')).toBeInTheDocument()
  })

  it('should render ForbiddenError', () => {
    render(<ForbiddenError />)
    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  it('should render NotFoundError', () => {
    render(<NotFoundError />)
    expect(screen.getByText('Page Not Found')).toBeInTheDocument()
  })

  it('should render InternalServerError', () => {
    render(<InternalServerError />)
    expect(screen.getByText('Internal Server Error')).toBeInTheDocument()
  })
})
