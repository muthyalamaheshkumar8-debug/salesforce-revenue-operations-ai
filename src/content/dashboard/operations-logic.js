// Local rehearsal helpers. Never mutate the reviewed CRM snapshot or contact services.
export const stages = ['Prospecting','Engaging','Qualification','Needs Analysis','Proposal','Negotiation','Closed Won','Closed Lost'];
const text = v => typeof v === 'string' && v.trim().length > 0;
const amount = v => (typeof v === 'number' || (text(v) && /^\d+(\.\d+)?$/.test(v))) && Number.isFinite(Number(v)) && Number(v) >= 0;
const isoDate = v => text(v) && /^\d{4}-\d{2}-\d{2}$/.test(v) && !Number.isNaN(Date.parse(v)) && new Date(v).toISOString().slice(0,10) === v;
export function parseRows(input) {
  if (input.length > 1000000) throw new Error('Use a JSON file smaller than 1 MB.');
  const rows = JSON.parse(input);
  if (!Array.isArray(rows) || rows.length > 500) throw new Error('Use a JSON array with at most 500 records.');
  if (rows.some(r => !r || typeof r !== 'object' || Array.isArray(r))) throw new Error('Every record must be an object.');
  return rows;
}
export function reviewEngagement(rows, platform, opportunities) {
  const master = new Map(opportunities.map(r => [r.opportunity_id,r]));
  const seen = new Set(); const accepted = [], exceptions = [];
  rows.forEach((r,i) => {
    const reasons = [];
    if (!text(r.activity_id)) reasons.push('Missing activity ID');
    else if (seen.has(r.activity_id)) reasons.push('Duplicate activity ID');
    seen.add(r.activity_id);
    const deal = master.get(r.opportunity_id);
    if (!deal) reasons.push('Unknown opportunity ID');
    if (!isoDate(r.activity_date)) reasons.push('Use a valid YYYY-MM-DD activity date');
    if (!['meeting','call','email'].includes(r.type)) reasons.push('Type must be meeting, call or email');
    if (!['scheduled','completed','replied','no_response'].includes(r.outcome)) reasons.push('Unsupported activity outcome');
    if (platform === 'Gong' && r.type !== 'call') reasons.push('Gong adapter accepts call records');
    if (!text(r.next_step)) reasons.push('Missing next step');
    if (reasons.length) exceptions.push({row:i+1,activity_id:r.activity_id ?? '',reason:reasons.join('; ')});
    else accepted.push({activity_id:r.activity_id,platform,opportunity_id:r.opportunity_id,rep:deal.rep,activity_date:r.activity_date,type:r.type,outcome:r.outcome,next_step:r.next_step,provenance:'User-supplied export; platform origin unverified'});
  });
  return {accepted,exceptions,connected:false};
}
export function mapAcquisition(rows, opportunities, reps, businessLine) {
  if (!text(businessLine)) throw new Error('Enter a business line.');
  const accounts = new Map(opportunities.filter(r => r.account_id).map(r => [r.account_id,r.account]));
  const owners = new Map(reps.map(r => [r.rep_id,r.rep]));
  const existing = new Set(opportunities.map(r => r.opportunity_id));
  const seen = new Set(); const accepted = [], exceptions = [];
  rows.forEach((r,i) => {
    const reasons = [];
    if (!text(r.legacy_id)) reasons.push('Missing legacy ID');
    else if (seen.has(r.legacy_id)) reasons.push('Duplicate legacy ID');
    seen.add(r.legacy_id);
    if (!accounts.has(r.account_id)) reasons.push('Unmapped account');
    if (!owners.has(r.rep_id)) reasons.push('Unmapped owner');
    if (!stages.includes(r.stage)) reasons.push('Unmapped sales stage');
    if (!amount(r.amount)) reasons.push('Amount must be a finite non-negative number');
    if (!/^[A-Z]{3}$/.test(r.currency ?? '')) reasons.push('Supply a three-letter currency code');
    if (!isoDate(r.close_date)) reasons.push('Supply a valid close date');
    const id = `${businessLine.trim()}:${r.legacy_id}`;
    if (existing.has(id)) reasons.push('Destination ID already exists');
    if (reasons.length) exceptions.push({row:i+1,legacy_id:r.legacy_id ?? '',reason:reasons.join('; ')});
    else accepted.push({opportunity_id:id,legacy_id:r.legacy_id,business_line:businessLine.trim(),account_id:r.account_id,account:accounts.get(r.account_id),rep_id:r.rep_id,rep:owners.get(r.rep_id),stage:r.stage,amount:Number(r.amount),currency:r.currency,close_date:r.close_date});
  });
  return {accepted,exceptions,commit_allowed:rows.length>0 && exceptions.length===0,crm_written:false};
}
// Integer cents avoid floating-point payroll rounding drift. This is a scenario only.
export function commissionLedger(reps, rateBps) {
  if (!Number.isInteger(rateBps) || rateBps<0 || rateBps>10000) throw new Error('Rate must be between 0 and 10000 basis points.');
  return reps.map(r => {
    if (!amount(r.actual) || Number(r.actual)*100 > Number.MAX_SAFE_INTEGER/10000) throw new Error('Invalid commission basis.');
    const basis_cents = Math.round(Number(r.actual)*100);
    return {rep_id:r.rep_id,rep:r.rep,basis_cents,rate_bps:rateBps,payout_cents:Math.round(basis_cents*rateBps/10000),status:'calculated',scenario:true};
  });
}
export function gradeTraining(course, answers) {
  const correct=course.questions.filter((q,i)=>answers[i]===q.answer).length;
  const answered=course.questions.every((q,i)=>Number.isInteger(answers[i]));
  return {correct,total:course.questions.length,passed:answered && correct===course.questions.length,answered};
}
