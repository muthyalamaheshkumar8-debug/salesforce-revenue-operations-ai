# High-value opportunity workflow

Import `high_value_opportunity.json` into n8n. It is inactive and contains no credentials. Flow: Salesforce Opportunity Updated → authenticated REST fetch → required-field/currency checks → high-value gate → protected analysis API → stored review outbox. The backend performs duplicate-event checks and runs either operational rules or the LangChain chain.

Configure Salesforce OAuth on the trigger and fetch nodes. Configure n8n Header Auth on the analysis node with header `Authorization` and your backend bearer token. Set the allowed environment variables on your own n8n deployment:

| Variable | Meaning |
|---|---|
| SALESFORCE_INSTANCE_URL | Canonical HTTPS Salesforce instance origin |
| SALESFORCE_API_VERSION | Supported org version, default v68.0 |
| REVENUE_API_URL | Your deployed backend HTTPS origin |
| WORKFLOW_CURRENCY | Exact configured source currency, default INR |
| HIGH_VALUE_THRESHOLD | Threshold in that currency, default 500000 |
| ANALYSIS_MODE | rules, or llm after configuring the model |

Default INR threshold matches the blueprint's ₹5 lakh example. It is **not applied to the Maven sample**, which has no currency code or high-value open amounts. Do not convert the public sample to INR without real currency evidence. In a single-currency Salesforce org, configure an explicit org-currency mapping after confirming the org setting; do not infer it.

The server stores an idempotent outbox record. A repeat `Id:LastModifiedDate` is a duplicate; a changed payload with that same ID is rejected. Currency mismatch and invalid amount stop the workflow. Below-threshold items take the false branch and produce no analysis. Keep state on a durable volume for deployment.

The final node intentionally stops for notification review. Choose recipients and add your approved email/Slack integration only after reviewing the draft. No messages have been sent and no native n8n run has been claimed. Environments that restrict `$env` access must use approved n8n variables or explicit node settings instead.

Local verification: `node --test tests/revenue/n8n.test.mjs` and the Python event tests validate the code node and backend contracts. They do not establish native n8n import/execution success.

Primary references: https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.salesforcetrigger/ ; https://github.com/n8n-io/n8n/blob/master/packages/nodes-base/nodes/Salesforce/SalesforceTrigger.node.ts ; https://developer.salesforce.com/docs/platform/api-rest/guide/resources-sobject-upsert-patch.html
