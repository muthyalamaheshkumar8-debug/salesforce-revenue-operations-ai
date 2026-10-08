import React,{useState} from 'react';
import {Button,DataComponent,DataTable,SectionHeader} from '../../data-app-public.jsx';
import {parseRows,reviewEngagement,mapAcquisition,commissionLedger,gradeTraining} from './operations-logic.js';
import './operations.css';

function download(name,data) {
  const content=typeof data==='string'?data:JSON.stringify(data,null,2);
  const url=URL.createObjectURL(new Blob([content],{type:typeof data==='string'?'text/plain':'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function LocalTable({rows,fields,caption}) {
  return <div className="ops-table"><table><caption>{caption}</caption><thead><tr>{fields.map(([key,label])=><th key={key}>{label}</th>)}</tr></thead><tbody>{rows.slice(0,100).map((r,i)=><tr key={i}>{fields.map(([key])=><td key={key}>{String(r[key]??'—')}</td>)}</tr>)}</tbody></table>{rows.length>100&&<p>Showing the first 100 rows. Export contains all {rows.length} rows.</p>}{!rows.length&&<p>No records.</p>}</div>;
}
function Notice({children}){return <p className="ops-note">{children}</p>;}
function Coverage({query}) {
  const [search,setSearch]=useState('');
  const rows=query.rows.filter(r=>`${r.requirement} ${r.status} ${r.implemented}`.toLowerCase().includes(search.toLowerCase()));
  return <><SectionHeader id="ops-requirement-heading" title="Integration & capability coverage"/>
    <div className="ops-toolbar"><label>Find a requirement<input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Zapier, Gong, Salesforce…"/></label><Button onClick={()=>download('requirement-coverage.json',query.rows)}>Export coverage</Button></div>
    <Notice>Local workflows and prepared assets are listed below. External accounts have not been verified. A setup asset does not establish production experience.</Notice>
    <DataComponent id="ops-coverage" queryId="requirements" title="All 16 requested requirements" kind="table" variant="card" sourceRows={rows} displayRows={rows}>
    <DataTable rows={rows} columns={[{field:'requirement',label:'Requirement'},{field:'status',label:'Available now'},{field:'implemented',label:'Included implementation'},{field:'next_step',label:'Verification still needed'}]} caption="Requirement coverage"/></DataComponent>
    <div className="ops-grid">{rows.map(r=><article className="ops-card" key={r.id}><div className="ops-card-top"><h3>{r.requirement}</h3><span className="ops-badge">{r.status}</span></div><p>{r.implemented}</p><code>{r.artifact}</code><details><summary>How to verify</summary><p>{r.next_step}</p></details></article>)}</div>
  </>;
}
function Enablement({knowledge,training}) {
  const [search,setSearch]=useState(''),[audience,setAudience]=useState('All'),[courseId,setCourseId]=useState(training.rows[0].id),[answers,setAnswers]=useState({}),[result,setResult]=useState(null);
  const rows=knowledge.rows.filter(r=>(audience==='All'||r.audience===audience)&&`${r.title} ${r.tags} ${r.body}`.toLowerCase().includes(search.toLowerCase()));
  const course=training.rows.find(r=>r.id===courseId);
  return <><SectionHeader id="enablement-heading" title="Sales enablement & knowledge"/>
    <div className="ops-toolbar"><label>Search playbooks<input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Forecast, Apollo, commissions…"/></label><label>Audience<select value={audience} onChange={e=>setAudience(e.target.value)}>{['All',...new Set(knowledge.rows.map(r=>r.audience))].map(a=><option key={a}>{a}</option>)}</select></label><Button onClick={()=>download('sales-knowledge-repository.json',knowledge.rows)}>Export repository</Button></div>
    <DataComponent id="ops-knowledge" queryId="knowledge" title="Sales support repository" kind="custom" variant="card" sourceRows={rows} displayRows={rows}>
    <div className="ops-grid" data-reviewed-rows>{rows.map(r=><article className="ops-card" key={r.id}><span className="ops-badge">{r.audience}</span><h3>{r.title}</h3><p>{r.body}</p><ul>{r.checklist.map(s=><li key={s}>{s}</li>)}</ul><small>{r.id} · v{r.version} · Owner: {r.owner} · Reviewed {r.review_date}</small></article>)}{!rows.length&&<p>No matching playbook. Clear the search or select All.</p>}</div></DataComponent>
    <SectionHeader id="ops-training-heading" title="Training practice"/>
    <Notice>Practice assessment only. Session results describe this exercise; they do not record an actual sales-team training event. Export before closing the app.</Notice>
    <DataComponent id="ops-training" queryId="training" title="Lessons & assessment" kind="custom" variant="card" sourceRows={training.rows} displayRows={training.rows}>
    <label className="ops-control">Course<select value={courseId} onChange={e=>{setCourseId(e.target.value);setAnswers({});setResult(null);}}>{training.rows.map(c=><option key={c.id} value={c.id}>{c.title}</option>)}</select></label>
    <p>{course.lesson}</p><small>{course.audience} · {course.minutes} minutes · Related: {course.knowledge_ids.join(', ')}</small>
    <div className="ops-quiz">{course.questions.map((q,i)=><fieldset key={q.prompt}><legend>{i+1}. {q.prompt}</legend>{q.choices.map((choice,j)=><label key={choice}><input type="radio" name={`${course.id}-${i}`} checked={answers[i]===j} onChange={()=>{setAnswers({...answers,[i]:j});setResult(null);}}/>{choice}</label>)}{result&&<p className="ops-note">{q.explanation}</p>}</fieldset>)}</div>
    <div className="ops-toolbar"><Button onClick={()=>setResult({...gradeTraining(course,answers),course_id:course.id,recorded_at:new Date().toISOString(),type:'self-directed practice',actual_team_training:false})}>Check answers</Button>{result&&<Button onClick={()=>download('training-practice-record.json',result)}>Export practice record</Button>}</div>
    {result&&<p role="status">{result.correct} / {result.total} correct · {!result.answered?'Answer every question.':result.passed?'Practice completed.':'Review the explanations and try again.'}</p>}
    </DataComponent>
  </>;
}
function ImportWorkspace({kind,opportunities,reps}) {
  const [platform,setPlatform]=useState('Gong'),[line,setLine]=useState('New business line'),[input,setInput]=useState('[]'),[result,setResult]=useState(null),[error,setError]=useState('');
  const acquisition=kind==='acquisition';
  const changeInput=v=>{setInput(v);setResult(null);setError('');};
  const loadExample=()=>{
    const deal=opportunities.find(r=>r.account_id&&r.stage==='Closed Won');
    changeInput(JSON.stringify(acquisition?[{legacy_id:'PRACTICE-001',account_id:deal.account_id,rep_id:deal.rep_id,stage:'Closed Won',amount:1200,currency:'USD',close_date:'2026-10-01'}]:[{activity_id:'PRACTICE-001',opportunity_id:deal.opportunity_id,activity_date:'2026-10-01',type:platform==='Gong'?'call':'email',outcome:'completed',next_step:'Schedule a handoff review'}],null,2));
  };
  const review=()=>{try{const rs=parseRows(input);setResult(acquisition?mapAcquisition(rs,opportunities,reps,line):reviewEngagement(rs,platform,opportunities));setError('');}catch(e){setError(e.message);setResult(null);}};
  return <><SectionHeader id={`ops-${kind}-heading`} title={acquisition?'Acquisition & new business integration':'Sales engagement review'}/>
    <Notice>{acquisition?'Dry-run a business-line migration against the existing CRM account and owner keys. Nothing is written to Salesforce.':'Review normalized Gong, Apollo, Outreach or Salesloft activity exports. This is an export adapter; no native platform account is connected.'} Use authorized metadata only. Practice examples are synthetic and remain separate from the CRM snapshot.</Notice>
    <div className="ops-toolbar">{acquisition?<label>Business line<input value={line} onChange={e=>{setLine(e.target.value);setResult(null);}}/></label>:<label>Platform<select value={platform} onChange={e=>{setPlatform(e.target.value);setResult(null);}}>{['Gong','Apollo','Outreach','Salesloft'].map(v=><option key={v}>{v}</option>)}</select></label>}<Button onClick={loadExample}>Load practice example</Button><label className="ops-upload">Upload normalized JSON<input type="file" accept="application/json,.json" onChange={async e=>{const file=e.target.files[0];if(!file)return;if(file.size>1000000){setError('Use a JSON file smaller than 1 MB.');return;}try{changeInput(await file.text());}catch{setError('The file could not be read.');}}}/></label></div>
    <label className="ops-control">{acquisition?'Legacy opportunity records':'Normalized activity records'}<textarea spellCheck="false" rows={12} value={input} onChange={e=>changeInput(e.target.value)}/></label>
    <div className="ops-toolbar"><Button onClick={review}>{acquisition?'Validate migration':'Review activities'}</Button><Button onClick={()=>{changeInput('[]');setResult(null);}}>Reset input</Button></div>
    {error&&<p className="ops-error" role="alert">{error}</p>}
    {result&&<section className="ops-card"><h3>{result.accepted.length} accepted · {result.exceptions.length} exceptions</h3><p>{acquisition?(result.commit_allowed?'Ready for an export dry-run. No CRM write performed.':'Resolve all exceptions before exporting a migration batch.'):'Accepted rows are linked to known CRM opportunities. Platform origin remains unverified.'}</p>
    <LocalTable caption={acquisition?'Mapped business-line records':'Accepted engagement records'} rows={result.accepted} fields={acquisition?[['opportunity_id','Destination ID'],['account','Account'],['rep','Owner'],['stage','Stage'],['amount','Amount'],['currency','Currency']]:[['activity_id','Activity ID'],['platform','Platform'],['rep','Owner'],['type','Type'],['outcome','Outcome'],['next_step','Next step']]}/>
    <LocalTable caption="Exceptions requiring review" rows={result.exceptions} fields={[[acquisition?'legacy_id':'activity_id','ID'],['row','Row'],['reason','Reason']]}/>
    <div className="ops-toolbar"><Button disabled={acquisition&&!result.commit_allowed} onClick={()=>download(acquisition?'migration-dry-run.json':'engagement-review.json',{...result,type:'local rehearsal',reviewed_at:new Date().toISOString()})}>Export {acquisition?'mapped batch':'review'}</Button><Button onClick={()=>download('import-exceptions.json',result.exceptions)}>Export exceptions</Button></div>
    </section>}
  </>;
}
function Payouts({reps}) {
  const [rate,setRate]=useState(500),[status,setStatus]=useState('calculated'),[events,setEvents]=useState([]);
  const ledger=commissionLedger(reps,rate), total=ledger.reduce((s,r)=>s+r.payout_cents,0);
  const transition=next=>{setStatus(next);setEvents([...events,{from:status,to:next,at:new Date().toISOString(),actor:'local practice user'}]);};
  return <><SectionHeader id="ops-payout-heading" title="Commission approval rehearsal"/>
    <Notice>This uses the full 35-representative sample. Basis and display currency follow the original scenario; the source has no currency code. Review and approval are practice states. No payroll, tax calculation or money transfer occurs. Session state can be exported and clears when the app closes.</Notice>
    <div className="ops-toolbar"><label>Scenario commission rate<select value={rate} onChange={e=>{setRate(Number(e.target.value));setStatus('calculated');setEvents([]);}}>{[[300,'3%'],[500,'5%'],[700,'7%']].map(([v,label])=><option key={v} value={v}>{label}</option>)}</select></label><span className="ops-badge">{status}</span><strong>Total scenario payout: {(total/100).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}</strong></div>
    <div className="ops-toolbar"><Button disabled={status!=='calculated'} onClick={()=>transition('reviewed')}>Mark practice review complete</Button><Button disabled={status!=='reviewed'} onClick={()=>transition('approved')}>Approve rehearsal</Button><Button onClick={()=>{setStatus('calculated');setEvents([]);}}>Reset rehearsal</Button><Button onClick={()=>download('commission-rehearsal-ledger.json',{scenario:true,currency:null,currency_display:'USD convention; source unspecified',rate_bps:rate,status,total_cents:total,rows:ledger.map(r=>({...r,status})),audit:events,payment_issued:false})}>Export ledger</Button></div>
    <LocalTable caption="Scenario commission ledger — per-representative cent rounding" rows={ledger.map(r=>({...r,basis:(r.basis_cents/100).toFixed(2),payout:(r.payout_cents/100).toFixed(2),status}))} fields={[[ 'rep','Representative'],['basis','Won-value basis'],['rate_bps','Rate (basis points)'],['payout','Scenario payout'],['status','Practice status']]}/>
    <Notice>The authenticated backend adds separate operations and finance token roles, a durable audit trail and idempotent ledger creation. A browser rehearsal is not a secure shared approval.</Notice>
  </>;
}
function Collaboration({handoff,opportunities}) {
  const [team,setTeam]=useState('Sales'),[decision,setDecision]=useState('');
  const won=opportunities.filter(r=>r.stage==='Closed Won'),closed=opportunities.filter(r=>r.stage.startsWith('Closed')),missing=opportunities.filter(r=>!r.account_id).length;
  const brief=`${team} operations review — historical CRM sample\n\nPeriod: 2017 closes. Source: Maven Analytics fictional CRM.\nWon value: ${won.reduce((s,r)=>s+r.amount,0).toLocaleString('en-US')}; source currency unspecified.\nClosed-deal win rate: ${(100*won.length/closed.length).toFixed(1)}% (${won.length} / ${closed.length}).\nMissing account links: ${missing}.\n\nDecision requested: ${team==='Sales'?'Assign owners to account exceptions and collect open-deal amounts/close dates.':team==='CSM'?'Agree customer handoff criteria and a named owner for the next step.':'Agree opportunity linkage and reporting scope before attributing engagement to revenue.'}\nOwner: to be assigned in a real review.\nDecision / next step: ${decision||'Not yet recorded.'}\n\nDraft only. No stakeholder meeting or communication has been verified.`;
  return <><SectionHeader id="ops-collaboration-heading" title="Developer handoff & stakeholder review"/>
    <DataComponent id="ops-handoff" queryId="handoff" title="Developer review backlog" kind="table" variant="card" sourceRows={handoff.rows} displayRows={handoff.rows}><DataTable rows={handoff.rows} columns={[{field:'id',label:'Ticket'},{field:'title',label:'Change'},{field:'owner_role',label:'Reviewer role'},{field:'acceptance',label:'Acceptance criteria'},{field:'status',label:'Status'}]} caption="Developer handoff backlog"/></DataComponent>
    <div className="ops-toolbar"><Button onClick={()=>download('developer-handoff.json',handoff.rows)}>Export handoff</Button><Button onClick={()=>download('developer-review-receipt-template.json',{ticket_id:null,reviewer:null,reviewed_at:null,decision:null,evidence_url:null,status:'awaiting actual developer review'})}>Download review receipt template</Button></div>
    <SectionHeader id="ops-stakeholder-heading" title="Sales / CSM / Marketing review brief"/>
    <label className="ops-control">Audience<select value={team} onChange={e=>setTeam(e.target.value)}>{['Sales','CSM','Marketing'].map(t=><option key={t}>{t}</option>)}</select></label><label className="ops-control">Draft decision or next step<textarea rows={3} value={decision} onChange={e=>setDecision(e.target.value)} placeholder="Record the decision after your actual review."/></label>
    <pre className="ops-brief">{brief}</pre><Button onClick={()=>download(`${team.toLowerCase()}-review-brief.txt`,brief)}>Export draft brief</Button>
  </>;
}
export function OperationsWorkspace({mode,queries}) {
  // Keep these panels mounted while switching dashboard views; all inputs remain session-local.
  const panels={integrations:<Coverage query={queries.requirements}/>,enablement:<Enablement knowledge={queries.knowledge} training={queries.training}/>,engagement:<ImportWorkspace kind="engagement" opportunities={queries.opportunities.rows} reps={queries.compensation.rows}/>,acquisition:<ImportWorkspace kind="acquisition" opportunities={queries.opportunities.rows} reps={queries.compensation.rows}/>,payouts:<Payouts reps={queries.compensation.rows}/>,collaboration:<Collaboration handoff={queries.handoff} opportunities={queries.opportunities.rows}/>};
  return <div className="ops-workspace">{Object.entries(panels).map(([id,panel])=><div key={id} hidden={mode!==id}>{panel}</div>)}</div>;
}
