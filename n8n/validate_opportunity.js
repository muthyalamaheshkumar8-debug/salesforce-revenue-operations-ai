const expected = $env.WORKFLOW_CURRENCY || 'INR';
const threshold = Number($env.HIGH_VALUE_THRESHOLD || 500000);
if (!Number.isFinite(threshold) || threshold < 0) throw new Error('Invalid threshold');
return $input.all().map(item => {
  const o = item.json;
  if (!o.Id || !o.StageName || !o.LastModifiedDate || (o.Amount == null || o.Amount === '') || !o.CurrencyIsoCode) throw new Error('Incomplete opportunity');
  const amount = Number(o.Amount);
  if (!Number.isFinite(amount) || amount < 0) throw new Error('Invalid amount');
  if (o.CurrencyIsoCode !== expected) throw new Error('Currency mismatch; no implicit FX conversion');
  return {json:{opportunity:o,event_id:o.Id + ':' + o.LastModifiedDate,mode:$env.ANALYSIS_MODE || 'rules',high_value:amount >= threshold}};
});