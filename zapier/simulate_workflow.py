"""Local idempotent Closed Won append simulation. No third-party writes."""
import csv,sqlite3,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def simulate(state):
    db=sqlite3.connect(state)
    db.execute('CREATE TABLE IF NOT EXISTS events(opportunity_id TEXT PRIMARY KEY,account TEXT,amount REAL,rep TEXT,close_date TEXT)')
    before=db.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    with (ROOT/'data/cleaned/opportunities.csv').open() as f:
        for r in csv.DictReader(f):
            if r['stage']=='Closed Won':db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?,?,?)',(r['opportunity_id'],r['account'],float(r['amount']),r['rep'],r['close_date']))
    db.commit();rows=db.execute('SELECT * FROM events ORDER BY opportunity_id').fetchall();added=len(rows)-before
    with (ROOT/'zapier/simulated_closed_won.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['opportunity_id','account','amount','rep','close_date']);w.writerows(rows)
    db.close();return added,len(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--state',default=str(ROOT/'zapier/local_state.sqlite'));a=p.parse_args();print(dict(zip(['added','total'],simulate(a.state))))
