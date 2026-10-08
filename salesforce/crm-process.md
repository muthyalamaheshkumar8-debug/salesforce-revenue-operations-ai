# CRM implementation checklist
1. Create your own developer or learning org; keep credentials out of the project.
2. Create external IDs and picklists using `data-model.md`.
3. Review standard-field validation XML in a sandbox before deploying. This repository has no live-deployment proof.
4. Import/map cleaned CSVs, accounting for unique actual User IDs.
5. Use the five JSON report specifications to build native reports. Include closed/won predicates explicitly; do not sum lost values into pipeline.
6. Build the executive dashboard from the five native reports.
7. Verify native totals against `documentation/sql_results.json`, allowing for any audited import/date differences.
8. Capture actual org screenshots only after implementation; never label the web portfolio dashboard as a Salesforce screenshot.
