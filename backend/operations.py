"""Authenticated rehearsal workflow. No payroll, CRM write or message delivery.

Deploy privately; use a durable OPERATIONS_STATE_PATH volume and rotate role tokens.
Token roles are service identities, not verified named human reviewers.
"""
import hashlib,json,os,secrets,sqlite3
from contextlib import contextmanager
from datetime import datetime,timezone
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
from typing import Literal
from fastapi import APIRouter,Depends,Header,HTTPException
from pydantic import BaseModel,ConfigDict,Field,field_validator
from backend.analytics import read_rows
from backend.events import analyze_event

router=APIRouter(prefix='/api/operations',tags=['Operations rehearsal'])
ROOT=Path(__file__).resolve().parents[1]
def now():return datetime.now(timezone.utc).isoformat()

def role(authorization:str|None=Header(default=None)):
    ops=os.getenv('OPERATIONS_API_TOKEN','');finance=os.getenv('FINANCE_API_TOKEN','')
    if not ops or not finance or secrets.compare_digest(ops,finance):
        raise HTTPException(503,'Configure distinct operations and finance tokens before enabling shared workflows.')
    for name,token in [('operations',ops),('finance',finance)]:
        if secrets.compare_digest(authorization or '', 'Bearer '+token):return name
    raise HTTPException(401,'Supply an authorized role bearer token.')

