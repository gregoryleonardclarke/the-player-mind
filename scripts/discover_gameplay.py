"""Identify HD genuine gameplay items in public Internet Archive metadata."""
import requests,concurrent.futures,re
GAMES=["Minecraft","World of Warcraft","Elden Ring","Dark Souls","Stardew Valley","Portal 2","Hades","Diablo","Skyrim","Fallout 4","Subnautica"]
S=requests.Session()
def search(g):
    q=f'title:("{g}") AND mediatype:(movies)'
    try:
        r=S.get("https://archive.org/advancedsearch.php",params={"q":q,"fl[]":["identifier","title"],"rows":75,"output":"json"},timeout=30)
        r.raise_for_status()
        ds=r.json()["response"]["docs"]
        # Prioritise recorded gameplay rather than reviews, trailers or compilations
        ds.sort(key=lambda d: (0 if "gameplay" in d.get("title","").lower() else 1, 0 if "4k" in d.get("title","").lower() or "1080" in d.get("title","").lower() else 1))
        return (g,ds[:35])
    except Exception as e: print("SEARCH_ERROR",g,str(e),flush=True);return(g,[])
def metadata(g,d):
    try:
        j=S.get("https://archive.org/metadata/"+d["identifier"],timeout=22).json()
        items=[]
        for f in j.get("files",[]):
            if f.get("source") not in ("original",None):continue
            if not f.get("name","").lower().endswith((".mp4",".webm",".mov")):continue
            w=int(f.get("width") or 0);h=int(f.get("height") or 0)
            z=int(f.get("size") or 0)
            dur=float(f.get("length") or 0)
            if w>=1920 and h>=1080 and (z<=250_000_000) and (dur==0 or dur>=50):
                items.append({"id":d["identifier"],"title":d.get("title"),"file":f.get("name"),"w":w,"h":h,"MB":round(z/1e6,1),"duration":round(dur),"host":"https://archive.org/details/"+d["identifier"]})
        return(g,items)
    except Exception as e:return(g,[])
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    found=list(pool.map(search,GAMES))
candidates=[(g,d) for g,ds in found for d in ds]
print("CANDIDATE COUNTS",[(g,len(ds)) for g,ds in found],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=14) as pool:
    rows=list(pool.map(lambda pair: metadata(*pair),candidates))
for g in GAMES:
    good=[z for a,items in rows if a==g for z in items]
    good.sort(key=lambda x: (0 if "gameplay" in x["title"].lower() else 1,x["MB"]))
    print("GAME",g,"VERIFIED",len(good),flush=True)
    for item in good[:7]:print("SOURCE",item,flush=True)
