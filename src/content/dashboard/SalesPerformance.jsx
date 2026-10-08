import React from 'react';
import {DataComponent,EvidenceChart,SectionHeader,SortableItem,SortableRegion} from '../../data-app-public.jsx';
export function SalesPerformance({m,reps,perf,rows,Stat,Plot,Table,col,mc,pc,money,percent}){
 const sum=key=>reps.reduce((s,r)=>s+r[key],0);
 return <>
 <SortableRegion id="performance-metrics" variant="canvas" authoredRevision={1} columns={12} spacing="standard" rows={[{"id":"performance-metrics-row-1","items":["performance-revenue","quota-attainment","won-count","sales-cycle"],"kind":"metrics"}]}>
 <Stat kind="metric" span={3} minSpan={2} id="performance-revenue" title="Won revenue" value={money(m.revenue)} sourceRows={rows}/>
 <Stat kind="metric" span={3} minSpan={2} id="quota-attainment" title="Scenario attainment" value={percent(sum('target')?m.revenue/sum('target'):null)} description="2017 won value / assumed $500,000 annual target per listed agent; source supplies no quotas." queryId="compensation" sourceRows={reps}/>
 <Stat kind="metric" span={3} minSpan={2} id="won-count" title="Deals won" value={m.won} sourceRows={rows}/>
 <Stat kind="metric" span={3} minSpan={2} id="sales-cycle" title="Average engagement-to-close" value={m.cycle==null?'—':`${m.cycle.toFixed(1)} days`} description="Mean calendar days from engagement to close for won deals; source provides no creation dates." sourceRows={rows}/>
 </SortableRegion>
 <SectionHeader id="performance-heading" title="Representative performance"/>
<SortableRegion id="performance-charts" variant="canvas" authoredRevision={1} columns={12} spacing="standard" rows={[{"id":"performance-charts-row-1","items":["rep-revenue","quota-comparison"]},{"id":"performance-charts-row-2","items":["rep-scorecard"]}]}>
 <Plot kind="chart" span={6} minSpan={4} id="rep-revenue" height={800} title="Won revenue by representative" rows={perf.map(r=>({label:r.rep,amount:r.actual})).sort((a,b)=>b.amount-a.amount)} sourceRows={rows}/>
 <SortableItem id="quota-comparison" label="Scenario target vs. won value" kind="chart" span={6} minSpan={4}><EvidenceChart id="quota-comparison" queryId="compensation" title="Scenario target vs. won value" variant="card" rows={perf.map(r=>({rep:r.rep,actual:r.actual,target:r.target}))} sourceRows={reps} height={270} spec={{type:'bar',x:'rep',y:'actual',fields:['actual','target'],currency:'USD',startAtZero:true,stackable:false,legend:{labels:{actual:'Won revenue',target:'Scenario target'}},showXAxisLabel:false,showYAxisLabel:false}} description="Portfolio scenario: $500,000 annual target per each of 35 listed agents, 2017. Not source quotas."/></SortableItem>
 <Table kind="table" span={12} minSpan={6} id="rep-scorecard" title="Sales performance scorecard" rows={perf} sourceRows={reps} queryId="compensation" columns={[col('rep','Representative'),mc('target','Scenario target'),mc('actual','Won revenue'),pc('achievement','Scenario attainment'),col('won_deals','Deals won'),pc('win_rate','Win rate'),mc('average','Average won deal')]} description="2017 closing cohort. Win rate excludes open deals; targets are illustrative assumptions."/>
 </SortableRegion></>;
}
