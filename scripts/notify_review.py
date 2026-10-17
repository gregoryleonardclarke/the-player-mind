#!/usr/bin/env python3
"""Open exactly one GitHub review issue; assignee receives a GitHub notification."""
import json,os,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1]
info=json.loads((root/"output/review_info.json").read_text())
run_url=os.getenv("GITHUB_SERVER_URL","https://github.com")+"/"+os.environ["GITHUB_REPOSITORY"]+"/actions/runs/"+os.environ["GITHUB_RUN_ID"]
mark="<!-- tpm-review:"+info["brief"]+" -->"
title="🎬 Video ready for approval: "+info["title"]
out=subprocess.run(["gh","issue","list","--state","all","--limit","100","--json","number,body,url"],capture_output=True,text=True,check=True)
existing=[i for i in json.loads(out.stdout) if mark in (i.get("body") or "")]
if existing:
    print("Existing review issue:",existing[0]["url"])
    sys.exit(0)
summary=(root/"output/review_summary.md").read_text()
body=(mark+"\n"+summary+f"\n### Download and watch\n\n**[Download the Full HD MP4 from this GitHub Actions run]({run_url})** — open the run and select the player-mind-review-1080p artifact. The ZIP contains the MP4 and a still preview. GitHub login may be required.\n\n**Publishing is BLOCKED until you explicitly approve the video in ChatGPT.**\n")
res=subprocess.run(["gh","issue","create","--title",title,"--body",body,"--assignee",os.environ["GITHUB_REPOSITORY_OWNER"]],capture_output=True,text=True)
if res.returncode:
    raise RuntimeError("Could not create review issue: "+res.stderr)
print("REVIEW NOTIFICATION ISSUE:",res.stdout.strip())
