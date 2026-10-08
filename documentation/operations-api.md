# Operations API
Public read-only routes: GET `/api/operations/capabilities`, GET `/api/operations/knowledge?q=...&audience=...`.

Private ledger/evidence routes require `Authorization: Bearer <role token>`. Configure distinct `OPERATIONS_API_TOKEN` and `FINANCE_API_TOKEN`. Identical/missing tokens disable the shared workflow. Tokens establish service roles, not verified human identities; deploy behind your identity provider before employer use. Set `OPERATIONS_STATE_PATH` and `WORKFLOW_STATE_PATH` to durable private volumes. Never place role tokens in the public React app.

- POST `/api/operations/ledgers`: operations role; `{ "ledger_id": "practice-001", "rate_bps": 500 }`. Reuses the immutable sample compensation basis. Same ID/calculation returns the existing ledger; changed rate under the same ID returns 409.
- GET `/api/operations/ledgers/{id}`: either role.
- POST `/api/operations/ledgers/{id}/transition`: `{ "expected_version": 1, "target": "reviewed", "note": "Basis reconciled in practice" }` by operations. Then expected_version 2 and target approved by finance. Skipped/out-of-order or stale transitions are rejected. No payment issued.
- POST `/api/operations/evidence`: operations role; receipt_id, requirement_id, external_run_id, note. Stores a self-attested receipt without upgrading external verification status.
- GET `/api/operations/evidence`: either role; private submitted receipts.
- POST `/api/operations/webhooks/zapier` or `/n8n`: **analysis** bearer token; event_id and opportunity with Id, StageName, Amount, CurrencyIsoCode, LastModifiedDate. Uses the existing durable event/currency/threshold guards. Namespace keeps platform event IDs separate. Returned receiver success is not evidence of a native platform run.

All ledgers are scenarios using the bundled fictional sample. Source currency is unspecified and ledger currency stays null. Real payroll rules, secure named approvers, employee pay information, tax, clawbacks and payment rails are not implemented.
