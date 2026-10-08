# Configure this connection name in your Looker project before validation.
connection: "revenue_operations_postgres"
include: "/*.view.lkml"
include: "/*.dashboard.lookml"
explore: opportunities { label: "Revenue operations" }
