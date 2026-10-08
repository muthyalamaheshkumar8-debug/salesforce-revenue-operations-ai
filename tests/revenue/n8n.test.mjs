import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const workflow=JSON.parse(fs.readFileSync(new URL('../../n8n/high_value_opportunity.json',import.meta.url),'utf8'));
const code=workflow.nodes.find(n=>n.type==='n8n-nodes-base.code').parameters.jsCode;
const fixture={Id:'demo-1',StageName:'Negotiation',Amount:600000,CurrencyIsoCode:'INR',LastModifiedDate:'2026-10-01T00:00:00Z'};
const run=(opportunity,env={})=>vm.runInNewContext(`(function(){${code}})()`,{$env:env,$input:{all:()=>[{json:opportunity}]}});
test('workflow is inactive and every connected node exists',()=>{
 assert.equal(workflow.active,false);const names=new Set(workflow.nodes.map(n=>n.name));
 for(const [from,outputs] of Object.entries(workflow.connections)){assert.ok(names.has(from));for(const branch of outputs.main)for(const target of branch)assert.ok(names.has(target.node));}
 assert.equal(workflow.nodes[0].parameters.triggerOn,'opportunityUpdated');
});
test('high-value boundary and event identity',()=>{
 assert.equal(run({...fixture,Amount:500000})[0].json.high_value,true);
 assert.equal(run({...fixture,Amount:499999})[0].json.high_value,false);
 assert.equal(run(fixture)[0].json.event_id,'demo-1:2026-10-01T00:00:00Z');
});
test('missing fields, invalid amount and currency mismatch stop analysis',()=>{
 for(const patch of [{Amount:null},{Amount:'NaN'},{Amount:-1},{CurrencyIsoCode:'USD'},{Id:''},{Amount:''}])assert.throws(()=>run({...fixture,...patch}));
 assert.throws(()=>run(fixture,{HIGH_VALUE_THRESHOLD:'NaN'}));
});
