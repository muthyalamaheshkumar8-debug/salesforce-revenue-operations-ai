# Salesforce setup mapping
The current public sample is a CSV extract, not a live Salesforce org. Import 85 accounts first. Map portfolio account/agent keys to actual AccountId/OwnerId. The opportunities import contains the 6,711 closed deals only: open source rows lack mandatory CloseDate and must not be assigned invented dates. Stage labels require appropriate org picklist mappings. No contacts or leads exist in the online sample; original synthetic fixtures remain separately archived.

Historical engagement dates are not Salesforce CreatedDate. Dollar display is a portfolio convention; select and document org currency before import. Validate XML rules and field mappings in a sandbox before deployment. Native import is not completed here.
