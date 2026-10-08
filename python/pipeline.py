"""Offline portfolio pipeline; never writes to Salesforce or sends messages."""
from pathlib import Path
import argparse,csv,json
from sample_data import ROOT,build,clean,write_csv

def read(name):
    with (ROOT/'data/raw'/f'{name}.csv').open(newline='') as f:return list(csv.DictReader(f))

def run(regenerate=False):
    if not regenerate and (ROOT/'data/source/maven_crm/sales_pipeline.csv').exists():
        from maven_data import run as import_maven
        return import_maven()
    old=json.loads((ROOT/'src/data.json').read_text())
    if regenerate:build(ROOT)
    accounts=read('accounts');reps=read('sales_reps');raw=read('opportunities')
    # Exact duplicate company names are flagged, canonical IDs remain explicit.
    canonical=[];seen=set()
    for a in accounts:
        key=a['account'].strip().casefold()
        if key not in seen:canonical.append(a);seen.add(key)
    for r in reps:r['target']=float(r['target']);r['commission_rate']=float(r['commission_rate'])
    for r in raw:
        for key in ['amount','probability']:
            try:r[key]=float(r[key])
            except (ValueError,TypeError):r[key]=None
    valid,issues=clean(raw,canonical,reps)
    # Verify matching dimensions; quarantine unexpected region/owner/account joins.
    account_map={r['account_id']:r for r in canonical};rep_map={r['rep_id']:r for r in reps}
    for row in valid:
        row['account']=account_map[row['account_id']]['account'];row['rep']=rep_map[row['rep_id']]['rep']
    for name,rows in [('accounts',canonical),('sales_reps',reps),('opportunities',valid),('quality_exceptions',issues)]:
        if rows:write_csv(ROOT/'data/cleaned'/f'{name}.csv',rows)
        elif name=='quality_exceptions':
            (ROOT/'data/cleaned/quality_exceptions.csv').write_text('record,input_row,field,issue,severity,disposition,resolution,region\n')
        else:raise ValueError(f'No valid {name}; dashboard snapshot unchanged')
    comp=[]
    for rep in reps:
        if rep['target']<=0 or not 0<=rep['commission_rate']<=1:raise ValueError('Invalid compensation assumption')
        deals=[r for r in valid if r['rep_id']==rep['rep_id']];won=[r for r in deals if r['stage']=='Closed Won'];closed=[r for r in deals if r['stage'].startswith('Closed')];actual=sum(r['amount'] for r in won)
        comp.append(dict(**rep,actual=actual,achievement=actual/rep['target'],won_deals=len(won),closed_deals=len(closed),win_rate=len(won)/len(closed) if closed else None,payout=round(actual*rep['commission_rate'],2)))
    write_csv(ROOT/'data/cleaned/compensation.csv',comp)
    duplicate_rows=len(raw)-len({r['opportunity_id'] for r in raw})
    unique=len({r['opportunity_id'] for r in raw})
    summary=dict(raw_rows=len(raw),clean_rows=len(valid),duplicates=duplicate_rows,quarantined=unique-len(valid),standardized=sum(i['disposition']=='Standardized' for i in issues),total_unique=unique)
    old['queries']['opportunities']['rows']=valid;old['queries']['compensation']['rows']=comp;old['queries']['quality']['rows']=issues;old['queries']['quality_summary']['rows']=[summary]
    (ROOT/'src/data.json').write_text(json.dumps(old,indent=2))
    print(json.dumps(summary));return old
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--regenerate',action='store_true',help='Replace raw inputs with deterministic synthetic sample');run(p.parse_args().regenerate)
