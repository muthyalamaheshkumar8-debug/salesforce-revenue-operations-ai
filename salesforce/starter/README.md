# 500-opportunity starter

500 deterministic source closed-deal rows selected at evenly spaced positions across the sorted closed-deal import. Only closed deals have the required source CloseDate. This is an import subset, not the 8,800-record dashboard population.

Use the 85 source accounts and your actual Salesforce owner mappings. The source has 35 listed agents and 7 products, and supplies no contacts or leads. Extra entities are not fabricated to meet approximate blueprint counts. Missing open CloseDate prevents native import of 2,089 open deals until owners supply valid values.

Create unique Portfolio_ID__c fields, map account and owner lookups to actual Salesforce IDs, configure stage names and verify org currency before import. See salesforce/data-model.md. No Salesforce org has been modified.
