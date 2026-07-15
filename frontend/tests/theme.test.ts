import { describe, it, expect, beforeEach } from 'vitest'
import { useThemeStore } from '../src/store/themeStore'

describe('useThemeStore', () => {
  beforeEach(() => {
    useThemeStore.setState({ theme: 'system' })
  })

  it('should have system theme as default', () => {
    const state = useThemeStore.getState()
    expect(state.theme).toBe('system')
  })

  it('should update theme correctly', () => {
    useThemeStore.getState().setTheme('dark')
    expect(useThemeStore.getState().theme).toBe('dark')
  })
})
