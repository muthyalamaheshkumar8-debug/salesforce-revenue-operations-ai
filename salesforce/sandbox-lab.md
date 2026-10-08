# Salesforce practice and evidence checklist
Prepared assets are not professional Salesforce administration experience. Complete the following in an actual authorized sandbox and retain real evidence privately.

- [ ] Inspect Account, Contact, Lead and Opportunity permissions with a least-privilege role.
- [ ] Map the provided Account and representative keys to actual AccountId and OwnerId. Import a controlled closed-deal subset, retaining a rollback export.
- [ ] Review and dry-run the supplied validation rules; demonstrate a valid and invalid edit without changing production records.
- [ ] Deploy/run the native report assets per `native-reports.md`; capture actual report results.
- [ ] Configure read-only REST credentials in your local environment and run `python/salesforce_extract.py`; verify pagination and record counts.
- [ ] Review the developer handoff with an actual collaborator. Record reviewer, decision and evidence; templates are not collaboration.
- [ ] Configure a real Zapier or n8n run using authorized test events; keep execution IDs.

Practice descriptions may say "built Salesforce integration and metadata assets" now. Say "configured and tested in a Salesforce sandbox" only after completing the native work. Say "professional administration" only for actual work experience you can support.
