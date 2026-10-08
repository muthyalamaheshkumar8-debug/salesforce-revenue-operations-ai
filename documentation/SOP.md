# Opportunity management and reporting SOP
1. Create an account/contact in the source CRM; verify company duplicates before import.
2. Create an opportunity with a unique external portfolio ID, account, owner, positive or zero amount, stage and close date.
3. Example configuration only (not Maven observations): Prospecting 10%, Qualification 25%, Needs Analysis 40%, Proposal 60%, Negotiation 80%, Closed Won 100%, Closed Lost 0%.
4. Update stage/close date as the deal progresses. Closed Won and Closed Lost are alternative terminal outcomes; do not move won deals automatically to lost.
5. Export the source data, mapping real Salesforce IDs to explicit portfolio dimension keys. Keep original raw inputs.
6. Run `python python/pipeline.py`. Review the exceptions before reporting. Formatting can be standardized; business-critical missing/invalid values require source-owner correction.
7. Resolve quarantined records in the authoritative CRM, then re-export and rerun. Never fabricate an owner/date/amount.
8. Run SQL and notebooks. Check that raw rows minus repeated-ID rows minus quarantined unique records equals valid rows.
9. Review revenue, pipeline and closed-deal denominators. Preserve the annual illustrative scope for quotas.
10. Review simulated commissions against the flat-rate policy. An authorized human must approve any real payroll outside this project.
11. Refresh the compiled dashboard with validated data, retaining source classification and reporting period.
12. Test Closed Won workflow idempotency before activating any external automation. No external messages are sent by the local simulator.

Current source: public Maven CRM sample. Open amounts/dates remain missing; use Open Opportunities for pipeline activity. Scenario targets and commission rates are assumptions. `created_date` represents engagement, not creation.

## AI and automation operations

Run python/sales_analysis.py after each validated import, then rebuild and republish the same Site. AS_OF is fixed to 2017-12-31 for this sample; review it when changing data. Live extraction stays private until mapped and validated.

Configure the dedicated PostgreSQL database before enabling REVENUE_STORAGE=postgres. Import the inactive n8n workflow and test threshold boundaries, currency mismatch and retry conflicts. Use rules mode initially. Configure model credentials after reviewing data scope. Human review precedes any notifications; explicitly select recipients. Keep event state on durable storage. Native setup is pending.
