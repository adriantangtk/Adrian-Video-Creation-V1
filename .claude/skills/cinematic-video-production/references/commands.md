# cvp.py command reference and JSON schemas

Load this only when you need an option or a schema. All commands take `-p <client>/<project>` (default: active project).

## Projects and sources
| command | does |
|---|---|
| `doctor` | checks Python, numpy, Pillow, FFmpeg/FFprobe + filters, curl, fonts, whisper, network. Drive and Chatcut are checked by you (connector tools). |
| `new <client> <project> [--drive ID \| --local DIR] [--title T]` | creates `$CVP_HOME/<client>/projects/<project>/`, copies the brief template, makes it active |
| `use <client>/<project>`, `list`, `status` | switch / list all / compact status |
| `source --drive ID \| --local DIR` | set or change the source folder |
| `drive-sync <listing> [--complete]` | diff a Drive listing (Drive JSON as saved by the connector, pages list, or TSV `id title size modifiedTime mimeType parentId [md5]`) against the manifest: new / changed / moved / removed / duplicate |
| `local-scan [--path DIR]` | same for a local folder (originals are read in place, never modified) |
| `fetch [--ids ...] [--jobs 3]` | downloads pending Drive media to `cache/media/` with resume + size check; a changed file's previous download is kept as `<id>.prev-<time>.<ext>` |
| `add-file <file>` | registers an uploaded file (copied into the cache) |
| `dig [--listing F --complete] [--language xx] [--no-transcribe]` | incremental refresh: sync → fetch → index → transcribe → report ids needing review |

Drive downloads use `drive.usercontent.google.com`, so files must be shared "Anyone with the link" (or be in a link-shared folder). If a download returns a web page, ask the owner to change sharing; never treat that as a deletion.

## Indexing (cached by sha256, re-runs skip unchanged media)
| command | output |
|---|---|
| `index [--ids] [--jobs N] [--force]` | `index/<id>/index.json` (probe, scenes, quality, audio loudness/silences, thumb list), `frames.jsonl.gz` (EVERY decoded frame: `n`, `t` pts, `scene` score, `y` luma, `sat`), `thumbs/t<ms>.jpg` (scene boundaries + regular interval, ≤48), `contact.jpg` |
| `transcribe [--ids] [--model small.en] [--language en] [--force]` | `index/<id>/transcript.json` words `{w,s,e}` + segments; stock whisper hallucinations over music/noise are dropped and listed. Machine transcript: verify names and quotes by ear before using them. |
| `digest [--new] [--all]` / `digest <id> [--since T]` | one line per clip / one clip's probe, quality, scenes, transcript, annotations, sheet paths |
| `find "<words>"` | search all transcripts, prints clip id + time + context |
| `frame <id> <t> [<t> ...] [--full]` | 1280px (or full-res) stills into `cache/frames/` |
| `sheet <id> <from> <to> [--step 0.5]` | contact sheet of a time range (≤36 frames) |

## Creative records (you write JSON, the script validates and persists)

### annotate <file.json>
```json
{"<media id>": {
  "summary": "Trainer opens the session, room laughs",
  "use": ["hook", "trainer", "reaction", "broll"],
  "people": [{"name": "unknown", "role": "trainer", "verified": false}],
  "shots": [{"t": 3.2, "shot": "MCU|wide|CU|insert|aerial", "action": "...", "speaker": "unknown|<verified name>",
             "dialogue": "exact words or empty", "emotion": "...", "quality": "good|soft|shaky|dark|blown", "use": "hook|broll|payoff|skip"}],
  "best_lines": [{"t": 3.2, "speaker": "unknown", "quote": "exact quote", "type": "line|trainer|reaction|broll", "note": "..."}],
  "coverage": "contact sheet + 3 stills"
}}
```

### hooks <file.json> [--merge]
List of hooks. Scores 0-10 for each of the six equal-weight criteria; the script computes `/10`, ranks, grabs a thumbnail.
```json
[{"clip": "m1a2b3c4d", "in": 12.4, "out": 15.9, "quote": "exact words", "action": "or a visual action",
  "speaker": "unknown", "overlay": "NOT A BUZZWORD",
  "scores": {"attention": 8, "curiosity": 7, "emotion": 7, "clarity": 9, "shareability": 7, "av_impact": 6},
  "why": "contrarian claim, clean audio", "selected_for": ["vertical"]}]
```

