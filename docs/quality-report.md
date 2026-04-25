# Quality Report

## Week 12. Testing

Command:

```powershell
pytest
```

Coverage gate:

```text
--cov=app --cov-report=term-missing --cov-fail-under=40
```

Covered areas:

- personalization API: favorites, saved searches, collections, topic subscriptions;
- Supabase OAuth token mapping to local user profile;
- collector upsert and relation sync logic;
- OpenAlex refresh TTL decision logic;
- publication query parameter parsing.

## Week 13. Load Testing

k6 command:

```powershell
k6 run load_tests/k6_public_api.js
```

Remote demo target:

```powershell
$env:BASE_URL="https://research-platform-seven.vercel.app"
k6 run load_tests/k6_public_api.js
```

Scenario:

- ramp to 25 virtual users;
- ramp to 100 virtual users;
- hit `/`, `/api/v1/health`, `/api/v1/publications`, `/api/v1/topics`, `/analytics`;
- check 2xx responses;
- enforce error rate `< 5%` and p95 latency `< 1500ms`.

## Week 14. Deployment

Deployment surface:

- Vercel application;
- Supabase PostgreSQL for demo/prod data;
- application logs through Vercel and Supabase dashboards.

## Week 15. Final Defense

Demo checklist:

- open Vercel deployment;
- show Google login and profile tools;
- run a publication search and show OpenAlex-backed refresh;
- show Supabase tables;
- show analytics dashboard;
- show GitHub Actions CI;
- show k6 output.
