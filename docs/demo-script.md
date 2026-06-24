# Orbit Sentinel — Hackathon Demo Script

## Prerequisites

1. Backend running (`make dev-backend`)
2. Dashboard running (`make dev-dashboard`)
3. Browser open at `http://localhost:3000`

---

## Demo Flow (5 minutes)

### 1. Introduction (30 seconds)

> "Orbit Sentinel is an AI-powered Cross-Repository Change Intelligence Agent.
> It predicts downstream breakages before code is merged, using GitLab Orbit's
> knowledge graph to discover cross-repository dependencies."

Show the **Overview Dashboard** at `http://localhost:3000`.

Point out:
- Total analyses run (142)
- Repositories protected (47)
- Breakages prevented (23)
- Prediction accuracy (87.5%)

---

### 2. Trigger Analysis (45 seconds)

> "Let's see what happens when a developer modifies a shared payment library."

Open terminal and run:

```bash
curl -X POST http://localhost:8000/api/v1/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "mr_iid": 342,
    "project_name": "platform/payment-library"
  }'
```

> "The developer is adding a new required `region` parameter to `validatePayment()`
> and deleting the `getPaymentStatus()` function."

---

### 3. Analysis Results (90 seconds)

Navigate to **Active Analyses** page.

Show the analysis card:
- 🔴 **Risk Score: 78/100** (CRITICAL)
- 💥 **Blast Radius: 82/100**
- 📦 **17 repositories affected**
- 👥 **8 teams impacted**

Show **Breaking Changes**:
- `validatePayment` — new required parameter (CRITICAL, 95% confidence)
- `getPaymentStatus` — function deleted (CRITICAL, 98% confidence)

Read the **Executive Summary**:
> "17 repositories are affected. 3 production services rely on validatePayment().
> 2 authentication flows may break. Recommended action: perform migration before merge."

---

### 4. Impact Explorer (60 seconds)

Navigate to **Impact Explorer** page.

Show the interactive **dependency graph**:
- Source: `payment-library` (purple, center)
- Critical repos: red (checkout-service, billing-service, fraud-detection, payment-sdk-python)
- High repos: orange (analytics-service, mobile-api, auth-service)
- Medium/Low repos: yellow/green (further out)

> "This graph was built by querying GitLab Orbit's knowledge graph.
> Orbit indexes call relationships across ALL repositories in your organization.
> Without Orbit, discovering these dependencies would require manual investigation."

Zoom in on critical paths. Click nodes to show details.

---

### 5. Blast Radius Report (45 seconds)

Navigate to **Blast Radius** page.

Show:
- Radar chart with 5 impact dimensions
- Per-severity breakdown of all 17 repos
- Call site counts (534 calls from payment-sdk-python alone!)

---

### 6. What Makes This Unique (30 seconds)

> "Every other tool discovers problems AFTER deployment.
> Orbit Sentinel prevents problems BEFORE merge.
>
> The key differentiator is GitLab Orbit. Without Orbit's cross-repository
> knowledge graph, you cannot discover that 17 repositories call your function.
> With Orbit, you know your blast radius in under 30 seconds."

---

### 7. Close (30 seconds)

> "Orbit Sentinel shifts organizations from reactive debugging to proactive prevention.
> Know every repository you'll break before you merge."

Show the dashboard one more time. Point to historical accuracy (87.5%).

---

## API Quick Reference

```bash
# Trigger analysis
POST http://localhost:8000/api/v1/analyses

# List analyses
GET http://localhost:8000/api/v1/analyses

# Get analysis detail
GET http://localhost:8000/api/v1/analyses/{id}

# Dashboard overview
GET http://localhost:8000/api/v1/dashboard/overview

# Health check
GET http://localhost:8000/health
```

---

## Key Talking Points

1. **GitLab Orbit is essential** — cross-repo dependency discovery is impossible without it
2. **Seven-agent pipeline** — each agent has a focused responsibility
3. **LangGraph orchestration** — production-grade agent coordination
4. **Under 30 seconds** — full analysis completes fast enough for CI/CD
5. **Actionable output** — migration plans, not just warnings
6. **87.5% accuracy** — predictions are tracked and continuously improved
