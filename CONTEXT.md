# JobMitra Backend — Context

## Stack
FastAPI + MongoDB Atlas + Redis + Gemini/OpenAI + Playwright

## Entry Point
`app.py` — `create_app()` registers all routers. Never add routes anywhere else.

## File Naming Convention
Every feature has exactly three files:
```
{feature}_endpoints.py   ← route handlers only
{feature}_db.py          ← all DB operations (class-based)
{feature}_schemas.py     ← Pydantic models
```

## Active Feature Files
| Feature | Endpoints | DB | Schemas |
|---|---|---|---|
| Auth | `auth_endpoints.py` | `auth_db.py` | `auth_schemas.py` |
| HR | `hr_endpoints.py` | — | — |
| Jobs | `endpoints.py` | `job_db.py` | `job_schemas.py` |
| Applications | `job_application_endpoints.py` | `job_application_db.py` | `job_application_schemas.py` |
| Apply | `apply_endpoints.py` | — | — |
| Dashboard | `dashboard_endpoints.py` | — | — |
| Resume | `resume_endpoints.py` | — | — |
| Resume Tailor | `resume_tailor_endpoints.py` | — | — |
| CV Bootstrap | `cv_bootstrap_endpoints.py` | — | — |
| CV Upload | `cv_upload_endpoints.py` | — | — |
| CV JD | `cv_jd_endpoints.py` | — | — |
| Mock Interview | `interview_prompts_endpoints.py` | — | — |
| Interview Eval | `interview_evaluation_endpoint.py` | — | — |
| Skill Assessment | `skill_assessment_endpoints.py` | — | — |
| Match Analysis | `match_analysis_endpoints.py` | — | — |
| Internal Jobs | `internal_job_endpoints.py` | `internal_job_db.py` | `internal_job_schemas.py` |
| Project Contest | `project_contest_endpoints.py` | `project_contest_db.py` | `project_contest_schemas.py` |
| Credits | `credits_endpoints.py` | — | — |
| PDF | `pdf_endpoints.py` | — | — |
| Upload | `upload_endpoints.py` | — | — |
| Google Auth | `google_auth_endpoints.py` | — | — |

## Key Shared Services
| File | Purpose |
|---|---|
| `multi_llm_service.py` | All LLM calls — never call OpenAI/Gemini SDKs directly |
| `prompt_manager.py` | All prompts from `prompts/*.json` — never hardcode prompts |
| `cache.py` | Redis caching — `await cache.get/set` |
| `activity_tracker.py` | User activity logging |
| `email_service.py` | Email sending (always via `asyncio.to_thread`) |
| `rate_limiter.py` | Rate limiting middleware |
| `response_helpers.py` | Standard response envelope |
| `db_indexes.py` | All MongoDB index definitions |

## Auth Pattern
```python
from auth_endpoints import get_current_user          # any authenticated user
from hr_endpoints import get_current_hr_user         # HR only
```

## Response Envelope
```python
{"message": "...", "data": ..., "success": True}
```

## Router Prefix
All routes: `/api/v1/{feature-name}`

## Prompts Location
`prompts/*.json` — 15 prompt files currently active.

## Environment
`.env` for local, `.env.dev` for dev, `.env.prod` for prod.
All config via `config.py` `settings.*` — never hardcode secrets.
