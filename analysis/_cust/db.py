import requests, json
try:
    import truststore; truststore.inject_into_ssl()
except Exception: pass
def env():
    e={}
    for l in open(r'C:/Projects/Sales_Platform/analysis/.env',encoding='utf-8'):
        if '=' in l and not l.startswith('#'):
            k,v=l.split('=',1); e[k.strip()]=v.strip().strip('"').strip("'")
    return e
E=env(); BASE=E['SUPABASE_URL'].rstrip('/'); KEY=E['SUPABASE_SERVICE_ROLE_KEY']
H={'apikey':KEY,'Authorization':'Bearer '+KEY}
def fetch(table,params='',page=1000):
    out=[];off=0
    while True:
        r=requests.get(f"{BASE}/rest/v1/{table}?{params}",headers={**H,'Range-Unit':'items','Range':f'{off}-{off+page-1}'},timeout=120)
        r.raise_for_status(); d=r.json(); out+=d
        if len(d)<page: break
        off+=page
    return out
