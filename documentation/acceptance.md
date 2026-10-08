# Verification

2026-10-07: 18 automated tests passed (10 Python, 8 JavaScript). Checks cover source reconciliation, filters and nulls, SQL totals, API endpoints/auth/pagination, rules output traceability, LangChain prompt/parser with an injected model, currency/threshold checks, duplicate events and conflicting retries. No live model invocation occurred.

Five SQL analyses ran with SQLite foreign keys; three Pandas notebooks were previously executed on the unchanged source. The source totals remain 8,800 rows, 10,005,534 won value, 4,238 wins, 6,711 closes, 2,089 open records and 500,276.70 simulated 5% commissions.

Public browser verification is recorded in live-verification.md after deployment. Native Salesforce, PostgreSQL, PBIX, n8n import/execution, notifications, live LLM and hosted FastAPI service are pending. Local browser preview was unavailable; deployed UI is checked directly. Mobile/owner editing has not been verified.
