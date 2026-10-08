view: opportunities {
  sql_table_name: public.opportunities ;;
  dimension: opportunity_id { primary_key: yes type: string sql: ${TABLE}.opportunity_id ;; }
  dimension: stage { type: string sql: ${TABLE}.stage ;; }
  dimension: rep { type: string sql: ${TABLE}.rep ;; }
  dimension: region { type: string sql: ${TABLE}.region ;; }
  dimension: product { type: string sql: ${TABLE}.product ;; }
  dimension: month { type: string sql: ${TABLE}.month ;; }
  dimension: amount { type: number sql: ${TABLE}.amount ;; }
  measure: opportunity_count { type: count }
  measure: won_deals { type: count filters: [stage: "Closed Won"] }
  measure: closed_deals { type: count filters: [stage: "Closed Won,Closed Lost"] }
  measure: won_value { type: sum sql: ${amount} ;; filters: [stage: "Closed Won"] value_format: "#,##0.00" description: "Won deal value; not accounting revenue. Source currency unspecified." }
  measure: win_rate { type: number sql: 1.0 * ${won_deals} / NULLIF(${closed_deals},0) ;; value_format_name: percent_1 }
  measure: open_deals { type: count filters: [stage: "Prospecting,Engaging,Qualification,Needs Analysis,Proposal,Negotiation"] }
}
