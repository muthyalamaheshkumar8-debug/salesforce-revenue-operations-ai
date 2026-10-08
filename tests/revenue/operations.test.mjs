import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {parseRows,reviewEngagement,mapAcquisition,commissionLedger,gradeTraining} from '../../src/content/dashboard/operations-logic.js';
const snapshot=JSON.parse(fs.readFileSync(new URL('../../src/data.json',import.meta.url)));
const deals=snapshot.queries.opportunities.rows,reps=snapshot.queries.compensation.rows;
const deal=deals.find(r=>r.account_id);
test('engagement validates linkage, calendar dates and duplicate IDs',()=>{
  const row={activity_id:'practice-call',opportunity_id:deal.opportunity_id,activity_date:'2026-10-01',type:'call',outcome:'completed',next_step:'Review handoff'};
  assert.equal(reviewEngagement([row],'Gong',deals).accepted.length,1);
  assert.equal(reviewEngagement([row,row],'Gong',deals).exceptions.length,1);
  for(const patch of [{opportunity_id:'missing'},{activity_date:'2026-02-30'},{next_step:''},{type:'email'}])assert.equal(reviewEngagement([{...row,...patch}],'Gong',deals).exceptions.length,1);
  assert.equal(reviewEngagement([{...row,type:'email'}],'Apollo',deals).accepted.length,1);
});
test('migration gate preserves existing CRM and blocks incomplete batches',()=>{
  const before=JSON.stringify(deals);
  const row={legacy_id:'legacy-001',account_id:deal.account_id,rep_id:deal.rep_id,stage:'Closed Won',amount:1200,currency:'USD',close_date:'2026-10-01'};
  const good=mapAcquisition([row],deals,reps,'new-business');
  assert.equal(good.commit_allowed,true);assert.equal(good.crm_written,false);
  assert.equal(good.accepted[0].opportunity_id,'new-business:legacy-001');
  assert.equal(mapAcquisition([],deals,reps,'new-business').commit_allowed,false);
  for(const patch of [{amount:null},{amount:''},{amount:'NaN'},{amount:-1},{account_id:'missing'},{rep_id:'missing'},{stage:'unknown'},{currency:''},{close_date:'2026-02-30'}])assert.equal(mapAcquisition([{...row,...patch}],deals,reps,'new-business').commit_allowed,false);
  assert.equal(mapAcquisition([row,row],deals,reps,'new-business').exceptions.length,1);
  assert.equal(JSON.stringify(deals),before);
});
test('per-representative cents reconcile with the full 5% scenario',()=>{
  const rows=commissionLedger(reps,500);assert.equal(rows.length,35);
  assert.equal(rows.reduce((s,r)=>s+r.payout_cents,0),50027670);
  assert.equal(commissionLedger([{rep_id:'r',rep:'Practice',actual:0.1}],500)[0].payout_cents,1);
  for(const rate of [-1,10001,2.5,NaN])assert.throws(()=>commissionLedger(reps,rate));
});
test('assessment requires all correct answers and never claims real team training',()=>{
  const c=snapshot.queries.training.rows[0];
  assert.equal(gradeTraining(c,{}).passed,false);
  assert.equal(gradeTraining(c,{0:1}).passed,false);
  assert.equal(gradeTraining(c,{0:1,1:2}).passed,true);
});
test('all requested requirements have artifacts without unsupported verification',()=>{
  const rows=snapshot.queries.requirements.rows;assert.equal(rows.length,16);
  for(const r of rows){assert.equal(r.external_verified,false);assert.ok(fs.existsSync(new URL('../../'+r.artifact,import.meta.url)),r.artifact);}
  assert.throws(()=>parseRows('{}'));assert.throws(()=>parseRows('[null]'));assert.throws(()=>parseRows('['));
});
