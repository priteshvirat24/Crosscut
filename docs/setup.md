# Orbit Sentinel — Setup Guide

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.12+ | 3.12+ |
| Node.js | 20+ | 22+ |
| PostgreSQL | 15+ | 16+ |
| Redis | 6+ | 7+ |
| Docker | 24+ | 27+ |

## Quick Setup (Development)

### 1. Clone the repository

```bash
git clone https://gitlab.com/your-org/orbit-sentinel.git
cd orbit-sentinel
```

### 2. Create environment file

```bash
cp .env.example .env
```

Edit `.env` and configure:
- **Required**: At least one LLM API key (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY`)
- **Optional**: `GITLAB_TOKEN` for live GitLab integration
- **Optional**: `ORBIT_API_URL` for Orbit Remote (defaults to mock mode)

### 3. Install dependencies

```bash
make install
```

This runs:
- `pip install -e ".[dev]"` for the Python backend
- `npm install` for the Next.js dashboard

### 4. Start development servers

```bash
make dev
```

This starts:
- **Backend**: http://localhost:8000 (FastAPI + Swagger at `/docs`)
- **Dashboard**: http://localhost:3000

### 5. Verify

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

## Docker Setup (Production)

### 1. Build and start all services

```bash
make deploy
```

This starts:
- Backend API (port 8000)
- Dashboard (port 3000)
- Celery worker
- PostgreSQL (port 5432)
- Redis (port 6379)

### 2. Run database migrations

```bash
make db-migrate
```

### 3. Seed demo data (optional)

```bash
make demo-seed
```

## GitLab Webhook Configuration

1. Go to your GitLab project → Settings → Webhooks
2. URL: `https://your-sentinel-host/api/v1/webhooks/gitlab`
3. Secret Token: Set to match `GITLAB_WEBHOOK_SECRET` in `.env`
4. Trigger: ✅ Merge request events
5. Click "Add webhook"

## Orbit Configuration

### Mock Mode (Default)
No configuration needed. Uses demo data simulating 17 downstream repositories.

### Orbit Remote
1. Enable Orbit on your GitLab instance (Premium/Ultimate)
2. Set `ORBIT_MODE=api` in `.env`
3. Set `ORBIT_API_URL` to your instance's Orbit API endpoint

### Orbit Local
1. Install the Orbit CLI: `pip install gitlab-orbit`
2. Set `ORBIT_MODE=cli` in `.env`
3. Index your repositories: `glab orbit index .`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change `APP_PORT` in `.env` |
| Database connection error | Ensure PostgreSQL is running, check `DATABASE_URL` |
| LLM API errors | Verify API key and model name in `.env` |
| Dashboard build fails | Run `cd dashboard && npm install` again |
