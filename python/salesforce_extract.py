"""Read-only Salesforce REST extraction. Secrets stay in environment variables.
Exports source JSON for review; does not silently replace the published sample.
"""
import os,json,urllib.request,urllib.parse,argparse
from pathlib import Path

def extract(output):
    instance=os.environ['SALESFORCE_INSTANCE_URL'].rstrip('/')
    parsed=urllib.parse.urlparse(instance)
    if parsed.scheme!='https' or parsed.port not in (None,443) or not parsed.hostname or not parsed.hostname.endswith(('.salesforce.com','.my.salesforce.com')) or parsed.path or parsed.query or parsed.fragment or parsed.username:
        raise ValueError('Use the canonical HTTPS Salesforce instance origin')
    version=os.getenv('SALESFORCE_API_VERSION','v68.0')
    if not __import__('re').fullmatch(r'v\d+\.0',version):raise ValueError('Invalid Salesforce API version')
    fields='Id,Name,AccountId,OwnerId,StageName,Amount,Probability,CloseDate,CreatedDate,LastModifiedDate'
    if os.getenv('SALESFORCE_MULTI_CURRENCY')=='true':fields+=',CurrencyIsoCode'
    url=instance+'/services/data/'+version+'/query?'+urllib.parse.urlencode({'q':'SELECT '+fields+' FROM Opportunity ORDER BY Id'})
    rows=[]
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args):raise ValueError('Unexpected Salesforce redirect')
    opener=urllib.request.build_opener(NoRedirect)
    while url:
        request=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['SALESFORCE_ACCESS_TOKEN'],'Accept':'application/json'})
        with opener.open(request,timeout=30) as response:body=json.load(response)
        rows.extend(body['records']);next_url=body.get('nextRecordsUrl')
        if next_url and (not next_url.startswith('/services/data/') or next_url.startswith('//')):raise ValueError('Invalid pagination path')
        url=instance+next_url if next_url else None
    destination=Path(output);destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps({'source':'Salesforce REST API','records':rows},indent=2));destination.chmod(0o600)
    print(json.dumps({'extracted_records':len(rows),'live_dashboard_updated':False}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='data/private/salesforce-opportunities.json');extract(parser.parse_args().output)
