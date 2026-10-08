import unittest,json,sys,tempfile,copy,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'zapier'))
from sample_data import generate,clean
from load_database import load
from simulate_workflow import simulate
class PortfolioTests(unittest.TestCase):
 def test_quarantine_and_duplicate_reconciliation(self):
  a,_,_,_,r,raw=generate();valid,issues=clean(raw,a,r)
  self.assertEqual(len(raw),306);self.assertEqual(len(valid),293)
  self.assertNotIn('OPP0008',{v['opportunity_id'] for v in valid})
  self.assertEqual(len({v['opportunity_id'] for v in valid}),len(valid))
  self.assertEqual(sum(i['disposition']=='Removed' for i in issues),6)
 def test_conflicting_duplicates_are_never_reported(self):
  a,_,_,_,r,raw=generate();raw.append(dict(raw[0],amount=12345));valid,issues=clean(raw,a,r)
  self.assertNotIn(raw[0]['opportunity_id'],{v['opportunity_id'] for v in valid})
 def test_mismatched_region_is_quarantined(self):
  a,_,_,_,r,raw=generate();raw[10]['region']='India' if raw[10]['region']!='India' else 'APAC';valid,issues=clean(raw,a,r)
  self.assertNotIn(raw[10]['opportunity_id'],{v['opportunity_id'] for v in valid})
 def test_closed_lost_is_not_pipeline(self):
  s=json.loads((ROOT/'src/data.json').read_text());rows=s['queries']['opportunities']['rows'];won=[r for r in rows if r['stage']=='Closed Won']
  self.assertEqual(sum(r['amount'] for r in won),10005534)
  sql=load();self.assertEqual(sum(r['won_revenue'] for r in sql['revenue_analysis']),10005534)
  self.assertTrue(all(r['pipeline_value'] is None for r in sql['pipeline_analysis']))
 def test_commission_ledger(self):
  s=json.loads((ROOT/'src/data.json').read_text());comp=s['queries']['compensation']['rows']
  self.assertAlmostEqual(sum(r['payout'] for r in comp),500276.70)
  for r in comp:self.assertAlmostEqual(r['actual']*.05,r['payout']);self.assertGreater(r['target'],0)
 def test_workflow_retry(self):
  with tempfile.TemporaryDirectory() as d:
   first=simulate(str(Path(d)/'state.sqlite'));second=simulate(str(Path(d)/'state.sqlite'))
   self.assertEqual(first,(4238,4238));self.assertEqual(second,(0,4238))
if __name__=='__main__':unittest.main()
