-- Apply inside a dedicated revenue_operations database; existing data is preserved.
CREATE TABLE IF NOT EXISTS accounts (account_id TEXT PRIMARY KEY,account TEXT NOT NULL,region TEXT NOT NULL,industry TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sales_reps (rep_id TEXT PRIMARY KEY,rep TEXT NOT NULL,region TEXT NOT NULL,target NUMERIC NOT NULL CHECK(target>0),commission_rate NUMERIC NOT NULL CHECK(commission_rate BETWEEN 0 AND 1));
CREATE TABLE IF NOT EXISTS contacts (contact_id TEXT PRIMARY KEY,account_id TEXT REFERENCES accounts(account_id),contact TEXT NOT NULL,email TEXT NOT NULL,job_title TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS products (product TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS opportunities (
 opportunity_id TEXT PRIMARY KEY,opportunity TEXT NOT NULL,account_id TEXT REFERENCES accounts(account_id),account TEXT,
 rep_id TEXT NOT NULL REFERENCES sales_reps(rep_id),rep TEXT NOT NULL,region TEXT NOT NULL,product TEXT NOT NULL REFERENCES products(product),source TEXT NOT NULL,
 stage TEXT NOT NULL CHECK(stage IN ('Prospecting','Engaging','Qualification','Needs Analysis','Proposal','Negotiation','Closed Won','Closed Lost')),
 amount NUMERIC CHECK(amount>=0),probability NUMERIC CHECK(probability BETWEEN 0 AND 1),close_date DATE,created_date DATE,
 expected_revenue NUMERIC,won_revenue NUMERIC NOT NULL,month TEXT NOT NULL,CHECK(close_date>=created_date));
CREATE OR REPLACE VIEW sales AS SELECT opportunity_id,account_id,rep_id,product,close_date,amount AS revenue FROM opportunities WHERE stage='Closed Won';
CREATE OR REPLACE VIEW compensation AS
SELECT r.rep_id,r.rep,r.region,r.target,r.commission_rate,
COALESCE(SUM(CASE WHEN o.stage='Closed Won' THEN o.amount ELSE 0 END),0) AS actual,
COALESCE(SUM(CASE WHEN o.stage='Closed Won' THEN o.amount ELSE 0 END),0)*r.commission_rate AS payout,
COALESCE(SUM(CASE WHEN o.stage='Closed Won' THEN o.amount ELSE 0 END),0)/r.target AS achievement,
COUNT(CASE WHEN o.stage='Closed Won' THEN 1 END) AS won_deals,
COUNT(CASE WHEN o.stage LIKE 'Closed%' THEN 1 END) AS closed_deals,
COUNT(CASE WHEN o.stage='Closed Won' THEN 1 END)::NUMERIC/NULLIF(COUNT(CASE WHEN o.stage LIKE 'Closed%' THEN 1 END),0) AS win_rate
FROM sales_reps r LEFT JOIN opportunities o ON o.rep_id=r.rep_id GROUP BY r.rep_id,r.rep,r.region,r.target,r.commission_rate;
