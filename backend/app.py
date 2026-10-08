"""Run: uvicorn backend.app:app --host 127.0.0.1 --port 8000.
Read-only sample APIs; POST analysis requires a configured bearer token.
"""
import os, secrets
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from backend.analytics import read_rows, select, summary, quality, insights, brief

app = FastAPI(title='Salesforce Revenue Operations AI',version='1.0.0')
from backend.operations import router as operations_router
app.include_router(operations_router)

def data(region=None,rep=None,product=None,month=None):
    return select(read_rows('opportunities'),{'region':region,'rep':rep,'product':product,'month':month})

@app.get('/api/sales')
def sales(region:str|None=None,rep:str|None=None,product:str|None=None,month:str|None=None,limit:int=Query(100,ge=1,le=1000),offset:int=Query(0,ge=0)):
    rows=data(region,rep,product,month)
    return {'summary':summary(rows),'total':len(rows),'rows':rows[offset:offset+limit],'limit':limit,'offset':offset,'source':'Maven Analytics fictional CRM sample'}

@app.get('/api/pipeline')
def pipeline(region:str|None=None,rep:str|None=None,product:str|None=None):
    rows=data(region,rep,product)
    opened=[r for r in rows if not r['stage'].startswith('Closed')]
    return {'summary':summary(rows),'stage_counts':{stage:sum(r['stage']==stage for r in opened) for stage in sorted({r['stage'] for r in opened})},'amount_available':all(r['amount'] is not None for r in opened)}

@app.get('/api/reps')
def reps(region:str|None=None,rep:str|None=None):
    return {'rows':select(read_rows('compensation'),{'region':region,'rep':rep}),'target_is_scenario':True,'commission_is_scenario':True}

@app.get('/api/insights')
def get_insights(region:str|None=None,rep:str|None=None,product:str|None=None):
    rows=data(region,rep,product)
    return brief(rows,select(read_rows('sales_reps'),{'region':region,'rep':rep}) if not product else None)

@app.get('/api/data-quality')
def get_quality(region:str|None=None):
    return quality(data(region))

class AnalyzeRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    mode:Literal['rules','llm']='rules'
    region:Literal['East','West','Central']|None=None
    opportunity:dict|None=None
    event_id:str|None=Field(default=None,max_length=200)

@app.post('/api/analyze')
def analyze(request:AnalyzeRequest,authorization:str|None=Header(default=None)):
    token=os.getenv('ANALYSIS_API_TOKEN')
    if not token or not secrets.compare_digest(authorization or '', 'Bearer '+token):
        raise HTTPException(401,'Configure ANALYSIS_API_TOKEN and supply its bearer token.')
    rows=data(request.region)
    if request.opportunity is not None:
        from backend.events import analyze_event
        try:return analyze_event(request.model_dump())
        except ValueError as e:raise HTTPException(422,str(e)) from e
    evidence=brief(rows)
    if request.mode=='rules':return evidence
    if not os.getenv('OPENAI_API_KEY') or not os.getenv('LLM_MODEL'):
        raise HTTPException(503,'LLM not connected. Configure OPENAI_API_KEY and LLM_MODEL; use rules mode meanwhile.')
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('revenue_ai_chain',str(__import__('pathlib').Path(__file__).resolve().parents[1]/'langchain/revenue_chain.py'))
    module=module_from_spec(spec);spec.loader.exec_module(module)
    try:return module.analyze(evidence)
    except Exception as e:raise HTTPException(502,'Model analysis failed; no result was approved or stored.') from e
