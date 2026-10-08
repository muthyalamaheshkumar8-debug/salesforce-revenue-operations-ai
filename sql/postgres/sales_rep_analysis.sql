SELECT r.rep, r.target, SUM(CASE WHEN o.stage='Closed Won' THEN o.amount ELSE 0 END) AS won_revenue,
 SUM(CASE WHEN o.stage='Closed Won' THEN 1 ELSE 0 END) AS won_deals,
 1.0*SUM(CASE WHEN o.stage='Closed Won' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN o.stage IN ('Closed Won','Closed Lost') THEN 1 ELSE 0 END),0) AS win_rate,
 1.0*SUM(CASE WHEN o.stage='Closed Won' THEN o.amount ELSE 0 END)/NULLIF(r.target,0) AS achievement
FROM sales_reps r LEFT JOIN opportunities o ON r.rep_id=o.rep_id GROUP BY r.rep,r.target ORDER BY won_revenue DESC;
