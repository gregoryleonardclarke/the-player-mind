import requests
queries=[
 'title:(Skyrim) AND title:(1080p) AND mediatype:(movies)',
 'title:(Skyrim) AND title:(60fps) AND mediatype:(movies)',
 'title:(Skyrim) AND title:(Special Edition) AND mediatype:(movies)',
 'title:(Skyrim gameplay) AND mediatype:(movies)'
]
for q in queries:
 try:
  r=requests.get('https://archive.org/advancedsearch.php',params={'q':q,'fl[]':['identifier','title'],'rows':100,'page':1,'output':'json'},timeout=25)
  print('SEARCH',q,'status',r.status_code,flush=True)
  if r.status_code!=200:continue
  dat=r.json()
  print('COUNT',dat.get('response',{}).get('numFound'),flush=True)
  for d in dat.get('response',{}).get('docs',[])[:100]:print('ITEM',d,flush=True)
 except Exception as e:print('ERROR',str(e),flush=True)
