SELECT month,SUM(amount) AS won_revenue,COUNT(*) AS won_deals,AVG(amount) AS average_deal_size FROM opportunities WHERE stage='Closed Won' GROUP BY month ORDER BY month;
