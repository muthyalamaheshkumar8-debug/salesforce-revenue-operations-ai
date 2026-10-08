"""Reconcile source won values to the explicitly simulated commission plan."""
import sys,json
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.analytics import read_rows,summary
if __name__=='__main__':
    rows=read_rows('compensation');revenue=Decimal(str(summary(read_rows('opportunities'))['won_revenue']))
    payout=sum(Decimal(str(r['payout'])) for r in rows)
    assert payout==revenue*Decimal('.05')
    print(json.dumps({'scenario':True,'assumed_rate':.05,'won_value':float(revenue),'estimated_payout':float(payout),'agents':len(rows)}))
