# Sales engagement export adapters
The app accepts normalized JSON, not arbitrary provider-specific CSV layouts. Export authorized metadata from your platform and map it to `engagement-contract.json` before uploading. Date and outcome conventions differ across providers; retain your source export privately.

Supported local adapters: Gong call metadata; Apollo/Outreach/Salesloft calls, emails and meetings. Each record must link to an existing CRM opportunity. Unknown opportunities, invalid dates, duplicate IDs and missing next steps become exceptions. Accepted records are not merged into the published snapshot. No platform API credentials or browser account are requested by this app.

Use Engagement → select platform → Load practice example to test locally. Use Upload normalized JSON for authorized exports. Export review/exception JSON for follow-up. Native API integrations remain unconfigured. An upload is not proof the file originated from the named vendor.
