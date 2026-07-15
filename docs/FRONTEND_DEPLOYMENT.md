# Frontend Deployment Guide

This document describes how to deploy the ApexGuidance AI React/Next.js frontend to production environments.

## 1. Multi-Stage Docker Builds

For production environments, utilize the multi-stage Docker orchestration setup.

```dockerfile
# Stage 1: Build workspace deps
FROM node:20-alpine AS base
WORKDIR /app
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Stage 2: Production compile
FROM base AS builder
WORKDIR /app
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
RUN pnpm run build

# Stage 3: Production runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN npm install -g pnpm
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["pnpm", "start"]
```

## 2. Static CDN Hosting (SSG/Vercel)

The Next.js configuration is optimized for server-less deployment targets like Vercel or AWS Amplify.

1. **Vercel Integration**: Import the repository and select the Next.js framework preset.
2. **Environment Configuration**: Set up environment variables matching `.env.example`.
3. **Build Command**: `pnpm run build`
