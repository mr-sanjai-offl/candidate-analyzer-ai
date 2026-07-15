# Performance Optimization Guide

This document describes frontend speed, caching, and layout bundle optimizations implemented across the application.

## 1. Dynamic Code Splitting & Suspense

Heavy client-side dashboard panels are split and resolved dynamically using Next.js imports:

```tsx
import dynamic from 'next/dynamic'

const HeavyChartComponent = dynamic(() => import('@/components/ui/HeavyChart'), {
  loading: () => <Skeleton className="h-64 w-full" />,
  ssr: false, // Prevents server hydration issues
})
```

## 2. Server State vs UI State Separation

- **Server Cache (React Query)**: Handles all backend resource caches, auto-invalidations, refetch loops, and network retries.
- **UI State Store (Zustand)**: Confined to light, local interactive operations (e.g. sidebar toggle status, navigation theme preferences).

## 3. Font and Image Optimizations

- **Next.js Fonts (`next/font`)**: Automatically packages Geist Sans and Geist Mono subsets into optimized self-hosted static font bundles.
- **Next.js Images (`next/image`)**: Assets are formatted automatically to WebP, respecting sizes arrays to avoid layout shifts (CLS).
