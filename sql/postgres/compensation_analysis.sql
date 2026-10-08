SELECT rep,target,actual,achievement,commission_rate,payout,CASE WHEN achievement>=1 THEN 'Target achieved' ELSE 'Below target' END AS status FROM compensation ORDER BY payout DESC;
