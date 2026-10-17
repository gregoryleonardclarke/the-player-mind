import requests,concurrent.futures
from collections import defaultdict
session=requests.Session()
queries=[
'title:(Subnautica) AND mediatype:(movies)',
'title:(Subnautica) AND title:(gameplay) AND mediatype:(movies)',
'title:(Subnautica) AND title:(leviathan) AND mediatype:(movies)',
'title:(Subnautica) AND title:(exploration) AND mediatype:(movies)'
]
items={}
for query in queries:
 try:
  q=session.get('https://archive.org/advancedsearch.php',params={'q':query,'fl[]':['identifier','title'],'rows':160,'output':'json'},timeout=40).json()
  print('QUERY',query,'total',q['response']['numFound'],flush=True)
  for d in q['response']['docs']:items[d['identifier']]=d
 except Exception as e:print('SEARCH ERR',repr(e),flush=True)
print('TOTAL CANDIDATES',len(items),flush=True)
def check(d):
 try:
  j=session.get('https://archive.org/metadata/'+d['identifier'],timeout=22).json()
  best=[]
  for f in j.get('files',[]):
   if f.get('source')!='original' or not f.get('name','').lower().endswith(('.mp4','.webm','.mkv')):continue
   w=int(f.get('width') or 0);h=int(f.get('height') or 0);z=int(f.get('size') or 0);t=float(f.get('length') or 0)
   if w>=1920 and h>=1080 and 45<=t<=2500 and z<=450000000:
    best.append({'id':d['identifier'],'title':d.get('title'),'file':f['name'],'size':z,'duration':t,'width':w,'height':h})
  return best
 except Exception as e:return []
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
 for result in pool.map(check,items.values()):
  for rec in result:
   print('HD SOURCE',rec,flush=True)
