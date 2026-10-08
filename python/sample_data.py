from pathlib import Path
import csv, json, random, datetime, copy, math

ROOT = Path(__file__).resolve().parents[1]
STAGES = {'Prospecting':.1,'Qualification':.25,'Needs Analysis':.4,'Proposal':.6,'Negotiation':.8,'Closed Won':1.,'Closed Lost':0.}
REGIONS = ['APAC','EMEA','North America','India']

def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def generate():
    rng=random.Random(42)
    reps=[dict(rep_id=f'REP{i:02}',rep=f'Representative {i:02}',region=REGIONS[(i-1)%4],target=450000,commission_rate=.05) for i in range(1,13)]
    accounts=[dict(account_id=f'ACC{i:03}',account=f'{["Alpha","Nova","Vertex","BluePeak","Orion","Summit"][i%6]} Systems {i:02}',region=REGIONS[(i-1)%4],industry=['Technology','Retail','Manufacturing'][i%3]) for i in range(1,41)]
    contacts=[dict(contact_id=f'CON{i:03}',account_id=accounts[(i-1)%40]['account_id'],contact=f'Contact {i:03}',email=f'contact{i}@example.invalid',job_title='Operations Manager') for i in range(1,81)]
    leads=[dict(lead_id=f'LEAD{i:03}',company=f'Prospect Company {i:03}',email=f'lead{i}@example.invalid',industry=['Technology','Retail','Manufacturing'][i%3],source=['Referral','Web','Partner','Outbound'][i%4],status=['New','Qualified','Working'][i%3],rep_id=reps[i%12]['rep_id']) for i in range(1,151)]
    opps=[]
    for i in range(1,301):
        rep=reps[(i-1)%12]; acc=rng.choice([a for a in accounts if a['region']==rep['region']])
        stage=rng.choices(list(STAGES),weights=[12,12,10,12,10,30,14])[0]
        close=datetime.date(2026,1,1)+datetime.timedelta(days=rng.randrange(273))
        created=close-datetime.timedelta(days=rng.randrange(12,91))
        opps.append(dict(opportunity_id=f'OPP{i:04}',opportunity=f'{acc["account"]} · {i:03}',account_id=acc['account_id'],account=acc['account'],rep_id=rep['rep_id'],rep=rep['rep'],region=acc['region'],product=rng.choice(['CRM Suite','Analytics Cloud','Automation Hub']),source=rng.choice(['Referral','Web','Partner','Outbound']),stage=stage,amount=rng.randrange(50,451)*100,probability=STAGES[stage],close_date=str(close),created_date=str(created)))
    dirty=copy.deepcopy(opps)
    dirty[7]['amount']=-5000;dirty[18]['close_date']='';dirty[25]['rep_id']='';dirty[39]['stage']='Unknown';dirty[61]['account_id']='ACC999';dirty[90]['close_date']='2026-02-30';dirty[111]['probability']=1.5
    for i in [42,66,86,143,192]:dirty[i]['region']=dirty[i]['region'].lower()+' '
    dirty.extend(copy.deepcopy(opps[:6]))
    raw_accounts=copy.deepcopy(accounts)+[dict(accounts[0],account_id='ACC-DUP',account=accounts[0]['account'].lower()+' ')]
    return accounts,raw_accounts,contacts,leads,reps,dirty

def clean(rows,accounts,reps):
    valid=[]; issues=[]; seen={}; account_ids={a['account_id'] for a in accounts}; rep_ids={r['rep_id'] for r in reps}
    conflicts=set(); first={}
    for row in rows:
        key=row['opportunity_id']
        if key in first and first[key]!=row:conflicts.add(key)
        first.setdefault(key,row)
    account_region={a['account_id']:a['region'] for a in accounts}; rep_region={r['rep_id']:r['region'] for r in reps}
    def issue(row,field,rule,resolution,severity='High',disposition='Quarantined'):
        issues.append(dict(record=row['opportunity_id'],input_row=len(seen),field=field,issue=rule,severity=severity,disposition=disposition,resolution=resolution,region=str(row['region']).strip().title()))
    for n,original in enumerate(rows,1):
        row=copy.deepcopy(original)
        if row['opportunity_id'] in conflicts:
            issue(row,'opportunity_id','Conflicting duplicate','All versions quarantined; manual review required');issues[-1]['input_row']=n;continue
        if row['opportunity_id'] in seen:
            if row==seen[row['opportunity_id']]:issue(row,'opportunity_id','Exact duplicate','Retained the first identical row','Medium','Removed')
            else:issue(row,'opportunity_id','Conflicting duplicate','Manual review required')
            issues[-1]['input_row']=n;continue
        seen[row['opportunity_id']]=copy.deepcopy(row)
        found=False
        for field,rule in [('amount','Non-negative amount'),('close_date','Valid close date'),('rep_id','Known owner'),('stage','Known sales stage'),('account_id','Known account'),('probability','Stage probability')]:
            ok=True
            if field=='amount':ok=isinstance(row[field],(int,float)) and math.isfinite(row[field]) and row[field]>=0
            elif field=='close_date':
                try:ok=datetime.date.fromisoformat(row[field])>=datetime.date.fromisoformat(row['created_date'])
                except ValueError:ok=False
            elif field=='rep_id':ok=row[field] in rep_ids
            elif field=='stage':ok=row[field] in STAGES
            elif field=='account_id':ok=row[field] in account_ids
            elif field=='probability':ok=row[field]==STAGES.get(row['stage'])
            if not ok:issue(row,field,rule,'Excluded from reporting; correction required');issues[-1]['input_row']=n;found=True
        region=next((r for r in REGIONS if r.lower()==str(row['region']).strip().lower()),None)
        if region is None:issue(row,'region','Known region','Manual review required');found=True
        elif row['region']!=region:issue(row,'region','Inconsistent formatting','Trimmed whitespace and mapped to canonical region','Low','Standardized');issues[-1]['input_row']=n;row['region']=region
        if region and row['account_id'] in account_region and region!=account_region[row['account_id']]:issue(row,'region','Account region mismatch','Manual review required');issues[-1]['input_row']=n;found=True
        if region and row['rep_id'] in rep_region and region!=rep_region[row['rep_id']]:issue(row,'region','Owner region mismatch','Manual review required');issues[-1]['input_row']=n;found=True
        if not found:
            row['expected_revenue']=round(row['amount']*row['probability'],2)
            row['won_revenue']=row['amount'] if row['stage']=='Closed Won' else 0
            row['month']=row['close_date'][:7];valid.append(row)
    return valid,issues

