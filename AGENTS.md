# Crosscut

**Tagline:** Run only the tests that matter.

## Mission

Use GitLab Orbit's call graph to automatically determine the smallest set of tests impacted by a code change and execute only those tests.

The system should reduce CI time, compute costs, and developer feedback latency.

## Core Problem

Organizations run hundreds or thousands of tests for every merge request because they do not know which tests are actually affected by a change. Small code changes trigger large CI workloads. Shared libraries multiply this cost across repositories. Developers wait longer. Companies spend more. CI infrastructure scales unnecessarily.

## Why Orbit Is Essential

Crosscut must demonstrate a capability that is difficult or impossible without Orbit.

The key differentiator: Orbit provides a structured cross-repository call graph.

Crosscut uses Orbit to:
1. Identify changed symbols from a merge request.
2. Traverse incoming call relationships.
3. Find transitive callers.
4. Discover impacted test files.
5. Generate a minimal execution set.

Traditional approaches rely on coverage reports, grep, build systems, or language-specific tooling. Crosscut relies on Orbit's graph intelligence.

## Product Flow

Merge Request Opened → Diff Analysis → Changed Symbol Extraction → Orbit Graph Query → Impacted Test Discovery → Test Selection Engine → Targeted Pipeline Generation → Test Execution → Result Analysis → MR Comment Generation

## Core Agents

1. **Diff Analyzer**: Parse MR diff, extract changed functions/classes/files.
2. **Orbit Traversal Agent**: Query Orbit graph, find transitive callers, cross-repository traversal.
3. **Test Selection Agent**: Discover impacted tests, eliminate irrelevant tests, calculate execution reduction.
4. **Pipeline Agent**: Generate child pipeline, execute selected tests, track runtime.
5. **Communication Agent**: Generate MR comments, explain selection reasoning, report savings.
