# Native Power BI acceptance checklist
The supplied Power Query, DAX, theme and four-page specifications remain the authoring kit. No PBIX/PBIT binary or fabricated native report is included. This Linux environment does not have Power BI Desktop; a native Power BI dashboard remains pending.

1. Open Power BI Desktop on a supported Windows machine. Import the cleaned CSVs using the supplied `.pq` scripts; set a private local root parameter for the extracted project folder.
2. Confirm opportunity/account/representative keys, one-to-many relationships and date column types. Preserve null open-deal amounts.
3. Add the supplied DAX measures and theme; author the four pages in the existing page specs.
4. Reconcile full-sample won value 10,005,534, won deals 4,238, closed deals 6,711, win rate 63.1501…%, open deals 2,089. Commission scenario should sum per-representative rounded 5% payouts to 500,276.70.
5. Verify office/representative filters, blank open monetary values and filtered export totals. The source has no currency code; use a visible convention, not an unsupported multi-currency claim.
6. Save an actual PBIX; optionally save a native PBIP project and keep the model/report files. Open it again, refresh successfully, and retain an actual Desktop screenshot and refresh time. Add those artifacts only after verification.

PBIR is a documented source format, but a handwritten empty report project would not satisfy the requested native dashboard. Reference: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report . Checked 2026-10-08.
