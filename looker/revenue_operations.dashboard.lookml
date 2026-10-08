- dashboard: revenue_operations
  title: Revenue operations — sample
  layout: newspaper
  preferred_viewer: dashboards-next
  elements:
  - name: won_value
    title: Won deal value
    model: revenue_operations
    explore: opportunities
    type: single_value
    fields: [opportunities.won_value]
    row: 0
    col: 0
    width: 8
    height: 4
  - name: win_rate
    title: Closed-deal win rate
    model: revenue_operations
    explore: opportunities
    type: single_value
    fields: [opportunities.win_rate]
    row: 0
    col: 8
    width: 8
    height: 4
  - name: open_deals
    title: Open opportunities
    model: revenue_operations
    explore: opportunities
    type: single_value
    fields: [opportunities.open_deals]
    row: 0
    col: 16
    width: 8
    height: 4
  - name: monthly_value
    title: Monthly won value
    model: revenue_operations
    explore: opportunities
    type: looker_column
    fields: [opportunities.month, opportunities.won_value]
    filters: {opportunities.stage: "Closed Won"}
    sorts: [opportunities.month]
    row: 4
    col: 0
    width: 12
    height: 8
  - name: regional_value
    title: Won value by office
    model: revenue_operations
    explore: opportunities
    type: looker_bar
    fields: [opportunities.region, opportunities.won_value]
    sorts: [opportunities.won_value desc]
    row: 4
    col: 12
    width: 12
    height: 8
