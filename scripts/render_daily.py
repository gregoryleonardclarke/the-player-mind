#!/usr/bin/env python3
"""The Player Mind cloud renderer: RESEARCH-BRIEF -> REVIEW VIDEO. NO PUBLISHING."""
import datetime, json, math, os, pathlib, re, subprocess, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy.io import wavfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
W,H,FPS=1080,1920,24
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def run(args):
    print("RUN"," ".join(map(str,args)),flush=True)
    return subprocess.run(args,check=True)

def load_input():
    candidates=sorted((ROOT/"briefs").glob("*.json"))
    if not candidates:raise ValueError("No approved-format research brief in briefs/")
    rel=os.environ.get("BRIEF_PATH")
    path=(ROOT/rel) if rel else candidates[-1]
    if ROOT not in path.resolve().parents:raise ValueError("Unsafe brief path")
    b=json.loads(path.read_text(encoding="utf-8"))
    duration=float(b["duration"])
    cards=b["cards"]
    if not 70<=duration<=121:raise ValueError("Duration must be 70-121 seconds")
    if not 12<=len(cards)<=28:raise ValueError("12-28 cards required to teach a lesson")
    p=0
    for card in cards:
        start=float(card["start"]);end=float(card["end"])
        lines=card["lines"]
        if abs(start-p)>.15 or end<=start or end-start>9.0:
            raise ValueError("Cards must cover continuous timeline with <=9 sec duration")
        if not 1<=len(lines)<=3 or any(not isinstance(t,str) or not t.strip() or len(t)>38 for t in lines):
            raise ValueError("Each card needs 1-3 short readable lines")
        p=end
    if abs(p-duration)>.2:raise ValueError("Cards must cover full duration")
    if len(b.get("research",[]))<1 or len(b.get("sources",[]))<1:
        raise ValueError("Specify research citations and catalogued gameplay sources")
    if b.get("requires_publication") or b.get("publish"):
        raise ValueError("Automated publication is prohibited")
    catalog=json.loads((ROOT/"assets/gameplay_catalog.json").read_text(encoding="utf-8"))
    ids={x["id"]:x for x in catalog["sources"]}
    sources=[]
    for name in b["sources"]:
        if name not in ids:raise ValueError("No verified catalog entry for: "+name)
        sources.append(ids[name])
    if len(set(x["game"] for x in sources))!=1:
        raise ValueError("Use clips from one appropriate game per video")
    return path,b,duration,sources

def ffprobe(path):
    return json.loads(subprocess.check_output([
      "ffprobe","-v","error","-show_entries","stream=codec_type,width,height:format=duration,size",
      "-of","json",str(path)]))

def download(src,index):
    ident=src["identifier"]
    with urllib.request.urlopen(urllib.request.Request("https://archive.org/metadata/"+ident,headers={"User-Agent":"Mozilla/5.0"}),timeout=60) as r:
        meta=json.load(r)
    matches=[f for f in meta.get("files",[]) if f.get("name")==src["filename"] and f.get("source") in (None,"original")]
    if not matches:raise ValueError("Archived original file is missing: "+src["id"])
    m=matches[0]
    if int(m.get("width") or 0)<1920 or int(m.get("height") or 0)<1080:
        raise ValueError("Source below Full HD: "+src["id"])
    link="https://archive.org/download/"+urllib.parse.quote(ident)+"/"+urllib.parse.quote(src["filename"])
    ext=pathlib.Path(src["filename"]).suffix
    path=OUT/f"source_{index}{ext}"
    req=urllib.request.Request(link,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=180) as resp,path.open("wb") as out:
        while True:
            chunk=resp.read(1024*1024)
            if not chunk:break
            out.write(chunk)
    if path.stat().st_size<4000000:raise ValueError("Source unexpectedly tiny")
    info=ffprobe(path)
    vs=[s for s in info["streams"] if s["codec_type"]=="video"]
    if not vs or vs[0]["width"]<1920 or vs[0]["height"]<1080:raise ValueError("Downloaded file is below Full HD")
    duration=float(info["format"]["duration"])
    print("VERIFIED HD SOURCE",src["id"],info["format"]["size"],vs[0]["width"],vs[0]["height"],duration,flush=True)
    if duration<55:raise ValueError("Clip is too short")
    return path,duration

def music(length,target):
    """Original low-volume instrumental. No synthetic narration."""
    sr=24000
    t=np.arange(int(sr*(length+1.0)),dtype=np.float64)/sr
    a=np.zeros(t.size)
    bpm=84; beat=60/bpm
    prog=[[196,246.94,293.66],[174.61,220,261.63],[164.81,207.65,246.94],[174.61,220,261.63]]
    for bar in range(math.ceil((length+1.0)/(beat*4))):
        onset=bar*beat*4
        mask=(t>=onset)&(t<onset+beat*4)
        x=t[mask]-onset
        for f in prog[bar%4]:
            a[mask]+=0.06*np.sin(2*np.pi*f*x)*(0.75+0.16*np.cos(2*np.pi*.11*x))
    rng=np.random.default_rng(43)
    for k in range(math.ceil((length+1.0)/beat)):
        x=t-k*beat
        mask=(x>=0)&(x<0.18)
        y=x[mask]
        if not len(y):continue
        if k%4 in (0,2):a[mask]+=.21*np.sin(2*np.pi*(62*y-26*y*y))*np.exp(-y*23)
        else:a[mask]+=.045*rng.standard_normal(len(y))*np.exp(-y*32)
    fade=np.minimum(np.clip(t/.6,0,1),np.clip((length-t)/1.5,0,1))
    a=np.tanh(a*1.2)*fade
    wavfile.write(str(target),sr,(np.clip(a,-1,1)*24000).astype(np.int16))

