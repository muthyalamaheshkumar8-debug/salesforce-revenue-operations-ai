"""Import the public Maven CRM sample without inventing missing observations."""
import csv,json,hashlib,collections
from pathlib import Path
from datetime import date,datetime,timezone
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
SOURCE_URL='https://mavenanalytics.io/data-playground/crm-sales-opportunities'
MIRROR='https://raw.githubusercontent.com/ZeinabBagherifard/CRM-Sales-Opportunities/master/'
EXPECTED={'sales_pipeline.csv':'02f44c2ccd46a1c7d7c1d2e568a7504c15560e11b3cdb330a0a8229a1a365421','accounts.csv':'7afe89404278290bc774d8d3f50f16abdc58ccfc6c4288bff23b74fc451abfef','products.csv':'5fb985638d44d53fa3b36276372dd9f5c3d1897a85822c92668e1b47f43167c5','sales_teams.csv':'e97c6d82adc829c2d340f44425b05f0fd50f07e55d60414889e7630bef6da531','data_dictionary.csv':'63ef4f284980ed75526f1f5bab25846e8ba75107ff7d877f151e2021ba355141'}
def read(name):
    p=ROOT/'data/source/maven_crm'/name
    if hashlib.sha256(p.read_bytes()).hexdigest()!=EXPECTED[name]:raise ValueError(f'Source changed: review {name} before importing')
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(name,rows,fields=None):
    for directory in ['data/raw','data/cleaned']:
        p=ROOT/directory/(name+'.csv');p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def run():
    raw=read('sales_pipeline.csv');teams=read('sales_teams.csv');accts=read('accounts.csv');products=read('products.csv');read('data_dictionary.csv')
    if len(raw)!=8800 or len({r['opportunity_id'] for r in raw})!=8800:raise ValueError('Unexpected source count or duplicate opportunity IDs')
    amap={r['account']:dict(account_id=f'A{i+1:03}',account=r['account'],region=r['office_location'],industry=r['sector']) for i,r in enumerate(accts)}
    rmap={r['sales_agent']:dict(rep_id=f'R{i+1:03}',rep=r['sales_agent'],region=r['regional_office'],target=500000,commission_rate=.05) for i,r in enumerate(teams)}
    pnames={r['product'] for r in products};issues=[];rows=[]
    def issue(r,n,field,rule,resolution,disposition='Retained',severity='Info'):
        issues.append(dict(record=r['opportunity_id'],input_row=n,field=field,issue=rule,severity=severity,disposition=disposition,resolution=resolution,region=rmap[r['sales_agent']]['region']))
    for n,r in enumerate(raw,1):
        if r['sales_agent'] not in rmap:raise ValueError('Unknown agent')
        product='GTX Pro' if r['product']=='GTXPro' else r['product']
        if product not in pnames:raise ValueError('Unknown product')
        if product!=r['product']:issue(r,n,'product','Product-key mismatch','GTXPro mapped to GTX Pro; original retained in source CSV','Standardized','Low')
        stage={'Won':'Closed Won','Lost':'Closed Lost','Engaging':'Engaging','Prospecting':'Prospecting'}[r['deal_stage']]
        closed=stage.startswith('Closed');amount=float(Decimal(r['close_value'])) if r['close_value'] else None
        engage=r['engage_date'] or None;close=r['close_date'] or None
        if closed and (amount is None or not engage or not close):raise ValueError('Incomplete closed deal')
        if amount is not None and amount<0:raise ValueError('Negative close value')
        for value in [engage,close]:
            if value:date.fromisoformat(value)
        if close and engage and close<engage:raise ValueError('Close precedes engagement')
        account=amap.get(r['account']);rep=rmap[r['sales_agent']]
        if r['account'] and not account:raise ValueError('Unknown account')
        if not account:issue(r,n,'account','Account not assigned','Retained open opportunity; account value remains null')
        rows.append(dict(opportunity_id=r['opportunity_id'],opportunity=r['opportunity_id'],account_id=account['account_id'] if account else None,account=r['account'] or None,rep_id=rep['rep_id'],rep=rep['rep'],region=rep['region'],product=product,source='Maven CRM public sample',stage=stage,amount=amount,probability=1 if stage=='Closed Won' else 0 if stage=='Closed Lost' else None,created_date=engage,close_date=close,expected_revenue=None,won_revenue=amount if stage=='Closed Won' else 0,month=close[:7] if close else 'Not closed'))
    comp=[]
    for rep in rmap.values():
        deals=[r for r in rows if r['rep_id']==rep['rep_id']];won=[r for r in deals if r['stage']=='Closed Won'];closed=[r for r in deals if r['stage'].startswith('Closed')];actual=sum(r['amount'] for r in won)
        comp.append(dict(**rep,actual=actual,achievement=actual/rep['target'],won_deals=len(won),closed_deals=len(closed),win_rate=len(won)/len(closed) if closed else None,payout=float(Decimal(str(actual))*Decimal('.05'))))
    summary=dict(raw_rows=len(raw),clean_rows=len(rows),duplicates=0,quarantined=0,standardized=sum(i['disposition']=='Standardized' for i in issues),total_unique=len(rows),missing_accounts=sum(not r['account'] for r in rows),open_without_value=sum(r['amount'] is None for r in rows))
    for name,rs in [('accounts',list(amap.values())),('sales_reps',list(rmap.values())),('opportunities',rows),('quality_exceptions',issues),('compensation',comp)]:write(name,rs)
    write('contacts',[],['contact_id','account_id','contact','email','job_title']);write('leads',[],['lead_id','company','industry','source','status','rep_id'])
    s=json.loads((ROOT/'src/data.json').read_text());s.update(buildStatus='updating',generatedAt=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),description='Public CRM sample analysis by Muthyala Mahesh Kumar')
    links=[dict(label='Maven Analytics — dataset and license',url=SOURCE_URL),dict(label='CSV data mirror',url='https://github.com/ZeinabBagherifard/CRM-Sales-Opportunities')]
    src=dict(label='Maven Analytics CRM Sales Opportunities — public fictional sample',classification='synthetic',links=links,coverage=dict(startDate='2017-01-01',endDate='2017-12-31'),tables=['data/source/maven_crm/sales_pipeline.csv','data/source/maven_crm/sales_teams.csv'],evidenceFlow=[dict(title='Download source CSVs',detail=MIRROR+'; download only the five CSVs; exact SHA-256 checks are in python/maven_data.py'),dict(title='Validate and join',detail='python python/pipeline.py; unique IDs, agent/account/product relationships, closed-deal values and date ordering; preserve open-deal nulls; normalize GTXPro to GTX Pro')],metricDefinitions=[dict(label='Won revenue',definition='Sum of source close_value for Won deals, all closing in 2017. Dollar display is a portfolio currency convention; source does not specify a currency code.'),dict(label='Open opportunities',definition='Count of Engaging and Prospecting rows. Open amounts and expected close dates are absent; no monetary pipeline estimate.'),dict(label='Win rate',definition='Won / (Won + Lost), excluding all open deals.'),dict(label='Average engagement-to-close',definition='Mean close_date minus engage_date for Won deals, in calendar days. Not creation-to-close.')])
    s['queries']['opportunities']=dict(rows=rows,source=src,methods=[dict(language='python',code='python python/pipeline.py')])
    scenario=src | dict(label='Portfolio compensation scenario applied to Maven won values',tables=['data/cleaned/compensation.csv'],metricDefinitions=[dict(label='Scenario attainment',definition='2017 won value / assumed $500,000 annual target per each of 35 listed agents; no quotas are supplied by the dataset.'),dict(label='Estimated payout',definition='5% of source Won close_value. Portfolio scenario, not actual compensation.')])
    s['queries']['compensation']=dict(rows=comp,source=scenario)
    for q,rs,label in [('quality',issues,'Source standardization and retained missing fields'),('quality_summary',[summary],'Full 8,800-row source reconciliation')]:s['queries'][q]=dict(rows=rs,source=src | dict(label=label,tables=['data/source/maven_crm/sales_pipeline.csv','data/cleaned/quality_exceptions.csv']))
    for f in s['filters']:
        if f['id']=='region':f.update(label='Sales office',queryIds=['opportunities','compensation'])
    (ROOT/'src/data.json').write_text(json.dumps(s,indent=2))
    receipt=dict(dataset=SOURCE_URL,mirror=MIRROR,files=EXPECTED,summary=summary,won_value=sum(r['amount'] for r in rows if r['stage']=='Closed Won'),won_deals=4238,lost_deals=2473,open_deals=2089)
    (ROOT/'documentation/source-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt));return s
if __name__=='__main__':run()
