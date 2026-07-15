# Frontend Folder Structure Guide

```
frontend/
├── src/
│   ├── app/                      (Next.js App Router root layout and pages)
│   │   ├── (app)/                (General views, components previews)
│   │   ├── (auth)/               (Auth modules: login, registration)
│   │   ├── (dashboard)/          (Dashboard views and specific segment workspaces)
│   │   └── unauthorized/         (Access denied layout fallback)
│   ├── components/
│   │   ├── errors/               (Retry controls and global error screens)
│   │   ├── layout/               (Sidebar, navbar, layouts)
│   │   └── ui/                   (Tailwind theme primitives, loaders)
│   ├── hooks/                    (React Query hooks wrapping API clients)
│   ├── lib/                      (Axios client instances, analytic trackers)
│   ├── providers/                (Composition wrappers: Auth, Theme, React-Query)
│   └── store/                    (Zustand stores for theme, navigation states)
└── tests/                        (Unit and routing layout test collections)
```
