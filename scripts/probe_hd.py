import yt_dlp
urls=[
"https://www.dailymotion.com/video/x7tyy7q",
"https://www.dailymotion.com/video/x9xjfas",
"https://www.dailymotion.com/video/x4zuv5k",
"https://www.dailymotion.com/video/x8bw6sh",
"https://www.dailymotion.com/video/x8bw1q7",
"https://www.dailymotion.com/video/x8bw6fj",
"https://www.dailymotion.com/video/x8aemwx",
"https://www.dailymotion.com/video/xa0mtk4",
"https://www.dailymotion.com/video/x2ehr4k",
"https://www.dailymotion.com/video/x8bt6bm"
]
opts={"quiet":True,"no_warnings":True,"noplaylist":True,"skip_download":True,"socket_timeout":15}
with yt_dlp.YoutubeDL(opts) as yd:
 for url in urls:
  try:
   info=yd.extract_info(url,download=False)
   formats=sorted([(f.get("height") or 0, f.get("width") or 0, f.get("format_id"), f.get("ext"), f.get("tbr")) for f in info.get("formats",[])],reverse=True)
   print("FOUND",url,repr(info.get("title")),formats[:12],flush=True)
  except Exception as e:
   print("FAILED",url,str(e)[:350],flush=True)
