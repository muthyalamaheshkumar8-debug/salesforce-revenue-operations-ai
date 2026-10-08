"""Loads portable SQL model into SQLite, or PostgreSQL with optional psycopg."""
import csv,sqlite3,os,argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(postgres=False):
    if postgres:
        import psycopg
        conn=psycopg.connect(os.environ['DATABASE_URL']);placeholder='%s'
    else:
        conn=sqlite3.connect(':memory:');conn.execute('PRAGMA foreign_keys=ON');placeholder='?'
    cur=conn.cursor()
    for statement in (ROOT/'sql/schema.sql').read_text().split(';'):
        if statement.strip():cur.execute(statement)
    def insert(table,rows):
        if not rows:return
        keys=list(rows[0]);query=f'INSERT INTO {table} ({",".join(keys)}) VALUES ({",".join([placeholder]*len(keys))})'
        cur.executemany(query,[tuple(r[k] for k in keys) for r in rows])
    def read(name):
        with (ROOT/'data/cleaned'/f'{name}.csv').open() as f:return list(csv.DictReader(f))
    opps=read('opportunities')
    for r in opps:
        for k in ['account_id','account','amount','probability','close_date','created_date','expected_revenue']:
            if r[k]=='':r[k]=None
    insert('dim_accounts',read('accounts'));insert('dim_sales_reps',read('sales_reps'));insert('dim_contacts',read('contacts'))
    insert('dim_products',[{'product':p} for p in sorted({r['product'] for r in opps})]);insert('dim_date',[{'date_key':d,'month':d[:7]} for d in sorted({r['close_date'] for r in opps if r['close_date']})]);insert('fact_opportunities',opps)
    conn.commit();results={}
    for name in ['pipeline_analysis','sales_rep_analysis','revenue_analysis','regional_analysis','compensation_analysis']:
        cur.execute((ROOT/'sql'/f'{name}.sql').read_text());keys=[d[0] for d in cur.description];results[name]=[dict(zip(keys,row)) for row in cur.fetchall()]
    if not postgres:(ROOT/'documentation/sql_results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps({'engine':'postgresql' if postgres else 'sqlite','loaded_opportunities':len(opps),'queries_executed':len(results)}));conn.close();return results
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--postgres',action='store_true');load(p.parse_args().postgres)
