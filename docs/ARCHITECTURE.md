PART 1

Architecture Bible

### AI Engineering Capability Assessment Platform

Production-Grade Architecture Master Prompt — Foundation Section

### How to Use This Document

Save this file as docs/ARCHITECTURE.md in your repository.

At the beginning of every AI coding session, prepend:

AI Session Instruction

COPY THIS

Read and follow docs/ARCHITECTURE.md strictly.

Do not violate any architectural rule.

Implement only the requested phase.

Do not create code outside the defined structure.

This ensures all generated code follows the same architecture.

### 1. Product Vision

Product Name: ApexGuidance AI (working name)

Mission: Build an evidence-based AI platform that evaluates a software engineer's real technical capabilities using public coding platforms and project repositories.

### The platform must answer

Can this candidate contribute effectively to a production engineering team within 3 months?

### Primary Users

* Recruiters

* Engineering Managers

* Universities

* Training Institutes

* Software Engineering Candidates

### 2. Core Functional Requirements

### The backend must support

| Feature                        | Status   |
| ------------------------------ | -------- |
| Authentication & Authorization | Required |
| GitHub profile analysis        | Required |
| LeetCode profile analysis      | Required |
| Codeforces profile analysis    | Required |
| Resume upload & parsing        | Required |
| Skill extraction engine        | Required |
| Capability scoring engine      | Required |
| AI report generation           | Required |
| Recruiter dashboard APIs       | Required |
| Candidate dashboard APIs       | Required |
| Background job processing      | Required |
| Rate limiting                  | Required |
| Monitoring & logging           | Required |
| Docker deployment              | Required |
| CI/CD integration              | Required |

### 3. Non-Functional Requirements

### Performance

P95

API response

< 300 ms

Profile analysis

< 60 s

Report generation

< 15 s

Concurrent analyses

100+

### Security

MANDATORY

* JWT authentication

* BCrypt password hashing

* Rate limiting

* Input validation

* SQL injection protection

* Secrets via environment variables only

### Scalability

READY

* Stateless API servers

* Horizontal scaling ready

* Redis-backed job queue

* Async I/O everywhere possible

### Reliability

TARGET

* 99.5% uptime target

* Automatic retries

* Idempotent jobs

* Graceful failure handling

### 4. Official Tech Stack

| Layer            | Technology              |
| ---------------- | ----------------------- |
| Frontend         | Next.js 16 + TypeScript |
| Backend          | FastAPI                 |
| AI Agents        | LangGraph               |
| Database         | Supabase PostgreSQL     |
| Storage          | Supabase Storage        |
| Cache            | Redis                   |
| Background Jobs  | Celery                  |
| ORM              | SQLAlchemy 2.0          |
| Migrations       | Alembic                 |
| Validation       | Pydantic v2             |
| Containerization | Docker                  |
| Reverse Proxy    | Nginx                   |
| Monitoring       | Sentry                  |
| Analytics        | PostHog                 |
| CI/CD            | GitHub Actions          |
| AI Provider      | OpenRouter              |

### 5. Repository Structure (MANDATORY)

candidate-analyzer-ai/

├── backend/

│ ├── app/

│ │ ├── api/

│ │ │ ├── v1/

│ │ │ │ ├── auth.py

│ │ │ │ ├── candidates.py

│ │ │ │ ├── recruiters.py

│ │ │ │ ├── analysis.py

│ │ │ │ └── reports.py

│ │ ├── core/

│ │ │ ├── config.py

│ │ │ ├── security.py

│ │ │ ├── logging.py

│ │ │ └── exceptions.py

│ │ ├── database/

│ │ │ ├── session.py

│ │ │ ├── base.py

│ │ │ └── models/

│ │ ├── schemas/

│ │ ├── services/

│ │ ├── collectors/

│ │ │ ├── github/

│ │ │ ├── leetcode/

│ │ │ └── codeforces/

│ │ ├── agents/

│ │ ├── scoring/

│ │ ├── tasks/

│ │ └── utils/

│ ├── tests/

│ ├── alembic/

│ ├── requirements.txt

│ └── Dockerfile

├── frontend/

├── infrastructure/

├── docs/

├── .github/workflows/

└── docker-compose.yml

NEVER

create business logic inside API route files.

All business logic must live in services/, collectors/, agents/, or scoring/.

### 6. Git Workflow (MANDATORY)

### Branches

main

└── develop

├── feature/authentication

├── feature/github-collector

├── feature/leetcode-collector

├── feature/codeforces-collector

├── feature/skill-engine

├── feature/report-generator

└── feature/deployment

### Commit Convention

feat(auth): implement JWT authentication

feat(github): add repository analyzer

fix(collector): handle rate limit retry

refactor(scoring): simplify skill aggregation

### Push Policy

* Push after every completed feature.

* Never push broken tests.

* Never push secrets.

