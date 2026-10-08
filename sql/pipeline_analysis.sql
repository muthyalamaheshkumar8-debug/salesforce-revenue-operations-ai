SELECT stage,COUNT(*) AS opportunities,SUM(amount) AS pipeline_value,SUM(amount*probability) AS weighted_pipeline
FROM fact_opportunities WHERE stage NOT IN ('Closed Won','Closed Lost') GROUP BY stage ORDER BY pipeline_value DESC;
