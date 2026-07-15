# Frontend Environment Configuration Guide

This document details all supported environment variables required for compiling and running the Next.js workspace.

## 1. Environment File Load Order

Next.js automatically loads configurations from the following files in order:
1. `.env.development.local` / `.env.production.local`
2. `.env.local`
3. `.env.development` / `.env.production`
4. `.env`

## 2. Variables Catalog

| Key | Mode | Required | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Client | Yes | The URL target of the API v1 gateway endpoint |
| `NEXT_PUBLIC_ENABLE_DEBUG_LOGS` | Client | No | Controls debug logging outputs in development consoles |
| `NEXT_PUBLIC_SENTRY_DSN` | Client | No | Error tracking DSN reference |
| `NEXT_PUBLIC_POSTHOG_KEY` | Client | No | PostHog telemetry token |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Client | No | Google Analytics telemetry tag |

## 3. Strict Runtime Assertions

Client-side environment variables are prefixed with `NEXT_PUBLIC_` to be securely exposed to browser compilation runs.
