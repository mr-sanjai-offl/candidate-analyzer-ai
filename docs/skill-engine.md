# Skill Extraction Engine

## Overview

The Skill Extraction Engine is a **fully deterministic**, rule-based system that identifies technical skills from multiple candidate data sources without using any LLM or AI model. It operates via keyword matching, regex scanning, and alias normalization.

## Architecture

```
Resume JSON ──┐
GitHub Profile ──┤
LeetCode Profile ──┤──→ SkillExtractionEngine ──→ UnifiedSkillGraph
Codeforces Profile ──┘        │
                              ├── Alias Normalization
                              ├── Category Resolution
                              └── Evidence Attribution
```

## Input Sources

| Source | Data Extracted |
|--------|---------------|
| **Resume JSON** | `skills[]` array, `work_experience[].description` keyword scanning |
| **GitHub Profile** | `primary_language`, `skills[]`, `projects[].languages`, `projects[].topics` |
| **LeetCode Profile** | `problems_solved`, `topic_distribution` tag counts |
| **Codeforces Profile** | `rating`, `rank`, `topic_distribution` tag counts |

## Extraction Categories

The engine extracts skills across 21 categories:

- Programming Languages, Frameworks, Libraries, Databases
- Cloud Platforms, DevOps, Containers, Operating Systems
- Networking, Cybersecurity, AI/ML, Embedded Systems
- Mobile, Frontend, Backend, Testing, CI/CD
- Architecture, System Design, Soft Skills, Certifications

## Alias Normalization

All extracted skills are normalized through a deterministic alias map:

| Input Variants | Standard Name |
|----------------|--------------|
| `FastAPI`, `Flask`, `Django` | `Python Backend` |
| `C++`, `CPP`, `c++17` | `C++` |
| `JS`, `JavaScript`, `NodeJS`, `Node.js` | `Node.js` |
| `Docker Compose`, `Docker` | `Docker` |

## Evidence Model

Every extracted skill carries evidence metadata:

```python
{
    "source": "GITHUB",          # RESUME | GITHUB | LEETCODE | CODEFORCES | PROJECT | COMMIT
    "weight": 0.8,               # Relevance weight (0.0 – 1.0)
    "confidence": 95,            # Confidence percentage (0 – 100)
    "evidence": "Primary language on GitHub",
    "timestamp": "2026-07-15T...",
    "verification_state": "VERIFIED",  # CLAIMED (resume) or VERIFIED (platform)
}
```

## Evidence Weights by Source

| Source | Default Weight | Confidence Range |
|--------|---------------|-----------------|
| Resume Skills List | 0.2 – 0.3 | 60 – 70 |
| Resume Work Experience | 0.4 | 75 |
| GitHub Primary Language | 0.8 | 95 |
| GitHub Repository Languages | 0.5 – 0.6 | 80 – 85 |
| GitHub Topics | 0.4 | 70 |
| LeetCode Problem Tags | scaled by count | 50 – 100 |
| Codeforces Problem Tags | scaled by count | 60 – 100 |

## Key Files

| File | Purpose |
|------|---------|
| `app/scoring/skill_engine.py` | Core extraction engine with alias maps |
| `app/services/skill_extraction_service.py` | Service layer coordinating DB persistence |
| `app/database/models/evidence.py` | Evidence database model |
| `app/database/models/aliases.py` | SkillAlias and TechnologyAlias models |
