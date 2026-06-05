# Load Testing Guide

## Quick Start

```bash
# Install Locust
pip install locust

# Run with web UI (interactive)
locust -f load_tests.py --host=http://localhost:8000

# Open browser at http://localhost:8089
# Set users: 100, spawn rate: 10, then click Start
```

## Headless Mode (CI/CD)

```bash
# 500 users, 50 new users/second, run for 5 minutes
locust -f load_tests.py \
  --host=http://localhost:8000 \
  --users=500 \
  --spawn-rate=50 \
  --run-time=5m \
  --headless \
  --csv=reports/load_test

# 1000 users stress test
locust -f load_tests.py \
  --host=http://localhost:8000 \
  --users=1000 \
  --spawn-rate=100 \
  --run-time=10m \
  --headless \
  --csv=reports/stress_test
```

## Test Scenarios

| User Type | Weight | Behavior |
|-----------|--------|----------|
| JobSeekerUser | 50% | Search jobs, view dashboard, browse |
| DashboardUser | 25% | View/update profile, check skills |
| AIUser | 15% | Generate summaries, interview questions |
| HRUser | 10% | View posted jobs, check applications |

## What to Measure

### Target SLAs for Production

| Metric | Target | Critical |
|--------|--------|----------|
| P50 response time | < 200ms | < 500ms |
| P95 response time | < 500ms | < 2000ms |
| P99 response time | < 1000ms | < 5000ms |
| Error rate | < 0.1% | < 1% |
| Throughput | > 500 req/s | > 100 req/s |
| AI endpoints P95 | < 5s | < 30s |

### Scaling Milestones

| Users | What to check |
|-------|---------------|
| 100 | Basic functionality, no errors |
| 500 | Response times stay under SLA |
| 1000 | DB connection pool behavior |
| 5000 | Rate limiter kicks in correctly |
| 10000 | Need horizontal scaling (multiple instances) |

## Pre-requisites for Accurate Testing

1. **Seed test data:**
   ```bash
   python seed_jobs.py  # Seed 50+ jobs
   # Create test users via /api/v1/auth/register
   ```

2. **Run backend in production mode:**
   ```bash
   APP_ENV=dev uvicorn main:app --workers=4 --host=0.0.0.0 --port=8000
   ```

3. **Monitor during tests:**
   - MongoDB Atlas metrics (connections, queries/sec, disk)
   - Server CPU/Memory (`htop` or cloud dashboard)
   - API response times in Locust UI

## Interpreting Results

### Healthy Results ✅
- RPS (Requests/sec) is stable
- Error rate < 1%
- Response times don't increase over time
- No connection pool exhaustion errors in logs

### Unhealthy Signs 🚨
- Response times keep climbing = memory leak or DB bottleneck
- Sudden error spike = connection pool exhausted
- 429 errors increasing = rate limiter working correctly (expected)
- Timeout errors on AI endpoints = LLM provider overloaded

## Running Against Production (Carefully)

```bash
# Start VERY low against production
locust -f load_tests.py \
  --host=https://api.jobmouka.com \
  --users=10 \
  --spawn-rate=2 \
  --run-time=2m \
  --headless

# Only increase if metrics look good
```

## CI/CD Integration

Add to your pipeline:
```yaml
- name: Load Test
  run: |
    pip install locust
    locust -f load_tests.py \
      --host=${{ secrets.API_URL }} \
      --users=100 \
      --spawn-rate=20 \
      --run-time=3m \
      --headless \
      --csv=reports/load_test \
      --exit-code-on-error 1
```
