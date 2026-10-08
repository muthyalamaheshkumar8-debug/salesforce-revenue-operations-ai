"""Validated opportunity event processing with durable idempotency.
No notification is sent; an outbox record is queued for review.
"""
import hashlib,json,os,sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

def validate_event(payload):
    opportunity=payload.get('opportunity')
    if not isinstance(opportunity,dict):raise ValueError('Opportunity must be an object')
    required=['Id','StageName','Amount','CurrencyIsoCode','LastModifiedDate']
    if any(opportunity.get(k) is None for k in required):raise ValueError('Missing required opportunity fields')
    try:amount=Decimal(str(opportunity['Amount']))
    except InvalidOperation:raise ValueError('Invalid amount')
    if not amount.is_finite() or amount<0:raise ValueError('Amount must be finite and non-negative')
    configured=os.getenv('WORKFLOW_CURRENCY','INR')
    if opportunity['CurrencyIsoCode']!=configured:raise ValueError('Currency mismatch; no implicit FX conversion')
    threshold=Decimal(os.getenv('HIGH_VALUE_THRESHOLD','500000'))
    if not threshold.is_finite() or threshold<0:raise ValueError('Invalid configured threshold')
    return opportunity,amount,threshold

def analyze_event(payload,state_path=None):
    opportunity,amount,threshold=validate_event(payload)
    if amount<threshold:return {'status':'below_threshold','engine':'rules','notification_sent':False}
    event_id=payload.get('event_id') or opportunity['Id']+':'+opportunity['LastModifiedDate']
    fingerprint=hashlib.sha256(json.dumps(opportunity,sort_keys=True).encode()).hexdigest()
    path=Path(state_path or os.getenv('WORKFLOW_STATE_PATH','/tmp/revenue-operations-events.sqlite'))
    conn=sqlite3.connect(path)
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,result TEXT NOT NULL)')
        conn.execute('BEGIN IMMEDIATE')
        old=conn.execute('SELECT fingerprint,result FROM events WHERE event_id=?',(event_id,)).fetchone()
        if old:
            if old[0]!=fingerprint:raise ValueError('Conflicting payload for the same event ID')
            return {**json.loads(old[1]),'status':'duplicate'}
        evidence={'facts':[f"Opportunity {opportunity['Id']} has amount {amount} {opportunity['CurrencyIsoCode']} and stage {opportunity['StageName']}.",f"Configured high-value threshold is {threshold} {opportunity['CurrencyIsoCode']}."],'risks':['Amount alone does not establish likelihood of closing.'],'recommendations':['Confirm next step, owner and expected close date before escalation.']}
        if payload.get('mode')=='llm':
            if not os.getenv('OPENAI_API_KEY') or not os.getenv('LLM_MODEL'):raise ValueError('LLM credentials and model are not configured')
            from importlib.util import spec_from_file_location,module_from_spec
            spec=spec_from_file_location('revenue_ai_chain',str(Path(__file__).resolve().parents[1]/'langchain/revenue_chain.py'));module=module_from_spec(spec);spec.loader.exec_module(module)
            evidence=module.analyze(evidence)
        result={'status':'stored','event_id':event_id,'engine':payload.get('mode','rules'),'analysis':evidence,'notification_sent':False,'outbox_status':'awaiting_review'}
        conn.execute('INSERT INTO events VALUES (?,?,?)',(event_id,fingerprint,json.dumps(result)));conn.commit()
        return result
    finally:conn.close()
