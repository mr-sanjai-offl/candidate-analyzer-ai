import * as React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from '../src/components/ui/button'
import { Input } from '../src/components/ui/input'
import { Card, CardTitle } from '../src/components/ui/card'

describe('Button Component', () => {
  it('should render children successfully', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('should support loading state by showing a spinner and disabling click', () => {
    render(<Button loading>Click me</Button>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })
})

describe('Input Component', () => {
  it('should render label and placeholder text', () => {
    render(<Input label="Username" placeholder="Enter username" />)
    expect(screen.getByText('Username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter username')).toBeInTheDocument()
  })

  it('should render error message in alert role', () => {
    render(<Input error="Must be valid" />)
    expect(screen.getByRole('alert')).toHaveTextContent('Must be valid')
  })
})

describe('Card Component', () => {
  it('should render card title hierarchy wrapper', () => {
    render(
      <Card>
        <CardTitle>Profile Card</CardTitle>
      </Card>
    )
    expect(screen.getByText('Profile Card')).toBeInTheDocument()
  })
})
