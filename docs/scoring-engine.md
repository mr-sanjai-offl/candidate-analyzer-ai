# Scoring Engine

## Overview

The Capability Scoring Engine is a **fully deterministic** scoring system that evaluates candidates across 20 technical categories using weighted evidence from multiple platform sources. No LLM or AI models are used — every score is a mathematical formula with a full explanation.

## Scoring Categories (20)

1. Programming Languages
2. Frameworks
3. Libraries
4. Databases
5. Cloud
6. DevOps
7. Security
8. Networking
9. AI
10. Machine Learning
11. Data Structures
12. Algorithms
13. Problem Solving
14. Projects
15. Open Source
16. Architecture
17. Testing
18. Leadership
19. Consistency
20. Learning Speed

## Four Score Metrics per Category

| Metric | Formula Basis | Range |
|--------|--------------|-------|
| **Confidence Score** | Average evidence confidence + source diversity boost (7.5 per unique source) | 0–100 |
| **Experience Score** | `15 + 35 × log₂(total_weight + 1)` | 0–100 |
| **Depth Score** | `avg_weight × 70 + (30 if VERIFIED else 10)` | 0–100 |
| **Breadth Score** | `unique_skills_in_category × 20` | 0–100 |

## Proficiency Level Assignment

```
overall_average = (confidence + experience + depth + breadth) / 4

≥ 80  → EXPERT
≥ 55  → ADVANCED
≥ 30  → INTERMEDIATE
< 30  → BEGINNER
```

## Evidence Weighting Formula

```
Python Example:
  Resume claim      → weight=0.2, confidence=60   (10% contribution)
  GitHub primary     → weight=0.8, confidence=95   (40% contribution)
  Project usage      → weight=0.6, confidence=85   (25% contribution)
  Commit evidence    → weight=0.5, confidence=80   (10% contribution)
  LeetCode tags      → weight=0.4, confidence=70   (10% contribution)
  Certifications     → weight=0.3, confidence=65   (5% contribution)
```

## Special Category Overrides

Some categories use platform-specific formulas instead of generic evidence aggregation:

| Category | Special Logic |
|----------|--------------|
| **Open Source** | `log₂(public_repos)` + `log₃(stars)` + `log₂(followers)` |
| **Consistency** | Weighted average of GitHub commit consistency, LeetCode activity, and Codeforces contest participation |
| **Learning Speed** | Platform count bonus + solve velocity: `min(50, problems_solved / 5)` |
| **Projects** | `log₂(project_count)` + `log₂(total_stars)` |
| **Leadership** | Resume keyword scanning for "lead", "manager", "mentor" + `log₂(followers)` |

## Explanation Structure

Every score includes a structured explanation:

```json
{
  "summary": "Proficiency evaluated as ADVANCED based on 5 pieces of evidence from: GITHUB, RESUME.",
  "details": [
    "Confidence Score of 89.5% derived from source trust levels and variety.",
    "Experience Score of 72.3% calculated using log weights of verified occurrences."
  ],
  "factors": {
    "evidence_count": 5,
    "unique_skills_count": 3,
    "verification_ratio": 0.8
  }
}
```

## Readiness Assessment

The Readiness Engine evaluates candidates against 9 standard engineering roles:

| Role | Required Skills |
|------|----------------|
| Backend | Python, Java, Go, FastAPI, PostgreSQL, Redis |
| Frontend | JavaScript, TypeScript, React, Angular, Vue |
| Full Stack | JS, TS, React, Python, Node.js, PostgreSQL |
| AI Engineer | Python, TensorFlow, PyTorch, NumPy, Pandas |
| Data Engineer | Python, PostgreSQL, MongoDB, Spark, Hadoop |
| DevOps | Docker, Kubernetes, Git, Jenkins, Terraform |
| Cloud | AWS, GCP, Azure, Kubernetes, Docker |
| Cybersecurity | Linux, Bash, Wireshark, Security, Networking |
| Embedded | C++, C, Assembly, Microcontrollers, Linux |

Formula: `role_score = (avg_category_score × 0.6) + (skill_match_ratio × 40)`

## Gap Analysis

Outputs:
- **Missing Skills**: Required by target role but absent from candidate profile
- **Weak Skills**: Present but with low evidence weight (< 0.7)
- **Strong Skills**: Present with high evidence weight (≥ 0.7)
- **Learning Priority**: Missing skills first, then weak skills
- **Recommended Projects**: Tailored project templates for skill improvement

## Key Files

| File | Purpose |
|------|---------|
| `app/scoring/scoring_engine.py` | Core scoring formulas and category calculations |
| `app/scoring/readiness_engine.py` | Role-specific readiness assessment |
| `app/scoring/gap_analysis_engine.py` | Gap detection and project recommendations |
| `app/services/capability_scoring_service.py` | Service coordinating DB persistence |
| `app/services/readiness_service.py` | Readiness report persistence |
| `app/services/gap_analysis_service.py` | Gap analysis persistence |
| `app/database/models/capability_score.py` | CapabilityScore database model |
| `app/database/models/readiness_report.py` | ReadinessReport database model |
