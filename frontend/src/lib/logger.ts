'use client'

type LogLevel = 'info' | 'warn' | 'error' | 'debug'

class FrontendLogger {
  private isProduction = process.env.NODE_ENV === 'production'

  private log(level: LogLevel, message: string, ...args: unknown[]) {
    if (this.isProduction && level === 'debug') {
      return
    }

    const timestamp = new Date().toISOString()
    const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`

    if (this.isProduction) {
      // In production, we only log warnings and errors to the console, or ship to a log aggregation service (like Sentry)
      if (level === 'error') {
        console.error(formattedMessage, ...args)
        // Placeholder for Sentry integration:
        // Sentry.captureMessage(message, { level: 'error', extra: { args } })
      } else if (level === 'warn') {
        console.warn(formattedMessage, ...args)
      }
    } else {
      // Development logging
      switch (level) {
        case 'info':
          console.info(formattedMessage, ...args)
          break
        case 'warn':
          console.warn(formattedMessage, ...args)
          break
        case 'error':
          console.error(formattedMessage, ...args)
          break
        case 'debug':
          console.debug(formattedMessage, ...args)
          break
      }
    }
  }

  info(message: string, ...args: unknown[]) {
    this.log('info', message, ...args)
  }

  warn(message: string, ...args: unknown[]) {
    this.log('warn', message, ...args)
  }

  error(message: string, ...args: unknown[]) {
    this.log('error', message, ...args)
  }

  debug(message: string, ...args: unknown[]) {
    this.log('debug', message, ...args)
  }
}

export const logger = new FrontendLogger()
