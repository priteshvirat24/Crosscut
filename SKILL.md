---
name: Crosscut CI Optimizer
description: A GitLab Duo Agent Platform Flow that uses GitLab Orbit's cross-repository call graph to automatically discover impacted tests and optimize CI pipelines.
version: 1.0.0
capabilities:
  - Read GitLab Orbit Remote
  - Analyze Merge Request Diffs
  - Trigger Target Child Pipelines
  - Add Merge Request Comments
---

# Crosscut CI Optimizer (AI Catalog Package)

Crosscut is an intelligent CI optimization skill powered by GitLab Orbit and executed by the GitLab Duo Agent Platform. 

## 1. Triggers
The Crosscut Flow is initiated by the following GitLab events:
- `merge_request_opened`
- `merge_request_updated`

## 2. Inputs
The Duo Agent Platform injects the following context into the flow:
- `mr_diff`: The raw diff of the active Merge Request.
- `source_branch`: The branch containing the changes.
- `project_id`: The ID of the repository where the MR originated.

## 3. Outputs
The Flow produces the following automated actions:
- **Targeted CI Execution**: Generates and triggers a downstream child pipeline containing ONLY the tests impacted by the diff.
- **MR Comment**: Posts an automated summary to the MR detailing the exact tests selected and the CI minutes saved.

## 4. Flow Architecture Diagram

```mermaid
graph TD
    A[GitLab Event: MR Opened] --> B[Diff Analysis]
    B --> C[Orbit Traversal]
    C --> D[Dependency Discovery]
    D --> E[Impacted Test Discovery]
    E --> F[Test Selection]
    F --> G[Pipeline Generation]
    G --> H[MR Comment Publication]
    H --> I[Output: Targeted CI Execution]
    
    style A fill:#fc6d26,stroke:#e24329,stroke-width:2px,color:#fff
    style C fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff
    style F fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style I fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
```

## 5. Capabilities & Orbit Usage
This flow relies fundamentally on **GitLab Orbit**. Without Orbit's cross-repository call graph, the agent would be restricted to guessing impact via regex or outdated coverage reports. By querying Orbit, the agent achieves 100% precision in test selection across microservice boundaries.
