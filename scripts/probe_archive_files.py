import requests
ids=[
'20111111-skyrim-gameplay-bleak-falls-barrow-boss-fight-116s-1920x-1080-q-99h-fmyt-oq',
'20111111-skyrim-gameplay-join-the-stormcloak-rebellion-125s-1920x-1080-q-5f-w-jt-8-rao',
'SkyrimGameplay2011-12-1009-20-20-01',
'youtube-gWj5-WZDyoI',
'the-elder-scrolls-v-skyrim-special-edition-2026-05-31-11-51-08-pm-1',
'youtube--NhevGw_qBw',
'skyrim-special-edition-werewolf-hunter-random-encounter',
]
for ident in ids:
 try:
  r=requests.get('https://archive.org/metadata/'+ident,timeout=25)
  print('IDENT',ident,'STATUS',r.status_code,flush=True)
  if r.status_code != 200:continue
  d=r.json()
  print('META',d.get('metadata',{}).get('title'),flush=True)
  for f in d.get('files',[]):
   if any(f.get('name','').lower().endswith(s) for s in ['.mp4','.webm','.mkv','.mov','.avi']):
    print('FILE',f.get('name'),'SIZE',f.get('size'),'WIDTH',f.get('width'),'HEIGHT',f.get('height'),'LENGTH',f.get('length'),'SOURCE',f.get('source'),flush=True)
 except Exception as e:print('FAIL',ident,str(e),flush=True)
