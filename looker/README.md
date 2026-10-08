# Looker authoring kit
These are actual LookML source files, not a screenshot or a claim of a deployed Looker dashboard. Native validation and execution are pending.

1. Load the existing PostgreSQL schema/data into a dedicated database using `python/load_postgres.py`.
2. Configure a read-only Looker PostgreSQL connection named `revenue_operations_postgres`, or change the model connection name.
3. Import these files into a Looker development project at its root. Run LookML validation and fix any version or connection-specific issues before deployment.
4. Open the Revenue operations Explore and supplied dashboard. Reconcile won_value = 10,005,534; won_deals = 4,238; closed_deals = 6,711; open_deals = 2,089 on the complete sample. Monthly groups use the same Closed Won filter.
5. Keep an actual query/dashboard ID and execution receipt. Importing files alone is not hands-on platform execution.

Source currency is unspecified. LookML intentionally uses plain number formatting and does not value unknown open pipeline amounts.
Official references: https://docs.cloud.google.com/looker/docs/reference/param-view-view and https://docs.cloud.google.com/looker/docs/reference/param-lookml-dashboard-type . Checked 2026-10-08.
