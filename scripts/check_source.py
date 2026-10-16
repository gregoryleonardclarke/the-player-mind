import urllib.request, re, html
from urllib.parse import urljoin
urls=[
 'https://www.gamersyde.com/news_20_minutes_of_skyrim_gameplay-11878_en.html',
 'https://www.gamersyde.com/video_the_elder_scrolls_v_skyrim_gameplay_demo_part_1-23439_en.html'
]
for u in urls:
    print("SOURCE",u,flush=True)
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)
        body=r.read().decode('utf-8',errors='replace')
        print('Status',r.status,'length',len(body),flush=True)
        found=[]
        for h in re.findall(r'''(?:href|src)=["']([^"']+)["']''',body,re.I):
            full=urljoin(u,html.unescape(h))
            if any(k in full.lower() for k in ['skyrim','download','video','mp4','gamersyde.com/stream','media.moddb','media.gamersyde']):
                if full not in found:found.append(full)
        print("CANDIDATE LINKS",found[:90],flush=True)
    except Exception as e:print('ERROR',str(e),flush=True)

# Inspect the actual download controls on Gamersyde's video detail page.
u="https://www.gamersyde.com/video_the_elder_scrolls_v_skyrim_gameplay_demo_part_1-23439_en.html"
r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)
body=r.read().decode('utf-8',errors='replace')
for term in ["Download","Téléchargement",".mp4","source","videojs","resolutions"]:
    print("CONTEXT",term,flush=True)
    matches=list(re.finditer(re.escape(term),body,re.I))
    print("COUNT",len(matches),flush=True)
    for m in matches[:5]:
        print(body[max(0,m.start()-300):m.end()+500].replace("\n"," ")[:900],flush=True)
