import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {metrics,scope,aggregate} from '../../src/content/dashboard/revenue-data.js';
const s=JSON.parse(fs.readFileSync(new URL('../../src/data.json',import.meta.url))),rows=s.queries.opportunities.rows;
test('Known independent portfolio totals and closed-deal denominator',()=>{const m=metrics(rows);assert.equal(m.revenue,10005534);assert.equal(m.pipeline,null);assert.equal(m.won,4238);assert.equal(m.closed,6711);assert.equal(m.winRate,4238/6711);});
test('Region slices reconcile and reset All restores population',()=>{const regions=[...new Set(rows.map(r=>r.region))];const total=regions.reduce((s,region)=>s+metrics(scope(rows,{region},['region'])).revenue,0);assert.equal(total,10005534);assert.equal(scope(rows,{region:'all'},['region']).length,8800);});
test('Filters intersect rather than broaden; an empty result has undefined rate',()=>{const cut=scope(rows,{region:'West',product:'GTX Pro',month:'2017-03'},['region','product','month']);assert.ok(cut.every(r=>r.region==='West'&&r.product==='GTX Pro'&&r.month==='2017-03'));assert.equal(metrics([]).winRate,null);assert.equal(metrics([]).average,null);});
test('Category bar total reconciles to won revenue',()=>{const won=rows.filter(r=>r.stage==='Closed Won');assert.equal(aggregate(won,'product','amount').reduce((s,r)=>s+r.amount,0),10005534);});

test('Open values stay unavailable and stages reconcile',()=>{const m=metrics(rows);assert.equal(m.open,2089);assert.equal(m.weighted,null);assert.ok(rows.filter(r=>!r.stage.startsWith('Closed')).every(r=>r.amount===null&&r.close_date===null));});
