# API service

The public dashboard is deployed separately and reads a same-origin published snapshot. This FastAPI service is runnable project code; it is **not yet a public backend deployment**.

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.lock.txt
.venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000/docs`. The five GET endpoints work on the bundled public sample without credentials. `/api/sales` is paginated (maximum 1,000 rows per request); region, rep, product and month filters intersect. Null open amounts remain null.

`POST /api/analyze` requires `ANALYSIS_API_TOKEN` and an Authorization bearer header. Request `{ "mode": "rules", "region": "West" }` gives reproducible findings. `mode: "llm"` additionally requires `OPENAI_API_KEY` and `LLM_MODEL`; missing configuration returns 503. Schema validation checks structure, not factual correctness: model output is a draft requiring human review.

PostgreSQL: create a dedicated `revenue_operations` database yourself, set `DATABASE_URL`, run `python python/load_postgres.py`, then set `REVENUE_STORAGE=postgres` before starting the API. The loader uses a transaction and primary-key upserts; it refuses a different database name and unexpected pre-existing opportunity coverage. Native PostgreSQL execution has not been performed in this environment.

The opportunity-event request also accepts `opportunity` and `event_id`. The event processor enforces currency and threshold, rejects conflicting retries, and stores a review outbox in SQLite. No email or Slack message is sent. Deploy the backend with HTTPS, a durable `WORKFLOW_STATE_PATH`, configured access controls and rate limits before connecting external automation. Do not expose the sample server directly from a laptop.

Environment variable names are in `.env.example`; the application reads the process environment, not that file automatically. Keep real Salesforce and model credentials out of source and exports. Salesforce extraction is read-only and saves private JSON for review; it does not replace the published dataset automatically.