def build(root=ROOT):
    accounts,raw_accounts,contacts,leads,reps,raw=generate()
    valid,issues=clean(raw,accounts,reps)
    for name,rows in [('accounts',raw_accounts),('contacts',contacts),('leads',leads),('sales_reps',reps),('opportunities',raw)]:write_csv(root/'data/raw'/f'{name}.csv',rows)
    for name,rows in [('accounts',accounts),('contacts',contacts),('leads',leads),('sales_reps',reps),('opportunities',valid),('quality_exceptions',issues)]:write_csv(root/'data/cleaned'/f'{name}.csv',rows)
    comp=[]
    for rep in reps:
        deals=[r for r in valid if r['rep_id']==rep['rep_id']];won=[r for r in deals if r['stage']=='Closed Won'];lost=[r for r in deals if r['stage']=='Closed Lost'];actual=sum(r['amount'] for r in won)
        comp.append(dict(**rep,actual=actual,achievement=actual/rep['target'],won_deals=len(won),closed_deals=len(won)+len(lost),win_rate=len(won)/(len(won)+len(lost)) if won or lost else None,payout=round(actual*rep['commission_rate'],2)))
    write_csv(root/'data/cleaned/compensation.csv',comp)
    source=dict(label='Deterministic synthetic CRM portfolio data',classification='synthetic',tables=['data/cleaned/opportunities.csv'],coverage={'startDate':'2026-01-01','endDate':'2026-09-30'},evidenceFlow=[dict(title='Generate sample CRM',detail='python python/pipeline.py --regenerate; seed 42, fictional companies and reserved .invalid emails'),dict(title='Validate and quarantine',detail='python python/pipeline.py; required fields, IDs, dates, amounts, stage probabilities, duplicates and region standardization')],metricDefinitions=[dict(label='Won revenue',definition='Sum of amount for Closed Won opportunities in the selected close-date cohort, USD. Portfolio sales proxy, not recognized accounting revenue.'),dict(label='Open pipeline',definition='Sum of amount where stage is neither Closed Won nor Closed Lost. Current snapshot grouped by expected close month.'),dict(label='Win rate',definition='Won deal count / (won deal count + lost deal count). Open deals excluded.'),dict(label='Weighted pipeline',definition='Open amount × assumed stage probability. This is a scenario, not a validated forecast.')])
    snapshot=dict(title='Revenue operations & sales analytics',surface='dashboard',status='fixture',buildStatus='creating',generatedAt='2026-10-07T12:00:00Z',description='Portfolio simulation by Muthyala Mahesh Kumar',filters=[dict(id='region',label='Region',field='region',defaultValue='all'),dict(id='product',label='Product',field='product',defaultValue='all',queryIds=['opportunities']),dict(id='month',label='Close month',field='month',defaultValue='all',queryIds=['opportunities']),dict(id='rep',label='Sales representative',field='rep',defaultValue='all',queryIds=['opportunities','compensation'])],queries={'opportunities':dict(rows=valid,source=source),'compensation':dict(rows=comp,source=dict(label='Synthetic nine-month quotas and flat commission plan',classification='synthetic',tables=['data/cleaned/compensation.csv'],metricDefinitions=[dict(label='Quota attainment',definition='Jan–Sep won revenue / fixed nine-month USD quota. Quotas are portfolio assumptions.'),dict(label='Estimated payout',definition='Closed Won amount × flat 5% commission. No accelerators, returns, tax or FX.')])),'quality':dict(rows=issues,source=dict(label='Validation exception ledger',classification='synthetic',tables=['data/cleaned/quality_exceptions.csv'])),'quality_summary':dict(rows=[dict(raw_rows=len(raw),clean_rows=len(valid),duplicates=6,quarantined=300-len(valid),standardized=5,total_unique=300)],source=dict(label='Record-level reconciliation',classification='synthetic',tables=['data/raw/opportunities.csv','data/cleaned/opportunities.csv']))})
    (root/'src').mkdir(parents=True,exist_ok=True)
    (root/'src/data.json').write_text(json.dumps(snapshot,indent=2))
    return snapshot