### storyboard <file.json> [--snap beat|bar|none] [--tolerance 0.12]
One file per format. The script checks every source in/out, computes the timeline, snaps cuts to the beat grid (by moving the previous shot's out-point when footage allows), and keeps earlier storyboards in `storyboards/history/`.
```json
{"format": "vertical", "fps": 30,
 "brand": {"accent": "#FF5A1F", "text": "#FFFFFF", "box": "#111111", "font": "Inter"},
 "music": {"track": "<music id>", "start": 0.0, "gain_db": -10, "fade_out": 1.5, "duck_threshold": 0.02, "duck_ratio": 8},
 "captions": {"enabled": true, "max_words": 3, "keywords": ["win"], "fixes": {"jon": "Jonn"}, "size": 66, "y": 1300},
 "loudness": -14, "crf": 20,
 "sfx": [{"file": "kit/sfx/sx-riser.wav", "at": 5.2, "gain_db": -8, "dur": 1.2}],
 "overlays": [{"text": "...", "style": "callout", "start": 9.0, "dur": 2}],
 "shots": [
  {"clip": "m1a2b3c4d", "in": 12.4, "out": 15.9, "speed": 1.0,
   "focus": [0.35, 0.45], "focus_to": [0.5, 0.45], "zoom": 1.0, "zoom_to": 1.1,
   "grade": "eq=contrast=1.05:saturation=1.08,colorbalance=rs=0.02",
   "audio": "source|mute", "audio_gain_db": 0, "speech": true,
   "transition": "cut|dissolve|fade|flash|whip|wipe|slide|zoom|<any xfade name>", "transition_dur": 0.3,
   "captions": "auto|none|[{\"text\":\"...\",\"start\":0.2,\"end\":1.4}]",
   "overlay": [{"text": "Not a buzzword", "style": "hook|kinetic|lower|callout", "anim": "pop|slide|type|fade",
                "start": 0.1, "dur": 1.8, "pos": [540, 420], "highlight": ["buzzword"]}],
   "sfx": [{"file": "kit/sfx/sx-impact-bass-2.wav", "at": -0.36, "gain_db": -6}],
   "dialogue": "for the storyboard table", "music_cue": "drop", "framing": "speaker left third", "purpose": "hook"},
  {"clip": "<photo id>", "dur": 2.5, "zoom": 1.0, "zoom_to": 1.08, "transition": "dissolve"}
 ]}
```
Notes: `focus` is the subject position (0-1) used to crop/reframe for each format; pick it from the contact sheet, do not centre-crop blindly. Times in a shot's `overlay`/`sfx` are relative to the shot start. `speed` ≥1.5 adds motion blur; a speed ramp is two consecutive shots at different speeds. Captions come from transcripts remapped through speed and cuts; keywords pop in the accent colour; all text is clamped to the format's safe zone (vertical x 60-940, y 250-1440).

## Music
| command | does |
|---|---|
| `music-add <file> --id ID --title T --artist A --source URL --license L [--verified]` | copies into the cache, records licence (UNVERIFIED unless `--verified`), builds `music/<id>/beats.json` |
| `beats <id> [--force]` | prints BPM, phrases, sections (build/drop/breakdown/climax), accents |
Write the three ranked recommendations to `music/recommendations.json` as `{"ranked":[{"title","why","license"}]}` so they appear in the artifact.

## Versions, render, QC, artifact
| command | does |
|---|---|
| `version-new --note "..."` | opens `versions/vNNN/` (never overwritten) |
| `render <landscape\|vertical> [--draft]` | per-shot intermediates cached in `cache/shots/` (reused across versions), one assembly pass: xfade transitions, natural sound, music ducked under speech, SFX, loudnorm -14 LUFS + limiter, ASS captions/overlays; H.264 High/AAC 48k, +faststart. Writes `<client>-<project>-<fmt>-vNNN.mp4`, `<fmt>.edl` (CMX 3600 for Premiere/Resolve), storyboard and captions copies, `render.json`. Drafts go to `drafts/`. |
| `qc [--version vNNN] [--file F --format fmt]` | resolution/codec/pix_fmt, black and frozen frames, loudness and true peak, 8 review stills + `stills/<fmt>-review.jpg` |
| `artifact` | rebuilds `artifact/index.html` + `artifact/clips/<id>.html`: inventory, every-frame index links, contact sheets, best lines, hook table, both storyboards, music + beat maps, versions/QC, scan log |
