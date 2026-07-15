# Security Implementation Guide

This document describes the client-side security architecture implemented in the application frontend.

## 1. Content Security Policy & Security Headers

Next.js security headers are strictly enforced via the root configuration layer to mitigate XSS and Clickjacking risks:

- **CSP (Content-Security-Policy)**: RESTRICTS script execution to self domains. Restricts connection scopes specifically to localhost APIs and verified platforms (Github, LeetCode, Codeforces).
- **X-Frame-Options**: `DENY` prohibits frame-ancestors nesting, eliminating UI redressing risks.
- **X-Content-Type-Options**: `nosniff` prevents MIME type sniffing exploits.
- **Strict-Transport-Security (HSTS)**: Redirects all browser communication to SSL/TLS connections for a duration of one year.

## 2. JWT Rotation & Authentication Guards

- **HTTP Interceptors**: The Axios network client automatically watches response codes. When access tokens expire, a refresh cycle is triggered silently using the backend's session rotation endpoint.
- **Role-Based Guards**: Routes are securely wrapped using `<ProtectedRoute allowedRoles={['ADMIN']}>` triggers. Claim checks occur client-side inside secure providers, and user context verification happens at the API gateway layer.
