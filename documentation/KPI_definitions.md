# KPI definitions
Population: all 8,800 Maven CRM opportunities; all closed deals close in 2017. Full extract is imported; no sampled row cap.

| KPI | Definition |
|---|---|
| Won revenue | Sum source close_value for Won deals; sales-value proxy |
| Open opportunities | Count Engaging + Prospecting, including rows with missing accounts |
| Win rate | Won / (Won + Lost); exclude open deals |
| Average won deal | Won value / Won count |
| Average engagement-to-close | Mean(close_date − engage_date) for Won deals |
| Scenario attainment | 2017 won value / assumed $500,000 annual target per selected listed agent |
| Estimated payout | 5% × won value; illustrative rate |
| Retained opportunities | All source rows after identity, relationship and date checks |

Monetary open pipeline, weighted forecasts, creation-to-close cycles, profit and historical stage transitions are unavailable. Never fill missing open amounts with zero. Null denominators yield unavailable rates. Overview filters intersect sales office, product, closing month and agent. `Not closed` selects open rows. Performance and compensation expose office/agent filters over the entire annual scenario period. Quality is full-dataset scope. Customer geography is distinct from agent sales office.