* Every push must pass linting.

### 7. Backend Coding Standards

### All code must follow

| Rule                 | Requirement                     |
| -------------------- | ------------------------------- |
| Python Version       | 3.12+                           |
| Type Hints           | Required everywhere             |
| Async Functions      | Use for all I/O operations      |
| Pydantic Models      | For all request/response bodies |
| Dependency Injection | FastAPI Depends()               |
| Logging              | Structured JSON logging         |
| Exceptions           | Custom exception classes        |
| Configuration        | Pydantic Settings only          |
| Secrets              | Environment variables only      |
| Database Access      | Through service layer           |

### Forbidden

* Hard-coded API keys

* Raw SQL in route handlers

* print() statements

* Global mutable state

* Synchronous HTTP requests

* Duplicate business logic

### 8. AI Agent Architecture

### Official Agent List

| Agent                  | Responsibility                       |
| ---------------------- | ------------------------------------ |
| GitHubAgent            | Analyze repositories & contributions |
| LeetCodeAgent          | Analyze DSA performance              |
| CodeforcesAgent        | Analyze competitive programming      |
| ResumeAgent            | Extract resume data                  |
| SkillExtractionAgent   | Build skill graph                    |
| CapabilityScoringAgent | Generate scores                      |
| ReportGenerationAgent  | Create recruiter report              |
| InterviewQuestionAgent | Generate targeted questions          |

### Agent Orchestration

Orchestrator

GitHub

LeetCode

Codeforces

Resume

Skill Graph

Capability Scoring

Recruiter Report

### 9. Database Design Principles

### Every table must have

* id UUID PRIMARY KEY

* created_at TIMESTAMPTZ

* updated_at TIMESTAMPTZ

* deleted_at TIMESTAMPTZ NULL (soft delete)

### Core Tables

| Table               | Purpose           |
| ------------------- | ----------------- |
| users               | Authentication    |
| candidate_profiles  | Candidate data    |
| github_profiles     | GitHub metrics    |
| leetcode_profiles   | DSA metrics       |
| codeforces_profiles | Contest metrics   |
| projects            | Analyzed projects |
| skills              | Extracted skills  |
| candidate_skills    | Skill mapping     |
| analysis_reports    | Final reports     |
| background_jobs     | Job tracking      |

### 10. Security Rules

CRITICAL

The AI must never generate:

* Exposed API keys

* Hard-coded secrets

* Weak JWT secrets

* Insecure password storage

* Open CORS policies in production

* Debug mode enabled in production

### Required

* BCrypt hashing

* JWT expiration

* Refresh token rotation

* Rate limiting per IP

* Request validation

* Audit logging

### 11. Testing Standards

### Minimum Coverage

| Component      | Coverage |
| -------------- | -------- |
| Services       | 90%      |
| Collectors     | 85%      |
| Scoring Engine | 95%      |
| API Routes     | 80%      |

### Required Tests

* Unit tests

* Integration tests

* API tests

* Background task tests

* Authentication tests

* Rate limit tests

### 12. Deployment Standards

### Every deployment must include

* Docker image build

* Health check endpoint

* Database migration execution

* Structured logging

* Sentry initialization

* Environment validation

* Graceful shutdown handling

### Health Endpoint

GET /api/v1/health

Response: 200 OK

{"status":"healthy","version":"1.0.0"}

### 13. AI Development Rules (MOST IMPORTANT)

### The AI must NEVER

HARD RULES

* Change the folder structure without explicit instruction.

* Add dependencies that are not approved in this document.

* Place business logic in route handlers.

* Create duplicate utility functions.

* Store secrets in code.

* Skip type hints.

* Skip error handling.

* Ignore existing architectural patterns.

* Generate incomplete database migrations.

* Use synchronous libraries for network I/O.

### The AI must ALWAYS

* Follow the repository structure exactly.

* Use Pydantic schemas.

* Use dependency injection.

* Write production-grade error handling.

* Add logging.

* Add docstrings.

* Write tests for new features.

* Update documentation.

* Generate clean commit messages.

* Keep functions small and focused.

### 14. Current Development Phase

START HERE

### Phase 1 — Project Foundation

IN PROGRESS

### The next AI coding prompt should implement only:

* FastAPI application setup

* Configuration management

* Logging system

* Database connection setup

* Docker configuration

* Health endpoint

* Basic project scaffolding

Do NOT implement authentication, collectors, AI agents, or scoring logic yet.

### Architecture Foundation Complete

You now have the first section of the Architecture Bible. Save it to docs/ARCHITECTURE.md and commit it.

Suggested commit

docs

feat(docs): add production architecture bible foundation

Includes product vision, tech stack, repository structure, coding standards, security rules, AI agent architecture, and development workflow.

Next step

Generate Phase 1 — Project Foundation Prompt that creates the initial FastAPI backend scaffold according to this architecture.
