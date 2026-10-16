import requests
queries=[
 'title:(Skyrim) AND mediatype:(movies)',
 'title:(Elder Scrolls V) AND mediatype:(movies)',
 '(Skyrim gameplay) AND mediatype:(movies)'
]
for q in queries:
 try:
  r=requests.get('https://archive.org/advancedsearch.php',params={'q':q,'fl[]':['identifier','title'],'rows':30,'page':1,'output':'json'},timeout=20)
  print('SEARCH',q,'status',r.status_code,flush=True)
  if r.status_code!=200: print(r.text[:300]);continue
  data=r.json()
  print('COUNT',data.get('response',{}).get('numFound'),flush=True)
  for d in data.get('response',{}).get('docs',[]):print('ITEM',d,flush=True)
 except Exception as e:print('ERROR',repr(e),flush=True)
