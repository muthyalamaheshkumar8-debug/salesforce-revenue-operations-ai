# Closed Won reporting workflow
Status: **local simulation executed; live Zap not connected or activated**.

Business purpose: copy new won opportunities to a review ledger with traceable source IDs.
Trigger: Salesforce opportunity update to Closed Won (choose the supported event available in your account).
Filter: StageName = Closed Won, Amount ≥ 0, required owner/account/close date present.
Lookup: Google Sheets row with unique Salesforce Opportunity ID.
Action: update the existing row if found; otherwise create a row containing opportunity ID, account, owner, won amount, currency, final close date, and processed timestamp. Preserve idempotency and reconcile retries; Lookup/Create without storage locking may still race under parallel events.
Expected result: one ledger record per won opportunity; no duplicate entries on retries. Closed Lost should not fire the append. Corrections must update the existing ledger rather than double-count.

Local equivalent: `python zapier/simulate_workflow.py`. SQLite's primary key makes same-ID insert retries idempotent. The first run inserted 102 won deals; second run inserted 0. `simulated_closed_won.csv` is the reviewed sample ledger. This does not test Zapier auth, API quotas, polling, Sheets concurrency or production failure handling.

Live acceptance: use your own Salesforce/Sheets accounts, verify permissions and plan eligibility, test won/lost/retry/changed-amount events, confirm actual Sheets rows, then activate. Add a real screenshot after the live test; never claim the local simulation proves the Zap is live.
