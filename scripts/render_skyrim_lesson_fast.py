#!/usr/bin/env python3
"""Render a 118-second researched Skyrim psychology mini-lesson for review only. NEVER publish."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
import numpy as np
import subprocess, math, os, glob

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
W,H=1080,1920
DURATION=118
FPS=24
SOURCE="https://www.youtube.com/watch?v=5xwboyafbwc" # Bethesda Softworks official gameplay demo

def cmd(args):
    print("RUN", args, flush=True)
    subprocess.run(args, check=True)

def find_font():
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]:
        if Path(f).exists(): return f
    raise RuntimeError("No bold font installed")

def get_footages():
    """Fetch TWO verified original Full HD Skyrim gameplay clips from Internet Archive."""
    import json, urllib.request, urllib.parse
    ids=[
     "20111111-skyrim-gameplay-bleak-falls-barrow-boss-fight-116s-1920x-1080-q-99h-fmyt-oq",
     "20111111-skyrim-gameplay-join-the-stormcloak-rebellion-125s-1920x-1080-q-5f-w-jt-8-rao",
    ]
    paths=[]
    for idx, identifier in enumerate(ids):
        metadata_url="https://archive.org/metadata/"+identifier
        with urllib.request.urlopen(urllib.request.Request(metadata_url,headers={"User-Agent":"Mozilla/5.0"}), timeout=50) as result:
            meta=json.load(result)
        choices=[f for f in meta.get("files",[])
                 if f.get("source")=="original" and f.get("name","").lower().endswith(".mp4")
                 and int(f.get("width") or 0)>=1920 and int(f.get("height") or 0)>=1080]
        if not choices: raise RuntimeError("No 1080p original available for "+identifier)
        src=choices[0]
        url="https://archive.org/download/"+identifier+"/"+urllib.parse.quote(src["name"])
        target=OUT/f"skyrim_original_{idx}.mp4"
        print("DOWNLOADING original",idx,src["name"],url,flush=True)
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=180) as r, target.open("wb") as dest:
            while True:
                b=r.read(1024*1024)
                if not b:break
                dest.write(b)
        if target.stat().st_size<10000000:raise RuntimeError("Gameplay file too small")
        info=json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,duration","-of","json",str(target)]))["streams"][0]
        print("VERIFIED SOURCE",idx,info,"bytes",target.stat().st_size,flush=True)
        if int(info["width"])<1920 or int(info["height"])<1080:raise RuntimeError("Source not Full HD")
        paths.append(target)
    return paths

def make_music(path):
    """Original chill instrumental; no generative speech."""
    sr=32000
    tt=np.arange(int((DURATION+2)*sr), dtype=np.float64)/sr
    sound=np.zeros(len(tt))
    bpm=88
    beat=60/bpm
    chords=[
      [196.00,246.94,293.66],  # G
      [174.61,220.00,261.63],  # F
      [164.81,207.65,246.94],  # E minor-ish
      [174.61,220.00,261.63],
    ]
    for bar in range(math.ceil((DURATION+2)/(beat*4))):
        start=bar*beat*4
        chord=chords[bar%4]
        segment=(tt>=start) & (tt<start+beat*4)
        st=tt[segment]-start
        for freq in chord:
            sound[segment] += .065*np.sin(2*np.pi*freq*st)*(0.68+0.22*np.cos(2*np.pi*.15*st))
    rng=np.random.default_rng(318)
    for k in range(int((DURATION+2)/beat)+2):
        onset=k*beat
        st=tt-onset
        active=(st>=0)&(st<0.26)
        if not active.any():continue
        x=st[active]
        if k%4 in (0,2):
            sound[active] += .29*np.sin(2*np.pi*(65*x-35*x*x))*np.exp(-x*22)
        if k%4 in (1,3):
            noise=rng.normal(0,1,active.sum())
            sound[active] += .08*noise*np.exp(-x*35)
    for k in range(int((DURATION+2)/(beat/2))+2):
        st=tt-k*beat/2
        active=(st>=0)&(st<.09)
        if active.any():
            noise=rng.normal(0,1,active.sum())
            sound[active]+=.025*noise*np.exp(-st[active]*60)
    fade=np.minimum(np.clip(tt/.6,0,1),np.clip((DURATION+.5-tt)/1.5,0,1))
    sound=np.tanh(sound*1.3)*fade
    wavfile.write(str(path),sr,(np.clip(sound,-1,1)*26000).astype(np.int16))

FONT=find_font()
card_data=[
  (0,4.5,["YOU HAVE 47 POTIONS.","WHY USE NONE?"],1),
  (4.5,10.5,["YOU'RE SAVING THEM","FOR SOMETHING WORSE."],1),
  (10.5,16.0,["EVEN WHEN A BOSS","IS DESTROYING YOU."],1),
  (16.0,22.0,["FIRST IDEA:","LOSS AVERSION."],1),
  (22.0,28.5,["IN SOME DECISIONS,","LOSSES FEEL HEAVIER","THAN SIMILAR GAINS."],1),
  (28.5,35.0,["DRINK THE RARE POTION:","IT'S DEFINITELY GONE."],1),
  (35.0,41.5,["KEEP IT IN YOUR BAG:","YOUR FUTURE OPTIONS","STAY OPEN."],2),
  (41.5,47.0,["THAT POSSIBILITY","CAN FEEL VALUABLE."],1),
  (47.0,53.5,["SECOND IDEA:","ANTICIPATED REGRET."],1),
  (53.5,60.0,["WHAT IF THE NEXT","FIGHT NEEDS IT MORE?"],1),
  (60.0,66.5,["WE SOMETIMES CHOOSE","TO AVOID REGRET","WE MIGHT FEEL LATER."],1),
  (66.5,73.0,["BUT THERE'S A COST:","YOU MISS THE BENEFIT","YOU COULD GET NOW."],1),
  (73.0,79.5,["THIRD PIECE:","UNCERTAINTY."],1),
  (79.5,86.0,["YOU DON'T KNOW","HOW MANY BOSSES","ARE STILL AHEAD."],1),
  (86.0,92.5,["SO THE PERFECT TIME","TO USE IT KEEPS","MOVING AWAY."],2),
  (92.5,99.0,["THESE ARE RESEARCHED","IDEAS ABOUT DECISIONS,","NOT A SKYRIM DIAGNOSIS."],1),
  (99.0,105.5,["TRY THIS EXPERIMENT:","USE ONE RARE POTION","IN A TOUGH FIGHT."],1),
  (105.5,112.5,["DID IT HELP YOU WIN?","THAT WAS THE VALUE","OF USING IT."],2),
  (112.5,118.0,["SO... WHAT ITEM","ARE YOU STILL","SAVING FOR LATER?"],2),
]
def make_card(index, lines, emphasis):
    img=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(img)
    font=ImageFont.truetype(FONT,78 if len(lines)<3 else 69)
    safe_w=885
    coords=[]
    for line in lines:
        box=d.textbbox((0,0),line,font=font,stroke_width=0)
        width=box[2]-box[0]
        if width>safe_w:
            # Fit text; rather than crop
            size=int(font.size*safe_w/width)
            f=ImageFont.truetype(FONT,max(45,size))
        else:f=font
        b=d.textbbox((0,0),line,font=f)
        coords.append((line,f,b,b[3]-b[1]))
    row_heights=[c[3]+42 for c in coords]
    total=sum(row_heights)
    start=(H-total)//2 - 42
    pad=26
    panel=(63,start-39,W-63,start+total+38)
    d.rounded_rectangle(panel, radius=33,fill=(9,12,23,205))
    y=start
    for i,(line,f,b,h) in enumerate(coords):
        width=d.textbbox((0,0),line,font=f)[2]
        x=(W-width)//2
        color=(255,209,98,255) if i==emphasis else (255,255,255,255)
        d.text((x,y),line,font=f,fill=color,stroke_width=2,stroke_fill=(5,7,12,255))
        y+=h+42
    path=OUT/f"caption_{index:02d}.png"
    img.save(path)
    return path

def render(footages):
    import json
    assert len(footages)==2
    audio=OUT/"chill_original_lesson.wav"
    make_music(audio)
    # ASS subtitles are composited once per frame (faster than 19 PNG decoders).
    def ts(sec):
        hh=int(sec//3600); mm=int((sec%3600)//60); ss=sec%60
        return f"{hh}:{mm:02d}:{ss:05.2f}"
    subtitle=OUT/"lesson_cards.ass"
    header="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,DejaVu Sans,68,&H00FFFFFF,&H000000FF,&H00000000,&HC0090C17,-1,0,0,0,100,100,0,0,3,14,2,5,95,95,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with subtitle.open("w") as sf:
        sf.write(header)
        for start,end,lines,emph in card_data:
            spans=[]
            for k,line in enumerate(lines):
                col=r"{\c&H62D1FF&}" if k==emph else r"{\c&HFFFFFF&}"
                spans.append(col+line)
            sf.write(f"Dialogue: 0,{ts(start)},{ts(end)},Main,,0,0,0,,{{\\fad(150,160)}}"+r"\N".join(spans)+"\n")
    inputs=["-i",str(footages[0]),"-i",str(footages[1]),"-i",str(audio)]
    chunks=12
    segments=[(k%2,(k//2)*20,min(10,DURATION-k*10)) for k in range(chunks)]
    a=sum(1 for x in segments if x[0]==0); b=chunks-a
    f=["[0:v]split="+str(a)+"".join(f"[a{i}]" for i in range(a)),
       "[1:v]split="+str(b)+"".join(f"[b{i}]" for i in range(b))]
    usage=[0,0]
    for k,(src,seek,length) in enumerate(segments):
        pin=f"a{usage[0]}" if src==0 else f"b{usage[1]}"
        usage[src]+=1
        f.append(f"[{pin}]trim=start={seek}:duration={length},setpts=PTS-STARTPTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},eq=brightness=-0.035:saturation=0.95,setsar=1[v{k}]")
    f.append("".join(f"[v{k}]" for k in range(chunks))+f"concat=n={chunks}:v=1:a=0[vbase]")
    f.append("[vbase]subtitles="+str(subtitle)+":fontsdir=/usr/share/fonts/truetype/dejavu[vout]")
    file=OUT/"skyrim_potion_psychology_mini_lesson.mp4"
    cmd(["ffmpeg","-hide_banner","-nostdin","-y",*inputs,"-filter_complex",";".join(f),
        "-map","[vout]","-map","2:a:0","-t",str(DURATION),"-r",str(FPS),
        "-c:v","libx264","-preset","ultrafast","-crf","19","-threads","4",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        "-movflags","+faststart",str(file)])
    cmd(["ffmpeg","-hide_banner","-nostdin","-y","-ss","20","-i",str(file),
        "-frames:v","1",str(OUT/"mini_lesson_preview.png")])
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height","-of","json",str(file)]))
    print("OUTPUT SUCCESS",info,flush=True)

if __name__=="__main__":
    render(get_footages())
