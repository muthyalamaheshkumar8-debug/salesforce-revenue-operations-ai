"""Executes trusted project notebook code cells and stores real stdout outputs."""
import json,io,contextlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
for path in sorted((ROOT/'python').glob('*.ipynb')):
    nb=json.loads(path.read_text());scope={};count=0
    for cell in nb['cells']:
        if cell['cell_type']!='code':continue
        count+=1;buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer):exec(compile(''.join(cell['source']),str(path),'exec'),scope)
        cell['execution_count']=count;cell['outputs']=[{'output_type':'stream','name':'stdout','text':buffer.getvalue().splitlines(True)}]
    path.write_text(json.dumps(nb,indent=2));print(f'Executed {path.name}: {count} code cells')
