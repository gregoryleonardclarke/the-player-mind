import urllib.request
u='https://www.gamersyde.com/news_20_minutes_of_skyrim_gameplay-11878_en.html'
try:
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=15)
    print('Gamersyde status:',r.status,'type:',r.headers.get('content-type'))
    print(r.read(2500).decode('utf-8',errors='replace'))
except Exception as e: print('Gamersyde:',str(e))
