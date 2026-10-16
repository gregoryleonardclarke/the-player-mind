#!/usr/bin/env python3
"""Create one private-review Skyrim gameplay short. No Buffer API and no publishing."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
import numpy as np
import subprocess, math, os, glob

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
W,H=720,1280
DURATION=34
FPS=30
SOURCE="https://www.youtube.com/watch?v=5xwboyafbwc" # Bethesda Softworks official gameplay demo

def cmd(args):
    print("RUN", args, flush=True)
    subprocess.run(args, check=True)

def find_font():
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]:
        if Path(f).exists(): return f
    raise RuntimeError("No bold font installed")

def get_footage():
    if os.getenv("FOOTAGE_FILE") and Path(os.environ["FOOTAGE_FILE"]).exists():
        return Path(os.environ["FOOTAGE_FILE"])
    # Only real captured Skyrim gameplay: fail if unavailable; never substitute generated slides.
    targets=[
        ("https://www.dailymotion.com/video/x9xjfas", "whiterun_aerial", "*00:00:10-00:00:47"),
        ("https://www.dailymotion.com/video/x7tyy7q", "skyrim_playthrough", "*00:01:30-00:02:15"),
        ("https://vimeo.com/182690011", "vimeo_skyrim", "*00:00:00-00:00:40"),
        ("https://vimeo.com/713796833", "vimeo_skyrim2", "*00:00:00-00:00:40"),
        ("https://www.gamersyde.com/video_the_elder_scrolls_v_skyrim_gameplay_demo_part_1-23439_en.html", "bethesda_download", "*00:01:30-00:02:20"),
        ("https://www.youtube.com/watch?v=5xwboyafbwc", "official_bethesda", "*00:01:30-00:02:20"),
        ("https://www.youtube.com/watch?v=QWoF8S_F3Bo", "backup_gameplay", "*00:01:30-00:02:20"),
    ]
    for url, name, section in targets:
        pattern=str(OUT / (name+".%(ext)s"))
        args=[
          "yt-dlp","--no-playlist","--no-part","--no-warnings",
          "--download-sections",section,
          "--force-keyframes-at-cuts",
          "-f","bv*[height<=720]+ba/b[height<=720]/best",
          "--merge-output-format","mp4","-o",pattern,url
        ]
        try:
            cmd(args)
            candidates=sorted(OUT.glob(name+".*"),key=lambda x:x.stat().st_size,reverse=True)
            candidates=[c for c in candidates if c.suffix.lower() in {".mp4",".webm",".mkv"}]
            if candidates and candidates[0].stat().st_size>1000000:
                print("Selected real gameplay:",candidates[0])
                return candidates[0]
        except Exception as e:
            print("Source unavailable:",e,flush=True)
    raise RuntimeError("No genuine Skyrim gameplay could be downloaded. Deliberately refusing to render fake gameplay.")

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
  (0.0,3.8,["WHY DO WE HOARD","POTIONS IN SKYRIM?"],0),
  (3.8,7.6,["YOU SAVE THEM FOR","A REAL EMERGENCY."],1),
  (7.6,11.6,["THEN EVEN THE BOSS","DOESN'T FEEL WORTH IT."],0),
  (11.6,16.4,["ONE POSSIBLE REASON:","LOSS AVERSION."],1),
  (16.4,22.0,["USING IT MEANS","LOSING IT NOW.","KEEPING IT LEAVES OPTIONS."],2),
  (22.0,27.1,["THE FUTURE IS UNCERTAIN.","SO YOU WAIT."],1),
  (27.1,31.5,["AND FINISH WITH","47 UNUSED POTIONS."],0),
  (31.5,34.0,["WHAT ITEM DO","YOU ALWAYS HOARD?"],1),
]
def make_card(index, lines, emphasis):
    img=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(img)
    font=ImageFont.truetype(FONT,52 if len(lines)<3 else 46)
    safe_w=590
    coords=[]
    for line in lines:
        box=d.textbbox((0,0),line,font=font,stroke_width=0)
        width=box[2]-box[0]
        if width>safe_w:
            # Fit text; rather than crop
            size=int(font.size*safe_w/width)
            f=ImageFont.truetype(FONT,max(30,size))
        else:f=font
        b=d.textbbox((0,0),line,font=f)
        coords.append((line,f,b,b[3]-b[1]))
    row_heights=[c[3]+28 for c in coords]
    total=sum(row_heights)
    start=(H-total)//2 - 28
    pad=26
    panel=(42,start-26,W-42,start+total+25)
    d.rounded_rectangle(panel, radius=22,fill=(9,12,23,205))
    y=start
    for i,(line,f,b,h) in enumerate(coords):
        width=d.textbbox((0,0),line,font=f)[2]
        x=(W-width)//2
        color=(255,209,98,255) if i==emphasis else (255,255,255,255)
        d.text((x,y),line,font=f,fill=color,stroke_width=2,stroke_fill=(5,7,12,255))
        y+=h+28
    path=OUT/f"caption_{index:02d}.png"
    img.save(path)
    return path

def render(footage):
    audio=OUT/"chill_original.wav"
    make_music(audio)
    plates=[make_card(i,lines,emph) for i,(_,_,lines,emph) in enumerate(card_data)]
    # Source is actual captured video. 9:16 crop is centred for dynamic short-form view.
    # User review is via private Actions artifact; this workflow contains NO publish step.
    inputs=["-stream_loop","-1","-i",str(footage),"-i",str(audio)]
    for p in plates:inputs+=["-loop","1","-i",str(p)]
    filt=["[0:v]fps=30,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=brightness=-0.035:saturation=0.95,setsar=1[v0]"]
    last="v0"
    for i,(start,end,_,_) in enumerate(card_data):
        nxt=f"v{i+1}"
        # Caption overlays kept within 590 px width, well away from mobile UI bottom.
        filt.append(f"[{last}][{i+2}:v]overlay=0:0:enable='between(t,{start},{end-.02})'[{nxt}]")
        last=nxt
    cmd(["ffmpeg","-hide_banner","-y",*inputs,"-filter_complex",";".join(filt),
          "-map",f"[{last}]","-map","1:a:0","-t",str(DURATION),"-r",str(FPS),
          "-c:v","libx264","-preset","veryfast","-crf","23",
          "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
          "-movflags","+faststart",str(OUT/"skyrim_potions_review.mp4")])
    cmd(["ffmpeg","-hide_banner","-y","-ss","1.1","-i",str(OUT/"skyrim_potions_review.mp4"),
         "-frames:v","1",str(OUT/"preview.png")])
    print("RENDERED:",OUT/"skyrim_potions_review.mp4")

if __name__=="__main__":
    render(get_footage())
