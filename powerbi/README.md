# Power BI implementation kit
Native PBIX authoring has not been performed. This folder contains implementation assets, not a renamed HTML/PBIX file.

1. In Power BI Desktop, create a Text parameter named `pRoot` equal to the extracted project folder, using forward slashes.
2. Create five blank queries named opportunities, accounts, sales_reps, compensation, quality_exceptions. Paste each matching `.pq` into Advanced Editor. The file explicitly promotes headers and sets numeric/date types.
3. Add the DAX measures one at a time; the final `Date = CALENDAR(...)` expression creates a calculated table, not a measure. Mark Date as the date table.
4. Relationships: accounts[account_id] 1→many opportunities[account_id], sales_reps[rep_id] 1→many opportunities[rep_id], Date[Date] 1→many opportunities[close_date]. Use single-direction filters. Compensation is a separately materialized annual illustrative ledger; do not relate it to a monthly date slicer. Dim rep can filter both facts.
5. Executive page: Won Revenue, Open Opportunities, Win Rate, Average Won Deal; monthly won-revenue columns, stage deal-count bars, regional/product breakdowns. Filter by close date/region/product/rep.
6. Performance page: fixed full-year 2017 closing cohort; rep/region slicers; quota vs won revenue bars and scorecard. Do not let product/month slicers turn annual illustrative quotas into partial-period comparisons.
7. Compensation page: fixed full-year 2017 closing cohort; estimated payouts, attainment, and ledger; explicit simulation note. Use only representative/region slicers.
8. Quality page: exception ledger plus counts of distinct records and raw-row reconciliation. Count failed rules separately from distinct bad records.
9. Import `theme.json`. Format money using the documented dollar convention; the source supplies no currency code, fractions as percentages. Export actual screenshots and save a native `.pbix` after totals match the verified source.

Optional database path: load PostgreSQL with the supplied script, then use Power BI’s PostgreSQL connector. That connection needs your own database host/access and was not tested here.

Primary references:
- https://learn.microsoft.com/en-us/power-query/connectors/text-csv
- https://learn.microsoft.com/en-us/power-query/connectors/postgresql

Current source: public Maven CRM sample. Open amounts/dates remain missing; use Open Opportunities for pipeline activity. Scenario targets and commission rates are assumptions. `created_date` represents engagement, not creation.