def ass_time(sec):
    cs=round(float(sec)*100)
    return f"{cs//360000}:{(cs//6000)%60:02d}:{(cs//100)%60:02d}.{cs%100:02d}"

def build_captions(cards,dest):
    font=ImageFont.truetype(FONT,76)
    d=ImageDraw.Draw(Image.new("RGB",(W,H)))
    start="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,DejaVu Sans,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&HC0100D0D,-1,0,0,0,100,100,0,0,3,14,0,5,105,105,20,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    entries=[start]
    for c in cards:
        lines=c["lines"]
        if any(d.textbbox((0,0),t,font=font)[2]>855 for t in lines):
            # Dynamically scale long cards rather than cropping words or glyph descenders.
            longest=max(d.textbbox((0,0),t,font=font)[2] for t in lines)
            fontsize=max(49,round(76*845/longest))
        else:fontsize=76
        if any(d.textbbox((0,0),t,font=ImageFont.truetype(FONT,fontsize))[2]>920 for t in lines):
            raise ValueError("Oversized caption (requires author rewrite)")
        emph=int(c.get("emphasis",-1))
        parts=[]
        for i,l in enumerate(lines):
            escaped=l.replace("{","").replace("}","").replace("\\","").replace("\n","")
            colour=r"{\c&H00EAD1A0&}" if i==emph else r"{\c&H00FFFFFF&}"
            parts.append(colour+escaped)
        pre=fr"{{\fs{fontsize}\fad(140,180)}}"
        entries.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Main,,0,0,0,,{pre}"+r"\N".join(parts)+"\n")
    dest.write_text("".join(entries),encoding="utf-8")

def render(paths,duration,brief):
    n=max(1,math.ceil(duration/10))
    segment_length=duration/n
    wav=OUT/"background_chill.wav"
    music(duration,wav)
    ass=OUT/"captions.ass"
    build_captions(brief["cards"],ass)
    inputs=[]
    for path,_ in paths:inputs+=["-i",str(path)]
    inputs+=["-i",str(wav)]
    count=[sum(1 for k in range(n) if k%len(paths)==i) for i in range(len(paths))]
    filters=[]
    for i,amount in enumerate(count):
        if amount:
            filters.append(f"[{i}:v]split={amount}"+ "".join(f"[src{i}_{j}]" for j in range(amount)))
    seq=[0]*len(paths)
    for k in range(n):
        src=k%len(paths)
        path,dur=paths[src]
        length=min(segment_length,duration-k*segment_length)
        start=(k//len(paths))*17+((src*11)%19)
        if start+length>dur-0.8:
            start=max(0,(start % max(1,dur-length-1)))
        name=f"src{src}_{seq[src]}";seq[src]+=1
        filters.append(f"[{name}]trim=start={start:.3f}:duration={length:.3f},setpts=PTS-STARTPTS,fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,eq=brightness=-0.035:saturation=1.04,setsar=1[v{k}]")
    filters.append("".join(f"[v{k}]" for k in range(n))+f"concat=n={n}:v=1:a=0[base]")
    filters.append("[base]subtitles="+str(ass)+":fontsdir=/usr/share/fonts/truetype/dejavu[final]")
    dest=OUT/"the_player_mind_review.mp4"
    run(["ffmpeg","-hide_banner","-nostdin","-y",*inputs,"-filter_complex",";".join(filters),
         "-map","[final]","-map",f"{len(paths)}:a:0","-t",str(duration),"-r",str(FPS),
         "-c:v","libx264","-preset","ultrafast","-crf","19","-threads","4",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",str(dest)])
    run(["ffmpeg","-hide_banner","-nostdin","-y","-ss","4","-i",str(dest),"-frames:v","1",str(OUT/"preview.png")])
    info=ffprobe(dest)
    v=[s for s in info["streams"] if s["codec_type"]=="video"]
    audio=[s for s in info["streams"] if s["codec_type"]=="audio"]
    if not v or v[0]["width"]!=1080 or v[0]["height"]!=1920 or not audio:raise RuntimeError("Output failed QA")
    if abs(float(info["format"]["duration"])-duration)>1.3:raise RuntimeError("Wrong video duration")
    print("VIDEO COMPLETE",json.dumps(info),flush=True)

def main():
    path,b,duration,sources=load_input()
    print("REVIEW BRIEF",path.name,b["title"],"GAME",sources[0]["game"],"DURATION",duration,flush=True)
    paths=[download(src,k) for k,src in enumerate(sources)]
    render(paths,duration,b)
    report={
      "title":b["title"],"brief":str(path.relative_to(ROOT)),"game":sources[0]["game"],
      "sources":b["sources"],"research":b["research"],
      "duration":duration,"status":"REVIEW_ONLY_UNPUBLISHED",
      "description":b.get("description",""),
      "youtube_title":b.get("youtube_title",b["title"]),
      "social_caption":b.get("social_caption",""),
      "approval_required":True
    }
    (OUT/"review_info.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    md=f"# Review: {b['title']}\n\n**Status:** Video rendered, not approved or published.\n\n**Game:** {sources[0]['game']}\n\n**Length:** {duration:.0f}s\n\n**Research:**\n"
    md+="".join(f"- {r.get('citation',r.get('title','Research'))}: {r.get('url','')}\n" for r in b["research"])
    md+=f"\n**Caption:** {b.get('social_caption','')}\n\n**Next:** Review the MP4 in the workflow artifact. Tell ChatGPT explicitly if you approve it for publishing. Do not publish automatically.\n"
    (OUT/"review_summary.md").write_text(md,encoding="utf-8")

if __name__=="__main__":main()
