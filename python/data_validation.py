"""Independent quality checks; exits nonzero on invalid retained records."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.analytics import read_rows,quality
if __name__=='__main__':
    result=quality(read_rows('opportunities'));print(json.dumps(result,indent=2))
    if any(result[k] for k in ('duplicate_ids','negative_amounts','invalid_date_order','missing_owners','missing_regions','invalid_stages')):raise SystemExit(1)
