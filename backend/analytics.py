"""Evidence-backed analytics. No model calls or guessed CRM fields."""
import csv, json, hashlib, os
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
AS_OF = '2017-12-31'  # historical snapshot, not today's live CRM

def read_csv_rows(name):
    with (ROOT / 'data/cleaned' / (name + '.csv')).open(newline='') as f:
        rows = list(csv.DictReader(f))
    numbers = {'amount','probability','expected_revenue','won_revenue','target','commission_rate','actual','achievement','payout','won_deals','closed_deals','win_rate'}
    for row in rows:
        for key, value in row.items():
            row[key] = None if value == '' else float(value) if key in numbers else value
    return rows

def read_rows(name):
    if os.getenv('REVENUE_STORAGE','csv') != 'postgres':return read_csv_rows(name)
    import psycopg
    from psycopg.rows import dict_row
    from decimal import Decimal
    # Closed table allowlist; no user-controlled SQL identifiers.
    tables={'accounts':'accounts','sales_reps':'sales_reps','contacts':'contacts','opportunities':'opportunities','compensation':'compensation'}
    if name not in tables:raise ValueError('Unsupported dataset')
    with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row) as connection:
        rows=connection.execute('SELECT * FROM '+tables[name]).fetchall()
    return [{k:float(v) if isinstance(v,Decimal) else v.isoformat() if isinstance(v,date) else v for k,v in row.items()} for row in rows]

def select(rows, filters=None):
    filters = filters or {}
    return [r for r in rows if all(not v or v == 'all' or r.get(k) == v for k,v in filters.items())]

def summary(rows):
    won = [r for r in rows if r['stage'] == 'Closed Won']
    closed = [r for r in rows if r['stage'].startswith('Closed')]
    opened = [r for r in rows if not r['stage'].startswith('Closed')]
    revenue = round(sum(r['amount'] for r in won), 2)
    return {'opportunities':len(rows), 'won_revenue':revenue, 'won_deals':len(won), 'closed_deals':len(closed), 'open_opportunities':len(opened), 'win_rate':len(won)/len(closed) if closed else None, 'average_won_deal':revenue/len(won) if won else None, 'open_pipeline_value':None if any(r['amount'] is None for r in opened) else sum(r['amount'] for r in opened), 'currency_code':None, 'display_currency':'USD (portfolio convention)', 'as_of':AS_OF}

def quality(rows):
    ids = Counter(r['opportunity_id'] for r in rows)
    opened = [r for r in rows if not r['stage'].startswith('Closed')]
    return {'rows':len(rows),'duplicate_ids':sum(n-1 for n in ids.values()),'missing_accounts':sum(r['account_id'] is None for r in rows),'open_without_amount':sum(r['amount'] is None for r in opened),'open_without_close_date':sum(r['close_date'] is None for r in opened),'negative_amounts':sum(r['amount'] is not None and r['amount']<0 for r in rows),'missing_owners':sum(not r['rep_id'] for r in rows),'missing_regions':sum(not r['region'] for r in rows),'invalid_stages':sum(r['stage'] not in {'Prospecting','Engaging','Qualification','Needs Analysis','Proposal','Negotiation','Closed Won','Closed Lost'} for r in rows),'invalid_date_order':sum(bool(r['close_date'] and r['created_date'] and r['close_date']<r['created_date']) for r in rows)}

def insights(rows, reps=None):
    """Rules are reproducible flags, not predictions or LLM-generated claims."""
    s, q = summary(rows), quality(rows)
    opened = [r for r in rows if not r['stage'].startswith('Closed')]
    aged = [r for r in opened if r['created_date'] and (date.fromisoformat(AS_OF)-date.fromisoformat(r['created_date'])).days > 90]
    result = []
    def add(key, category, severity, title, fact, action, count, metric, ids=()):
        result.append(dict(id=key,category=category,severity=severity,title=title,fact=fact,recommendation=action,count=count,metric=metric,evidence_ids=list(ids),engine='rules',as_of=AS_OF))
    if q['open_without_amount']:
        add('forecast-coverage','Data quality','High','Forecast value unavailable',f"{q['open_without_amount']:,} open opportunities have no amount. Expected close dates are also absent.",'Collect amount, probability and expected close date before publishing a monetary forecast.',q['open_without_amount'],'Missing open amounts',[r['opportunity_id'] for r in opened if r['amount'] is None])
    if q['missing_accounts']:
        missing = [r for r in rows if r['account_id'] is None]
        add('account-coverage','Data quality','High','Account assignment gaps',f"{len(missing):,} opportunities have no assigned account.",'Ask deal owners to verify account relationships; keep unresolved records in the exception queue.',len(missing),'Missing accounts',[r['opportunity_id'] for r in missing])
    if aged:
        add('engagement-age','Pipeline','Medium','Long-running engagements',f"{len(aged):,} open deals are more than 90 days past their engagement date at {AS_OF}. This is not days since last activity.",'Review next steps with owners and check actual activity before marking any deal stale.',len(aged),'Open engagements over 90 days',[r['opportunity_id'] for r in aged])
    monthly = defaultdict(float)
    for r in rows:
        if r['stage']=='Closed Won':monthly[r['month']]+=r['amount']
    months = sorted(monthly)
    if len(months)>1:
        current,previous = months[-1],months[-2]
        # Only consecutive calendar months may be described as month-over-month.
        a,b = date.fromisoformat(current+'-01'),date.fromisoformat(previous+'-01')
        if (a.year-b.year)*12+a.month-b.month == 1 and monthly[previous]:
            delta = (monthly[current]-monthly[previous])/monthly[previous]
            add('monthly-movement','Sales trend','Medium' if delta<0 else 'Info','Latest monthly movement',f"{current} won value is {monthly[current]:,.0f}, versus {monthly[previous]:,.0f} in {previous} ({delta:+.1%}). Source currency is unspecified.",'Compare product and representative mix; the change does not establish a cause.',sum(r['stage']=='Closed Won' and r['month']==current for r in rows),'Latest month won deals',[r['opportunity_id'] for r in rows if r['stage']=='Closed Won' and r['month'] in (current,previous)])
    if reps:
        actual = defaultdict(float)
        for r in rows:
            if r['stage']=='Closed Won':actual[r['rep_id']]+=r['amount']
        below = [r for r in reps if actual[r['rep_id']] < r['target']]
        add('scenario-targets','Scenario','Info','Illustrative target gaps',f"{len(below)} of {len(reps)} listed agents are below the assumed 500,000 annual target. Targets are portfolio assumptions.",'Validate real quotas and territories before evaluating performance or changing compensation.',len(below),'Agents below scenario target')
    if s['closed_deals']:
        add('closed-win-rate','Sales trend','Info','Closed-deal conversion',f"{s['won_deals']:,} of {s['closed_deals']:,} closed opportunities were won ({s['win_rate']:.1%}). Open deals are excluded.",'Inspect conversion by product and sales office; do not infer future win probabilities from this rate.',s['won_deals'],'Won deals')
    return result

def brief(rows, reps=None):
    findings = insights(rows,reps)
    return {'engine':'rules','llm_connected':False,'summary':summary(rows),'facts':[r['fact'] for r in findings],'risks':[r['fact'] for r in findings if r['severity'] in ('High','Medium')],'recommendations':[r['recommendation'] for r in findings[:3]],'findings':findings,'limitations':['Historical fictional CRM sample; not a live Salesforce feed.','Source currency code, open values, expected close dates, quotas and activity timestamps are unavailable.','Rule alerts are review prompts, not causal conclusions or predictions.']}

def evidence_fingerprint(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
