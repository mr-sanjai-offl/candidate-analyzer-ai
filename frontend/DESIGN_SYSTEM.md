# ApexGuidance AI — Design System & UI Component Library

This design system is implemented with Next.js 15, React 19, Tailwind CSS v4, Radix UI Primitives, Framer Motion, and Recharts.

---

## Folder Organization

All reusable UI components are organized under `src/components/ui/`:
```
src/components/ui/
├── animations.tsx         # Framer Motion transitions (Fade, SlideUp, ScaleIn, StaggerList, PageTransition, HoverScale)
├── button.tsx             # Button, IconButton, LoadingButton
├── input.tsx              # Input (text, search, validation, adornments), Textarea
├── form.tsx               # FormWrapper (RHF + Zod integration), FormField, FormSectionHeader
├── card.tsx               # Card, CardHeader, CardTitle, CardContent, CardFooter, StatCard
├── dialog.tsx             # Dialog (Modal), AlertDialog (Confirm, Delete dialogs)
├── select.tsx             # Select trigger, SelectContent, SelectItem dropdown list
├── checkbox.tsx           # Checkbox control wrapper
├── switch.tsx             # Switch toggle wrapper
├── alert.tsx              # Alert banner layout wrapper and variants
├── skeleton.tsx           # Skeleton loading state item
├── data-table.tsx         # Sorting, filtering, pagination, visible columns toggle, select-all
├── file-upload.tsx        # Drag & drop upload wrapper + simulation state indicators
├── charts.tsx             # Recharts wrappers (Radar, Bar, Pie)
├── knowledge-graph.tsx    # React Flow graphs mapping skill nodes and evidence items
├── chat.tsx               # ChatWindow loaded with user avatars, message actions, typing status
├── loading.tsx            # Spinner, CircularProgress, LoadingCard/Table/Chart/Dashboard
├── empty-states.tsx       # NoData, NoResults, NoInternet, UploadEmpty, SearchEmpty, PermissionDenied, ServerError, Maintenance
├── primitives.tsx         # Badge, Tabs, Tooltip, Progress, Avatar, Separator, Label
├── layout-primitives.tsx  # Breadcrumb, PageHeader, Section, StatsGrid, Toolbar, Stepper
├── sheet.tsx              # Sheet slide-out panels (left/right drawers)
└── index.ts               # Barrel export file
```

---

## Design Token Strategy

Tailwind v4 tokens are configured using HSL CSS variables inside `globals.css`, supporting automatic light & dark mode syncing:
- `--primary`: Main action color (sleek blue/indigo)
- `--secondary`: Accent and muted backgrounds
- `--background`: Base body background
- `--foreground`: Text contrast
- `--card`: Content surfaces
- `--muted`: Inactive tabs/borders
- `--destructive`: Error highlights
- `--radius`: Reusable border curvature (defaults to `0.5rem`)

---

## Accessibility Compliance Summary (WCAG AA)

- **Keyboard Traversal**: Full tab index traversal supported across buttons, select panels, checkbox toggles, and drawers.
- **Focus Rings**: Visual focus borders (`focus-visible:ring-2`) wrap interactive elements when navigated via keyboard.
- **ARIA Descriptors**: Dynamic `aria-invalid`, `aria-describedby` error states, and `role="alert"` tags are attached to inputs and wrappers.
- **Contrast Ratios**: Custom text configurations map to standard HSL values verifying full readable contrast in light and dark modes.
- **Reduced Motion**: Motion transitions auto-adjust (`prefers-reduced-motion`) to safe zero-duration variants.

---

## Component Showcase Guide

To inspect components in action, navigate to `/components-preview` in dev mode. It provides preview blocks, customizable sliders, and live interactive examples for every component in the system.
