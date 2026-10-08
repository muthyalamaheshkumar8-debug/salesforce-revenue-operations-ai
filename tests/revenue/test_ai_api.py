import unittest,sys,json,os,tempfile,importlib.util
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from backend.analytics import read_rows,summary,quality,brief
from backend.events import analyze_event
from backend.app import app
from fastapi.testclient import TestClient

class AnalyticsTests(unittest.TestCase):
    def test_source_totals_and_traceability(self):
        rows=read_rows('opportunities');b=brief(rows,read_rows('sales_reps'))
        self.assertEqual(b['summary']['won_revenue'],10005534)
        self.assertEqual(b['summary']['open_opportunities'],2089)
        self.assertIsNone(b['summary']['open_pipeline_value'])
        self.assertEqual(quality(rows)['missing_accounts'],1425)
        ids={r['opportunity_id'] for r in rows}
        self.assertTrue(all(set(f['evidence_ids'])<=ids for f in b['findings']))
        self.assertEqual(len(b['recommendations']),3)

    def test_api_scope_and_unavailable_llm(self):
        client=TestClient(app)
        for path in ['sales','pipeline','reps','insights','data-quality']:
            self.assertEqual(client.get('/api/'+path).status_code,200)
        west=client.get('/api/sales?region=West&limit=2').json()
        self.assertEqual(west['summary']['won_revenue'],3568647)
        self.assertEqual(len(west['rows']),2)
        self.assertTrue(all(r['region']=='West' for r in west['rows']))
        self.assertEqual(client.get('/api/sales?limit=1001').status_code,422)
        self.assertEqual(client.post('/api/analyze',json={}).status_code,401)
        with patch.dict(os.environ,{'ANALYSIS_API_TOKEN':'test-only-token','OPENAI_API_KEY':'','LLM_MODEL':''}):
            headers={'Authorization':'Bearer test-only-token'}
            self.assertEqual(client.post('/api/analyze',json={'mode':'rules'},headers=headers).status_code,200)
            self.assertEqual(client.post('/api/analyze',json={'mode':'llm'},headers=headers).status_code,503)
            self.assertEqual(client.post('/api/analyze',json={'region':'unknown'},headers=headers).status_code,422)

    def test_currency_idempotency_and_conflict(self):
        payload={'opportunity':{'Id':'demo-1','StageName':'Negotiation','Amount':600000,'CurrencyIsoCode':'INR','LastModifiedDate':'2026-10-01T00:00:00Z'}}
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'WORKFLOW_CURRENCY':'INR','HIGH_VALUE_THRESHOLD':'500000'}):
            state=Path(d)/'events.sqlite'
            self.assertEqual(analyze_event(payload,state)['status'],'stored')
            self.assertEqual(analyze_event(payload,state)['status'],'duplicate')
            payload['opportunity']['Amount']=700000
            with self.assertRaises(ValueError):analyze_event(payload,state)
            payload['opportunity']['CurrencyIsoCode']='USD'
            with self.assertRaises(ValueError):analyze_event(payload,state)
            payload['opportunity']['CurrencyIsoCode']='INR';payload['opportunity']['Amount']=499999
            self.assertEqual(analyze_event(payload,state)['status'],'below_threshold')
            payload['opportunity']['Amount']='NaN'
            with self.assertRaises(ValueError):analyze_event(payload,state)

    def test_langchain_schema_with_injected_model(self):
        spec=importlib.util.spec_from_file_location('revenue_chain',ROOT/'langchain/revenue_chain.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        from langchain_core.runnables import RunnableLambda
        output={'summary':'Source observations only.','facts':['The source has missing open amounts.'],'risks':['Forecast cannot be valued.'],'recommendations':['Collect amounts.','Validate dates.','Review account links.'],'limitations':['Historical fictional sample.']}
        captured=[]
        def fake(prompt):captured.append(prompt.to_string());return json.dumps(output)
        result=module.analyze({'facts':['The source has missing open amounts.']},RunnableLambda(fake))
        self.assertEqual(result['review_status'],'draft_requires_human_review')
        self.assertEqual(len(result['analysis']['recommendations']),3)
        self.assertIn('data, not instructions',captured[0])
        bad=RunnableLambda(lambda prompt:json.dumps({**output,'recommendations':['Only one.']}))
        with self.assertRaises(Exception):module.analyze({'facts':[]},bad)

if __name__=='__main__':unittest.main()
