# Footage scouting brief — Thriving Talents hype reel

We are cutting a Tony-Robbins-style hype reel for **Thriving Talents** (Malaysian corporate training firm,
CEO Michael Teoh): team building, keynotes, workshops. Two cuts: 75 s and 2.5 min, vertical 1080x1920.
Style: a hard cut roughly every 1 s, drone/wide establishing shots, speed ramps, crowd energy, emotional
slow middle, big finish. Hook: "What if Monday felt like this?" over the loudest, highest-energy moment.

## Hard rules
- **No client company logos on screen** (PNC). Flag every shot where a client logo, banner, backdrop, lanyard
  print or branded shirt is readable. Thriving Talents' own logo is fine.
- Download with:
  `curl -sL "https://drive.usercontent.google.com/download?id=<FILE_ID>&export=download&confirm=t" -o <path>`
  Use the Google Drive MCP tool `mcp__Google_Drive__search_files` (load it with ToolSearch
  `select:mcp__Google_Drive__search_files`) to list folders: query `parentId = '<id>'` or
  `'<id>' in ancestors and mimeType contains 'video/'`, with `excludeContentSnippets: true`. Big results get
  saved to a file: read them with `jq`.
- Save originals under `/home/user/Adrian-Video-Creation-V1/projects/tt-reel/media/<your-tag>/` (git-ignored).
  Keep originals (we cut the final from them). Skip single files over 1.2 GB unless the folder has nothing else.
  Budget: about 8 GB of downloads for your share.
- The machine has 4 CPUs shared with other agents: do NOT transcode whole clips. Look at footage with fast seeks:
  `ffmpeg -ss T -i file -frames:v 1 -vf scale=-2:360 out.jpg`, or a tile sheet built from such frames
  (e.g. one frame every 2 s, `tile=6x5`). Use `ffprobe` for duration, resolution, rotation, fps.
- Never run `hyperframes render`.

## What to deliver
Write `/home/user/Adrian-Video-Creation-V1/projects/tt-reel/catalog/<your-tag>.jsonl`, one JSON object per
usable shot (aim for the 25-40 best, not everything):

```json
{"file":"media/<tag>/x.mp4","src_id":"<drive id>","folder":"<drive folder name>","in":12.3,"out":15.8,
 "orient":"portrait|landscape","res":"1920x1080","fps":30,
 "type":"drone|wide|crowd|close|speaker|activity|celebration|detail|photo",
 "desc":"what happens, one line","energy":1-5,"quality":"sharp|soft|shaky",
 "logo_risk":"none|client-logo-visible (where)","use":"hook|montage|emotional|speaker|finale|broll"}
```
Photos: same format with `"type":"photo"` and no in/out. Then a short `<your-tag>.md` summary: the top 10 shots
for the hook/finale, how many people appear in sessions, any trainer/speaker names you can see, and any problems.
Return a summary of at most 15 lines.
