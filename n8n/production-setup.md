# Native n8n verification
The existing `high_value_opportunity.json` is an inactive native n8n workflow. This project also provides POST `/api/operations/webhooks/n8n` for a Webhook → authenticated HTTP Request flow. Local receiver tests are not native n8n executions.

1. Import the existing workflow into your n8n environment and inspect every node before activation.
2. Configure Salesforce credentials, backend HTTPS origin and bearer auth through n8n's private credentials store. Set currency and amount thresholds to match source records.
3. For a webhook variant, use a Webhook POST trigger followed by an HTTP Request to the operations receiver; send event_id and opportunity, with analysis bearer auth. Restrict ingress to authorized senders.
4. Use the test webhook URL while listening. Use the production URL only after publishing/activating the workflow. Confirm the distinction in your installed n8n version.
5. Verify success, same-event retry, changed-payload conflict, currency mismatch and below-threshold behavior. Retain the actual native execution ID and response.
6. Backend outbox is awaiting_review. No notification delivery or CRM update is implemented. Do not add unsupervised messaging as a test.

Reference: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook . Checked 2026-10-08.
