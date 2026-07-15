# ApexGuidance AI — Frontend Architecture Master Prompt

You are acting as a Principal Frontend Architect, Senior React Engineer, Senior Next.js Engineer, UI/UX Designer, TypeScript Expert, Accessibility Specialist, Performance Engineer, and Code Reviewer.

Your task is to build the **entire production-grade frontend** for ApexGuidance AI.

This frontend must integrate with the already completed production backend.

---

# IMPORTANT

Before generating ANY code:

Read the backend OpenAPI documentation.

Understand every API endpoint.

Do NOT create fake backend logic.

Do NOT duplicate backend business logic.

The frontend is only responsible for:

* UI
* UX
* State Management
* API Communication
* Data Visualization
* Authentication Flow
* File Upload
* Real-time Updates

Never perform business logic on the client.

All intelligence belongs to the backend.

---

# Technology Stack

Use ONLY

* Next.js 15 (App Router)
* React 19
* TypeScript
* Tailwind CSS
* shadcn/ui
* TanStack Query
* Zustand
* React Hook Form
* Zod
* Axios
* Framer Motion
* Recharts
* React Flow (Knowledge Graph)
* Lucide Icons
* Sonner
* next-themes
* ESLint
* Prettier

Package manager

pnpm

---

# Folder Structure

Create a scalable enterprise architecture.

Example

app/

components/

features/

hooks/

lib/

providers/

services/

types/

schemas/

store/

utils/

constants/

styles/

public/

tests/

---

# Design System

Build a complete reusable design system.

Create reusable

Buttons

Inputs

Select

Textarea

Dropdown

Modal

Drawer

Sidebar

Navbar

Breadcrumb

Table

Data Grid

Cards

Badges

Avatar

Pagination

Tabs

Tooltip

Progress

Charts

Timeline

Skeleton

Loading states

Error states

Empty states

Command Palette

Theme Switcher

Notifications

Everything must use shadcn/ui.

Never duplicate components.

---

# Authentication

Implement

Login

Register

Forgot Password

Reset Password

Refresh Token

Session Persistence

Protected Routes

Role-based UI

Roles

Admin

Recruiter

Candidate

---

# Layouts

Create

Landing Layout

Dashboard Layout

Authentication Layout

Admin Layout

Recruiter Layout

Candidate Layout

Responsive Sidebar

Responsive Navbar

Mobile Navigation

---

# Landing Page

Professional SaaS landing page.

Sections

Hero

Features

Architecture

How It Works

Screenshots

Testimonials (placeholder)

Pricing (placeholder)

FAQ

Footer

Animations

Responsive

SEO optimized

---

# Dashboard

Create dashboard with

Statistics Cards

Recent Analyses

Background Jobs

Notifications

Activity Timeline

Quick Actions

Usage Analytics

Token Usage

---

# Candidate Pages

Candidate Profile

Resume Upload

Platform Linking

GitHub

LeetCode

Codeforces

Analysis Progress

Skill Graph

Capability Scores

Readiness Dashboard

Gap Analysis

AI Feedback

Job Matching

Interview Questions

Chat Assistant

Export Reports

Settings

---

# Recruiter Pages

Recruiter Dashboard

Candidate Search

Candidate Comparison

Candidate Profile

Reports

Job Matching

Interview Generator

Analytics

Saved Searches

Export

---

# Admin Pages

User Management

Prompt Templates

Prompt Versions

Model Configuration

Analytics

Logs

Background Jobs

Token Usage

Health Monitoring

Settings

---

# API Layer

Create

Axios Client

Authentication Interceptor

Refresh Token Logic

Retry Logic

Error Handling

API Hooks

Query Keys

Mutation Hooks

Never call Axios directly from components.

---

# State Management

Use Zustand ONLY for

Theme

User

UI State

Notifications

Preferences

Use TanStack Query for

Server State

Caching

Invalidation

Background Refetch

Pagination

Infinite Queries

Optimistic Updates

---

# Forms

Use

React Hook Form

Zod

Client Validation

Server Validation

Field Errors

Loading

Success

Reset

---

# File Upload

Implement

Drag and Drop

Progress Bar

Resume Preview

Validation

Retry

Cancel Upload

Multiple Uploads

---

# Background Jobs

Create

Job Queue UI

Progress

Status

Logs

Retry

Cancel

Polling

Real-time updates

---

# Charts

Use Recharts

Capability Radar

Readiness Bar Chart

Skill Distribution

Language Distribution

Contribution Timeline

Problem Solving Statistics

Technology Usage

Analytics Dashboard

---

# Knowledge Graph

Use React Flow

Display

Skills

Projects

Evidence

Relationships

Interactive nodes

Zoom

Mini Map

Filters

Search

---

# AI Chat

Build

Conversation List

Chat Window

Markdown Rendering

Code Blocks

Streaming Responses

Typing Indicator

Evidence References

Suggested Questions

---

# Search

Global Search

Candidate Search

Filters

Sorting

Pagination

Saved Filters

Advanced Search

---

# Reports

Display recruiter reports beautifully.

Support

PDF Preview

JSON Viewer

Markdown Viewer

Export Buttons

Evidence Panels

Confidence Indicators

---

# Notifications

Toast

Inbox

Unread Count

Email Status

Background Job Alerts

---

# Accessibility

WCAG AA

Keyboard Navigation

Focus Management

ARIA Labels

Screen Reader Support

---

# Responsive Design

Desktop

Tablet

Mobile

No broken layouts.

---

# Performance

Lazy Loading

Dynamic Imports

Code Splitting

Image Optimization

Memoization

Virtualization

Prefetching

Suspense

Streaming

---

# Security

Sanitize Markdown

XSS Protection

CSRF Ready

Token Refresh

Secure Storage

Input Validation

---

# Testing

Write

Unit Tests

Component Tests

Integration Tests

Accessibility Tests

Coverage >90%

---

# Documentation

Generate

Frontend Architecture

Component Documentation

Folder Structure

Design System Guide

API Integration Guide

Developer Setup

Deployment Guide

---

# Deliverables

1. Complete frontend architecture

2. All reusable components

3. All pages

4. API integration

5. Authentication flow

6. Dashboard

7. Responsive design

8. Charts

9. Knowledge graph

10. AI chat

11. Testing

12. Documentation

Do not generate placeholder implementations where a real implementation is possible.

Produce production-quality, modular, maintainable code following enterprise best practices.
