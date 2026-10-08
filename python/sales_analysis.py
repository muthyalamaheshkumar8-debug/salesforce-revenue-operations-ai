"""Regenerate reproducible rules-based findings and the public snapshot query."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend.analytics import read_rows,brief

def run():
    evidence=brief(read_rows('opportunities'),read_rows('sales_reps'))
    (ROOT/'documentation/analysis-brief.json').write_text(json.dumps(evidence,indent=2))
    path=ROOT/'src/data.json';snapshot=json.loads(path.read_text())
    snapshot['queries']['insights']={'rows':evidence['findings'],'source':{'label':'Reproducible operational rules on the Maven fictional CRM sample','classification':'synthetic','links':snapshot['queries']['opportunities']['source']['links'],'tables':['data/cleaned/opportunities.csv','data/cleaned/sales_reps.csv'],'coverage':{'startDate':'2017-01-01','endDate':'2017-12-31'},'evidenceFlow':[{'title':'Validate sample','detail':'python python/pipeline.py; preserve null open values and missing account relationships.'},{'title':'Evaluate operational rules','detail':'python python/sales_analysis.py; backend/analytics.py calculates account gaps, open-value coverage, engagement age at 2017-12-31, consecutive-month movement, scenario target gaps and closed-deal win rate.'}],'metricDefinitions':[{'label':'Rule analysis','definition':'Deterministic review flags, not LLM-generated forecasts. Facts and recommendations are separate; source IDs permit traceability.'},{'label':'Engagement age','definition':'2017-12-31 minus source engage_date in calendar days. Not inactivity; missing dates are not filled.'}]},'methods':[{'language':'python','code':'from backend.analytics import read_rows, insights\ninsights(read_rows("opportunities"), read_rows("sales_reps"))'}]}
    snapshot['buildStatus']='updating';snapshot['generatedAt']=datetime.now(timezone.utc).isoformat();snapshot['description']='Salesforce revenue operations portfolio with sales, pipeline, quality, compensation scenarios and evidence-backed operational insights.'
    path.write_text(json.dumps(snapshot,indent=2))
    print(json.dumps({'findings':len(evidence['findings']),'summary':evidence['summary']}))
if __name__=='__main__':run()
