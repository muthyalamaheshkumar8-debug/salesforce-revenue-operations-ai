import React from 'react';
import {DataComponent,EvidenceChart,SectionHeader,SortableItem,SortableRegion} from '../../data-app-public.jsx';
export function DataQuality({q,issues,Stat,Table,col}){
 return <>
 <SortableRegion id="quality-metrics" variant="canvas" authoredRevision={1} columns={12} spacing="standard" rows={[{"id":"quality-metrics-row-1","items":["raw-records","valid-records","quarantined-records","duplicate-records"],"kind":"metrics"}]}>
 <Stat kind="metric" span={3} minSpan={2} id="raw-records" title="Raw opportunity rows" value={q.raw_rows} queryId="quality_summary" sourceRows={[q]}/>
 <Stat kind="metric" span={3} minSpan={2} id="valid-records" title="Retained opportunities" value={q.clean_rows} queryId="quality_summary" sourceRows={[q]}/>
 <Stat kind="metric" span={3} minSpan={2} id="quarantined-records" title="Missing account values" value={q.missing_accounts} queryId="quality_summary" sourceRows={[q]} description="Open deals without assigned accounts; retained for stage and agent counts, not filled with invented accounts."/>
 <Stat kind="metric" span={3} minSpan={2} id="duplicate-records" title="Duplicates removed" value={q.duplicates} queryId="quality_summary" sourceRows={[q]} description="Identical repeated IDs; conflicting duplicates require manual review."/>
 </SortableRegion>
 <SectionHeader id="quality-heading" title="Validation & exception handling"/>
<SortableRegion id="quality-evidence" variant="canvas" authoredRevision={1} columns={12} spacing="standard" rows={[{"id":"quality-evidence-row-1","items":["quality-reconciliation"]},{"id":"quality-evidence-row-2","items":["quality-exceptions"]}]}>
 <SortableItem id="quality-reconciliation" label="Record reconciliation" kind="custom" span={12} minSpan={6}><DataComponent variant="card" id="quality-reconciliation" title="Record reconciliation" queryId="quality_summary" kind="custom" sourceRows={[q]} displayRows={[q]}><div className="rev-equation" data-reviewed-rows><span><strong>{q.raw_rows}</strong>raw rows</span><b>−</b><span><strong>{q.duplicates}</strong>duplicates</span><b>−</b><span><strong>{q.quarantined}</strong>quarantined</span><b>=</b><span><strong>{q.clean_rows}</strong>retained</span></div><p className="rev-note">{q.standardized} product keys mapped from GTXPro to GTX Pro. {q.missing_accounts} open deals have no account; {q.open_without_value} open amounts and close dates remain unavailable. All source opportunities are retained.</p></DataComponent></SortableItem>
 <Table kind="table" span={12} minSpan={6} id="quality-exceptions" title="Source quality ledger" rows={issues} queryId="quality" columns={[col('record','Record'),col('input_row','Input row'),col('field','Field'),col('issue','Rule'),col('severity','Severity'),col('disposition','Disposition'),col('resolution','Resolution')]} description="Product normalization and missing-account disclosures; expected open-stage blanks are preserved."/>
 </SortableRegion></>;
}
