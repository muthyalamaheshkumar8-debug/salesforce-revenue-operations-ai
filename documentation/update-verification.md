# Operations workspace verification — 2026-10-08

Passed: 16 Python tests and 13 JavaScript tests (29 total). Existing source totals and filters reconcile; new tests cover engagement linkage and invalid/duplicate dates, acquisition mapping and export gates, per-representative commission rounding, training grading, complete requirement/artifact coverage, private role access, durable ledger retries, changed-ID conflicts, optimistic concurrency, separate finance approval, receipt provenance and authenticated Zapier/n8n event processing.

Full sample unchanged: 8,800 opportunities; won value 10,005,534; 4,238 won / 6,711 closed deals; 2,089 open deals; per-representative 5% scenario payout 500,276.70. Original app ID and query IDs preserved. Six new operational views supplement seven original views. Shared runtime/chrome and integrity files were not changed.

Native Salesforce XML parses as well-formed XML. This does not establish compatibility or deployment in a Salesforce org. LookML files are authored; native validation/execution remains pending. Native Power BI Desktop/PBIX authoring remains pending. No vendor accounts, real sales-team sessions, actual collaborator reviews, payments, notifications or CRM writes occurred.

Build: supported installed Data compiler with separate-data snapshot and portable offline export. Authored ownership checks pass.

Published and reviewed on the existing public site on 2026-10-08. Deployment version 5, source commit 969079eebae909b6c00439724d9f55b04d38124c. The complete client and snapshot assets passed SHA-256 readback; the published snapshot has 9 queries and 11,776 total reviewed rows. Data, app ID, saved presentation and sharing policy were preserved.

Live browser review: all 13 navigation views are present. Verified knowledge search, training grading (2/2), Gong practice import matching (1 accepted, 0 exceptions), business-line practice mapping (1 accepted, 0 exceptions), payout state sequence calculated → reviewed → approved and CSM audience-specific draft generation. Captured seven genuine live screenshots. The 42-second MP4 is a captioned screenshot walkthrough, not a continuous recording. Browser extension metadata errors occurred; no application error appeared in the inspected console output. Narrow-width layouts, UI download exports and native vendor UIs remain unverified.

The public site hosts the browser workspace; the separate authenticated Python backend is supplied as source and is not claimed to be deployed by this Sites release. Native execution, actual sales-team sessions, actual developer reviews and real payouts remain pending as shown in the coverage view.
