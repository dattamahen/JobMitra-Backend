You are generating code for an Angular 18+ + FastAPI backend project. Follow these rules strictly:
FRONTEND:
- Use standalone components, @if/@for/@switch.
- Prefer signals (signal, computed, effect) over manual RxJS.
- Auto-teardown subscriptions with takeUntilDestroyed().
- No setTimeout/setInterval — use signals/animations.
- Strict typing, remove unused code, optimize performance (OnPush, trackBy, memoization, lazy routes).
- Accessibility and security must be ensured.
- Recheck before concluding whether there are build errors and run time errors

BACKEND:
- Use MongoDB Atlas with connection pooling and proper indexing.
- Add Redis caching for frequent queries and sessions.
- All operations must be async/non-blocking.
- Implement rate limiting (100 req/min/user).
- Design for horizontal scaling: multiple FastAPI instances + load balancer.
- Secure endpoints, validate inputs, avoid sensitive data leaks.
- Handle errors gracefully with safe responses.
- Include infrastructure readiness: Docker, K8s, CDN.