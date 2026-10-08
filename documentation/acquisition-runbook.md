# New business-line integration rehearsal
Open **New business** in the dashboard. Choose a business-line name and use the practice example or normalized legacy export. The dry-run checks duplicate legacy/destination IDs, known account/owner keys, valid mapped stages, finite non-negative amounts, currency codes and real close dates. Every rejected row needs review before a mapped batch can be exported.

The operation never changes the existing snapshot or writes to Salesforce. Source/owner/territory integration is demonstrated as a rehearsal, not an actual acquisition. Included practice examples are synthetic and separate from the 2017 CRM sample.

Before real migration: inventory systems and permissions, approve account/owner crosswalks, define stage mappings, agree territory/compensation policy, obtain data-owner sign-off, dry-run, reconcile row counts and totals **separately per currency**, define rollback and test in sandbox. Record batch IDs and post-load totals. One business line can contain multiple currencies; do not add their amounts together without an approved FX process.

Normalized fields: legacy_id, account_id, rep_id, stage, amount, currency, close_date. The prefixed destination key is `<business-line>:<legacy-id>`. Re-running the same source against a real destination requires checking persisted destination IDs; this app checks the bundled snapshot only. No production commit is offered.