@contextmanager
def db():
    path=Path(os.getenv('OPERATIONS_STATE_PATH','/tmp/revenue-operations-workspace.sqlite'))
    path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(path,timeout=15);conn.row_factory=sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS ledgers (id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,document TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS receipts (id TEXT PRIMARY KEY,document TEXT NOT NULL)')
    conn.execute('BEGIN IMMEDIATE')
    try:
        yield conn;conn.commit()
    except Exception:
        conn.rollback();raise
    finally:conn.close()

def catalog(name):return json.loads((ROOT/'documentation'/f'{name}.json').read_text())

@router.get('/capabilities')
def capabilities():
    return {'requirements':catalog('requirement-coverage'),'source':'Included project assets',
            'external_execution_verified':False,'payment_connector':False}

@router.get('/knowledge')
def knowledge(q:str='',audience:str|None=None):
    return {'rows':[r for r in catalog('knowledge-repository') if (audience is None or audience==r['audience']) and q.lower() in (r['title']+' '+r['body']+' '+r['tags']).lower()]}

class LedgerRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    ledger_id:str=Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
    rate_bps:int=Field(default=500,ge=0,le=10000,strict=True)

@router.post('/ledgers')
def create_ledger(request:LedgerRequest,actor=Depends(role)):
    if actor!='operations':raise HTTPException(403,'The operations role calculates ledgers.')
    rows=[]
    for rep in read_rows('compensation'):
        basis=Decimal(str(rep['actual']))
        if not basis.is_finite() or basis<0:raise HTTPException(422,'Invalid source commission basis.')
        payout=(basis*Decimal(request.rate_bps)/Decimal(10000)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
        rows.append({'rep_id':rep['rep_id'],'rep':rep['rep'],'basis_cents':int((basis*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP)),'payout_cents':int(payout*100)})
    fingerprint=hashlib.sha256(json.dumps({'rows':rows,'rate_bps':request.rate_bps},sort_keys=True).encode()).hexdigest()
    document={'ledger_id':request.ledger_id,'status':'calculated','version':1,'scenario':True,'currency':None,'payment_issued':False,
              'rate_bps':request.rate_bps,'rows':rows,'total_cents':sum(r['payout_cents'] for r in rows),
              'audit':[{'action':'calculated','actor_role':actor,'at':now()}]}
    with db() as conn:
        old=conn.execute('SELECT fingerprint,document FROM ledgers WHERE id=?',(request.ledger_id,)).fetchone()
        if old:
            if old['fingerprint']!=fingerprint:raise HTTPException(409,'Ledger ID already refers to a different calculation.')
            return {**json.loads(old['document']),'duplicate':True}
        conn.execute('INSERT INTO ledgers VALUES (?,?,?)',(request.ledger_id,fingerprint,json.dumps(document)))
    return document

@router.get('/ledgers/{ledger_id}')
def get_ledger(ledger_id:str,actor=Depends(role)):
    with db() as conn:
        record=conn.execute('SELECT document FROM ledgers WHERE id=?',(ledger_id,)).fetchone()
        if not record:raise HTTPException(404,'Ledger not found.')
        return json.loads(record['document'])

class Transition(BaseModel):
    model_config=ConfigDict(extra='forbid')
    expected_version:int=Field(ge=1)
    target:Literal['reviewed','approved']
    note:str=Field(min_length=1,max_length=1000)

@router.post('/ledgers/{ledger_id}/transition')
def transition(ledger_id:str,request:Transition,actor=Depends(role)):
    required='finance' if request.target=='approved' else 'operations'
    if actor!=required:raise HTTPException(403,'This transition requires the '+required+' role.')
    with db() as conn:
        old=conn.execute('SELECT document FROM ledgers WHERE id=?',(ledger_id,)).fetchone()
        if not old:raise HTTPException(404,'Ledger not found.')
        document=json.loads(old['document'])
        if document['version']!=request.expected_version:raise HTTPException(409,'Ledger changed. Read its current version before retrying.')
        expected='reviewed' if request.target=='approved' else 'calculated'
        if document['status']!=expected:raise HTTPException(409,'Invalid workflow transition.')
        document['status']=request.target;document['version']+=1
        document['audit'].append({'action':request.target,'actor_role':actor,'at':now(),'note':request.note})
        conn.execute('UPDATE ledgers SET document=? WHERE id=?',(json.dumps(document),ledger_id))
    return document

class Receipt(BaseModel):
    model_config=ConfigDict(extra='forbid')
    receipt_id:str=Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
    requirement_id:str=Field(min_length=1,max_length=100)
    external_run_id:str=Field(min_length=1,max_length=200)
    note:str=Field(min_length=1,max_length=1000)

@router.post('/evidence')
def submit_receipt(request:Receipt,actor=Depends(role)):
    if actor!='operations':raise HTTPException(403,'The operations role submits receipts.')
    if request.requirement_id not in {r['id'] for r in catalog('requirement-coverage')}:raise HTTPException(422,'Unknown requirement.')
    document={**request.model_dump(),'submitted_at':now(),'verification':'self-attested; external run not independently verified'}
    with db() as conn:
        if conn.execute('SELECT 1 FROM receipts WHERE id=?',(request.receipt_id,)).fetchone():raise HTTPException(409,'Receipt ID already exists.')
        conn.execute('INSERT INTO receipts VALUES (?,?)',(request.receipt_id,json.dumps(document)))
    return document

@router.get('/evidence')
def receipts(actor=Depends(role)):
    with db() as conn:return {'rows':[json.loads(r['document']) for r in conn.execute('SELECT document FROM receipts ORDER BY id')]}

class OpportunityEvent(BaseModel):
    model_config=ConfigDict(extra='forbid')
    Id:str=Field(min_length=1,max_length=100)
    StageName:str=Field(min_length=1,max_length=100)
    Amount:Decimal=Field(ge=0,allow_inf_nan=False)
    CurrencyIsoCode:str=Field(pattern=r'^[A-Z]{3}$')
    LastModifiedDate:datetime

    @field_validator('LastModifiedDate')
    @classmethod
    def require_timezone(cls,value):
        if value.tzinfo is None:raise ValueError('A timezone-qualified source timestamp is required.')
        return value

class WebhookEvent(BaseModel):
    model_config=ConfigDict(extra='forbid')
    event_id:str=Field(min_length=1,max_length=200)
    opportunity:OpportunityEvent

@router.post('/webhooks/{platform}')
def automation_event(platform:Literal['zapier','n8n'],request:WebhookEvent,authorization:str|None=Header(default=None)):
    token=os.getenv('ANALYSIS_API_TOKEN','')
    if not token or not secrets.compare_digest(authorization or '', 'Bearer '+token):raise HTTPException(401,'Supply the analysis bearer token.')
    opportunity=request.opportunity.model_dump(mode='json')
    try:result=analyze_event({'event_id':platform+':'+request.event_id,'opportunity':opportunity,'mode':'rules'})
    except (ValueError,TypeError,KeyError) as error:raise HTTPException(422,'Invalid or conflicting event: '+str(error)) from error
    return {**result,'ingress':platform,'native_platform_execution_verified':False}
