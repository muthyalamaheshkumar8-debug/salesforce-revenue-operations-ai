# Native Salesforce report metadata
Included: native ReportFolder and Report XML under `force-app/main/default/reports/`. These are source-format Metadata API assets, not deployed reports. XML well-formedness can be checked locally; only a target org can establish schema compatibility, report-field aliases and successful execution.

From `salesforce/`, authenticate a dedicated sandbox with Salesforce CLI using your normal login flow. Confirm the alias points to a sandbox; do not use a production alias for portfolio practice.

```sh
sf project deploy start --target-org revenue-sandbox --source-dir force-app/main/default/reports --dry-run
sf project deploy start --target-org revenue-sandbox --source-dir force-app/main/default/reports
```

Perform actual deployment only after inspecting the dry-run. The report folder is public within the org with ReadOnly public access; adjust to your org's approved sharing policy before deployment. No deployment command was run here.

Open Reports → Revenue Operations → Won Revenue. Confirm the Opportunity report type, Amount summary and Closed Won filter. A custom stage name or different report alias can require changes. Use native Report Builder and retrieve metadata if your org differs. Record the actual report ID, report period, run time, row count and value. The complete imported sample reconciles to 4,238 won deals and 10,005,534 value; the existing 500-row starter subset will have different totals.

Keep org-specific OwnerId/AccountId values private. Native Salesforce totals may use org currency conversions; compare currencies and report scope before reconciliation.
Reference: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_report.htm and https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_start.html . Checked 2026-10-08.
