CREATE TABLE IF NOT EXISTS dim_accounts (account_id TEXT PRIMARY KEY, account TEXT NOT NULL, region TEXT NOT NULL, industry TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dim_sales_reps (rep_id TEXT PRIMARY KEY, rep TEXT NOT NULL, region TEXT NOT NULL, target NUMERIC NOT NULL CHECK(target>0), commission_rate NUMERIC NOT NULL CHECK(commission_rate BETWEEN 0 AND 1));
CREATE TABLE IF NOT EXISTS dim_contacts (contact_id TEXT PRIMARY KEY, account_id TEXT REFERENCES dim_accounts(account_id), contact TEXT NOT NULL, email TEXT NOT NULL, job_title TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dim_products (product TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS dim_date (date_key DATE PRIMARY KEY, month TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fact_opportunities (
 opportunity_id TEXT PRIMARY KEY, opportunity TEXT NOT NULL, account_id TEXT REFERENCES dim_accounts(account_id), account TEXT,
 rep_id TEXT NOT NULL REFERENCES dim_sales_reps(rep_id), rep TEXT NOT NULL, region TEXT NOT NULL,
 product TEXT NOT NULL REFERENCES dim_products(product), source TEXT NOT NULL,
 stage TEXT NOT NULL CHECK(stage IN ('Prospecting','Engaging','Qualification','Needs Analysis','Proposal','Negotiation','Closed Won','Closed Lost')),
 amount NUMERIC CHECK(amount>=0), probability NUMERIC CHECK(probability BETWEEN 0 AND 1),
 close_date DATE REFERENCES dim_date(date_key), created_date DATE,
 expected_revenue NUMERIC, won_revenue NUMERIC NOT NULL, month TEXT NOT NULL,
 CHECK(close_date>=created_date));
CREATE VIEW fact_sales AS SELECT opportunity_id, account_id, rep_id, product, close_date, amount AS revenue FROM fact_opportunities WHERE stage='Closed Won';
CREATE VIEW fact_compensation AS SELECT r.rep_id,r.rep,r.region,r.target,r.commission_rate,
 COALESCE(SUM(s.revenue),0) AS actual, COALESCE(SUM(s.revenue),0)*r.commission_rate AS payout,
 COALESCE(SUM(s.revenue),0)/NULLIF(r.target,0) AS achievement
 FROM dim_sales_reps r LEFT JOIN fact_sales s ON s.rep_id=r.rep_id GROUP BY r.rep_id,r.rep,r.region,r.target,r.commission_rate;
