import React from 'react';
import {DataComponent,DataTable,EvidenceChart,MetricCard,SectionHeader,SortableItem,SortableRegion} from '../../data-app-public.jsx';

export function Pipeline({rows}){
 const open=rows.filter(r=>!r.stage.startsWith('Closed'));
 const aged=open.map(r=>({...r,engagement_days:r.created_date?Math.floor((Date.parse('2017-12-31')-Date.parse(r.created_date))/86400000):null}));
 const counts=['Prospecting','Engaging'].map(stage=>({stage,count:open.filter(r=>r.stage===stage).length}));
 const buckets=[{label:'No engagement date',test:r=>r.engagement_days==null},{label:'0–30 days',test:r=>r.engagement_days!=null&&r.engagement_days<=30},{label:'31–90 days',test:r=>r.engagement_days>30&&r.engagement_days<=90},{label:'Over 90 days',test:r=>r.engagement_days>90}].map(b=>({label:b.label,count:aged.filter(b.test).length}));
 return <>
 <SortableRegion id="pipeline-metrics" variant="canvas" authoredRevision={1} columns={12} rows={[{id:'pipeline-metric-row',kind:'metrics',items:['pipeline-count','pipeline-unassigned','pipeline-aged','pipeline-amount']}]}>
 {[
 ['pipeline-count','Open opportunities',open.length,'Prospecting and Engaging records.'],
 ['pipeline-unassigned','Account unassigned',open.filter(r=>!r.account_id).length,'Account relationships are absent in the source.'],
 ['pipeline-aged','Engaged over 90 days',aged.filter(r=>r.engagement_days>90).length,'At 31 Dec 2017; days since engagement, not last activity.'],
 ['pipeline-amount','Monetary forecast','Unavailable','Open amounts, probability and expected close dates are missing.']
 ].map(([id,title,value,description])=><SortableItem key={id} id={id} label={title} kind="metric" span={3} minSpan={2}><MetricCard id={id} queryId="opportunities" title={title} value={value} description={description} sourceRows={open} displayRows={[{metric:title,value}]}/></SortableItem>)}
 </SortableRegion>
 <SectionHeader id="pipeline-review-heading" title="Open-deal review"/>
 <SortableRegion id="pipeline-evidence" variant="canvas" authoredRevision={1} columns={12} rows={[{id:'pipeline-chart-row',items:['pipeline-stage-count','pipeline-age-count']},{id:'pipeline-review-row',items:['pipeline-review-queue']}] }>
 <SortableItem id="pipeline-stage-count" label="Open stage coverage" kind="chart" span={6} minSpan={4}><EvidenceChart id="pipeline-stage-count" queryId="opportunities" title="Open stage coverage" variant="card" rows={counts} sourceRows={open} height={270} spec={{type:'bar',x:'stage',y:'count',startAtZero:true,currency:null,showXAxisLabel:false,showYAxisLabel:false}} description="Counts of current stages; this is not a historical conversion funnel."/></SortableItem>
 <SortableItem id="pipeline-age-count" label="Engagement age" kind="chart" span={6} minSpan={4}><EvidenceChart id="pipeline-age-count" queryId="opportunities" title="Engagement age" variant="card" rows={buckets} sourceRows={open} height={270} spec={{type:'horizontalBar',x:'label',y:'count',startAtZero:true,currency:null,showXAxisLabel:false,showYAxisLabel:false}} description="Age at 31 Dec 2017; missing engagement dates are retained separately."/></SortableItem>
 <SortableItem id="pipeline-review-queue" label="Deal review queue" kind="table" span={12} minSpan={6}><DataComponent id="pipeline-review-queue" queryId="opportunities" title="Deal review queue" kind="table" variant="card" sourceRows={open} displayRows={aged} description="Verify next activity and required forecast fields with the listed owner."><DataTable rows={[...aged].sort((a,b)=>(b.engagement_days??-1)-(a.engagement_days??-1))} columns={[{field:'opportunity_id',label:'Opportunity'},{field:'rep',label:'Owner'},{field:'account',label:'Account'},{field:'stage',label:'Stage'},{field:'created_date',label:'Engaged on'},{field:'engagement_days',label:'Engagement days'}]}/></DataComponent></SortableItem>
 </SortableRegion>
 </>;
}
