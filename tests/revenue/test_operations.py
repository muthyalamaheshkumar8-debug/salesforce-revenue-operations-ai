import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app import app

class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.patch=patch.dict(os.environ,{'OPERATIONS_API_TOKEN':'ops-test-only','FINANCE_API_TOKEN':'finance-test-only','ANALYSIS_API_TOKEN':'analysis-test-only','OPERATIONS_STATE_PATH':str(Path(self.temp.name)/'workspace.sqlite'),'WORKFLOW_STATE_PATH':str(Path(self.temp.name)/'events.sqlite'),'WORKFLOW_CURRENCY':'INR','HIGH_VALUE_THRESHOLD':'500000'})
        self.patch.start();self.client=TestClient(app)
        self.ops={'Authorization':'Bearer ops-test-only'};self.finance={'Authorization':'Bearer finance-test-only'}
    def tearDown(self):self.patch.stop();self.temp.cleanup()
    def create(self,rate=500):return self.client.post('/api/operations/ledgers',json={'ledger_id':'practice-001','rate_bps':rate},headers=self.ops)
    def test_role_configuration_and_access(self):
        self.assertEqual(self.client.post('/api/operations/ledgers',json={'ledger_id':'x'}).status_code,401)
        self.assertEqual(self.client.post('/api/operations/ledgers',json={'ledger_id':'x'},headers=self.finance).status_code,403)
        with patch.dict(os.environ,{'FINANCE_API_TOKEN':'ops-test-only'}):self.assertEqual(self.create().status_code,503)
    def test_reconciliation_deduplication_and_conflict(self):
        response=self.create();self.assertEqual(response.status_code,200);ledger=response.json()
        self.assertEqual(ledger['total_cents'],50027670);self.assertEqual(len(ledger['rows']),35)
        self.assertIsNone(ledger['currency']);self.assertFalse(ledger['payment_issued'])
        self.assertTrue(self.create().json()['duplicate'])
        self.assertEqual(self.create(300).status_code,409)
        self.assertEqual(self.client.post('/api/operations/ledgers',json={'ledger_id':'x','rate_bps':500.5},headers=self.ops).status_code,422)
    def test_separate_roles_and_optimistic_transitions(self):
        self.create();url='/api/operations/ledgers/practice-001/transition'
        request={'expected_version':1,'target':'approved','note':'Practice approval'}
        self.assertEqual(self.client.post(url,json=request,headers=self.ops).status_code,403)
        self.assertEqual(self.client.post(url,json=request,headers=self.finance).status_code,409)
        request.update(target='reviewed')
        reviewed=self.client.post(url,json=request,headers=self.ops);self.assertEqual(reviewed.status_code,200)
        self.assertEqual(self.client.post(url,json=request,headers=self.ops).status_code,409)
        request.update(target='approved',expected_version=2)
        approved=self.client.post(url,json=request,headers=self.finance).json()
        self.assertEqual(approved['status'],'approved');self.assertEqual(approved['version'],3)
        self.assertFalse(approved['payment_issued']);self.assertEqual(len(approved['audit']),3)
        self.assertEqual(self.client.get('/api/operations/ledgers/practice-001',headers=self.finance).json(),approved)
    def test_evidence_does_not_promote_external_verification(self):
        receipt={'receipt_id':'receipt-1','requirement_id':'zapier','external_run_id':'user-entered-run','note':'Self-attested example'}
        r=self.client.post('/api/operations/evidence',json=receipt,headers=self.ops)
        self.assertEqual(r.status_code,200);self.assertIn('not independently verified',r.json()['verification'])
        self.assertEqual(self.client.post('/api/operations/evidence',json=receipt,headers=self.ops).status_code,409)
        receipt.update(receipt_id='receipt-2',requirement_id='missing')
        self.assertEqual(self.client.post('/api/operations/evidence',json=receipt,headers=self.ops).status_code,422)
        self.assertFalse(self.client.get('/api/operations/capabilities').json()['external_execution_verified'])
    def test_platform_receivers_validate_auth_currency_and_retry(self):
        payload={'event_id':'practice-1','opportunity':{'Id':'sample-1','StageName':'Negotiation','Amount':600000,'CurrencyIsoCode':'INR','LastModifiedDate':'2026-10-01T00:00:00Z'}}
        headers={'Authorization':'Bearer analysis-test-only'}
        for platform in ['zapier','n8n']:
            url='/api/operations/webhooks/'+platform
            self.assertEqual(self.client.post(url,json=payload).status_code,401)
            first=self.client.post(url,json=payload,headers=headers).json()
            self.assertEqual(first['status'],'stored');self.assertFalse(first['native_platform_execution_verified'])
            self.assertEqual(self.client.post(url,json=payload,headers=headers).json()['status'],'duplicate')
            wrong=json.loads(json.dumps(payload));wrong['opportunity']['Amount']=700000
            self.assertEqual(self.client.post(url,json=wrong,headers=headers).status_code,422)
            wrong['opportunity']['CurrencyIsoCode']='USD'
            self.assertEqual(self.client.post(url,json=wrong,headers=headers).status_code,422)
            invalid=json.loads(json.dumps(payload));invalid['opportunity']['LastModifiedDate']='2026-10-01T00:00:00'
            self.assertEqual(self.client.post(url,json=invalid,headers=headers).status_code,422)
            invalid['opportunity']['Amount']='NaN'
            self.assertEqual(self.client.post(url,json=invalid,headers=headers).status_code,422)
    def test_knowledge_search_and_complete_coverage(self):
        self.assertEqual(len(self.client.get('/api/operations/capabilities').json()['requirements']),16)
        rows=self.client.get('/api/operations/knowledge?q=Apollo').json()['rows']
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['id'],'KB-002')

if __name__=='__main__':unittest.main()
