# JobMouka Coding Guidelines
> Also see EnterpriseRules.md in this same folder for full enterprise standards.

You are generating code for an Angular 20+ + FastAPI backend project. Follow these rules strictly:

FRONTEND:
- Use standalone components, @if/@for/@switch.
- Prefer signals (signal, computed, effect) over manual RxJS.
- Auto-teardown subscriptions with takeUntilDestroyed().
- No setTimeout/setInterval — use signals/animations.
- Strict typing, remove unused code, optimize performance (OnPush, trackBy, memoization, lazy routes).
- Accessibility and security must be ensured.
- Recheck before concluding whether there are build errors and run time errors.
- **Reuse existing configurable components** — before creating a new component, check `src/app/shared/ui/` and `src/app/shared/components/` for an existing one that can be configured via inputs. Never duplicate a component that already exists.
- **Optimised code only** — write the minimal code that correctly solves the problem. No redundant variables, no unnecessary re-renders, no over-engineered abstractions.
- **Space & time complexity** — always choose the most efficient algorithm and data structure. Prefer `Map`/`Set` over array scans for lookups. Avoid nested loops on large datasets. Memoize expensive `computed()` values.

BACKEND:
- Use MongoDB Atlas with connection pooling and proper indexing.
- Add Redis caching for frequent queries and sessions.
- All operations must be async/non-blocking.
- Implement rate limiting (100 req/min/user).
- Design for horizontal scaling: multiple FastAPI instances + load balancer.
- Secure endpoints, validate inputs, avoid sensitive data leaks.
- Handle errors gracefully with safe responses.
- Include infrastructure readiness: Docker, K8s, CDN.
- **Optimised queries** — always project only required fields, use indexes, prefer `$match` early in aggregation pipelines to reduce working set.
- **Space & time complexity** — avoid loading entire collections into memory. Use cursors for large datasets. Prefer `$lookup` + `$project` over multiple round-trips. Use `asyncio.gather` for parallel independent operations.
- **Reuse existing services** — before writing new logic, check if `MultiLLMService`, `EmailService`, `CacheService`, or an existing `*_db.py` method already covers it.