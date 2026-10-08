import React from 'react';
import {DataComponent,DataTable,SectionHeader,SortableItem,SortableRegion} from '../../data-app-public.jsx';

export function AIInsights({query}) {
 const findings=query.rows;
 const exportBrief=()=>{const body=JSON.stringify({engine:'rules',llm_connected:false,findings},null,2);const url=URL.createObjectURL(new Blob([body],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='revenue-operations-brief.json';a.click();URL.revokeObjectURL(url);};
 return <>
 <div className="rev-insights-status"><div><strong>Evidence-backed operational review</strong><p>Rules-based analysis · historical snapshot at 31 Dec 2017. LLM connection pending.</p></div><button type="button" onClick={exportBrief}>Download brief</button></div>
 <SortableRegion id="ai-findings" variant="canvas" authoredRevision={1} columns={12} rows={findings.map(f=>({id:`ai-row-${f.id}`,items:[`ai-${f.id}`]}))}>
 {findings.map(f=><SortableItem key={f.id} id={`ai-${f.id}`} label={f.title} kind="custom" span={12} minSpan={6}><DataComponent id={`ai-${f.id}`} queryId="insights" title={f.title} kind="custom" variant="card" sourceRows={[f]} displayRows={[f]}><div className="rev-finding" data-reviewed-rows><span className={`rev-severity rev-severity-${f.severity.toLowerCase()}`}>{f.severity} · {f.category}</span><div className="rev-finding-columns"><div><span className="rev-field-label">Observed fact</span><p>{f.fact}</p></div><div><span className="rev-field-label">Recommended action</span><p>{f.recommendation}</p></div></div><small>Rule: {f.id} · {f.count.toLocaleString()} {f.metric.toLowerCase()} · {f.evidence_ids.length.toLocaleString()} linked opportunity IDs</small></div></DataComponent></SortableItem>)}
 </SortableRegion>
 <p className="rev-note">Alerts prompt investigation. Engagement age does not measure inactivity. Target gaps use an assumed annual quota. The downloadable project includes a tested LangChain prompt and output parser; model-generated drafts require review.</p>
 </>;
}
