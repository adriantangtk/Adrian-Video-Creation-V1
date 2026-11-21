# GFX3: RISE 2.0 cinematic title system (landscape 1920x1080)

Files: `gfx3.css`, `gfx3.js` (global `GFX3`), `fonts/` (Inter, Newsreader, JetBrains Mono), `grain/noise.png`,
`vendor/gsap.min.js`. `index.html` is a 20 s test composition using every component on photos in `test/`.
Palette: red #DB0011, white, charcoal #1A1A1A, gold #C9A46A / #F3DDB0. Text safe x 120-1800, y 80-1000.

## Drop-in
1. Copy `gfx3.css`, `gfx3.js`, `fonts/*`, `grain/noise.png` into the project (keep folder names).
2. `<link rel="stylesheet" href="gfx3.css">`, `<script src="gfx3.js"></script>` after GSAP.
3. Add the hosts after the footage (each `class="g3-host clip"`, spanning the part of the video that uses it):
```html
<div id="g3-vignette" class="g3-host clip" ...></div>  <!-- static edge darkening, z 20 -->
<div id="g3-grain"    class="g3-host clip" ...></div>  <!-- z 22 -->
<div id="g3-chapter"  class="g3-host clip" ...></div>  <!-- z 30 -->
<div id="g3-houses"   class="g3-host clip" ...></div>  <!-- z 31 -->
<div id="g3-lt"       class="g3-host clip" ...></div>  <!-- z 32 -->
<div id="g3-captions" class="g3-host clip" data-track-kind="captions" ...></div>  <!-- z 40 -->
<div id="g3-outro"    class="g3-host clip" ...></div>  <!-- z 50 -->
<div id="g3-open"     class="g3-host clip" ...></div>  <!-- z 55 -->
<div id="g3-matte"    class="g3-host clip" ...></div>  <!-- letterbox bars, z 60 -->
<div id="g3-leak"     class="g3-host clip" ...></div>  <!-- z 65 -->
<div id="g3-flash"    class="g3-host clip" ...></div>  <!-- z 70 -->
<div id="g3-black"    class="g3-host clip" ...></div>  <!-- outro fade to black, z 75 -->
```
4. `const tl = gsap.timeline({paused:true}); GFX3.use(tl);` then the calls, then `window.__timelines["main"] = tl`.

All times are absolute seconds. Functions build their DOM once inside the hosts and only add tweens (no callbacks,
no randomness), so every frame is seek-safe.

## Functions
| Call | What |
|---|---|
| `letterbox(t0, t1, {ratio:2.39, inDur:.9, outDur:.7})` | Black matte bars ease in at t0, gone at t1 (`t1=null` keeps them). 2.39 -> bars cover y<138 and y>941. |
| `openTitle(t, dur, {kicker, title:"RISE", accent:"2.0", bg:1, flash:true})` | On black (`bg` = black opacity; 0.5 over footage): gold rule draws, spaced kicker tracks in, RISE 2.0 letters track in from the centre (Newsreader, 2.0 in gold), light sweep across the type, slow push; white flash peaks at t+dur (the impact), title cut under it. Needs ~4.5 s. Returns `{settled, end}`. |
| `chapter(t, word, {index:"01", total:"03", hold:1.2})` | Huge spaced Inter 700 word rises from a mask, gold `01 / 03`, red underline, soft centre scrim. Returns the time it is gone (~t+2.4). |
| `housesList(t, dur, names?, {title:"15+ YEARS ACROSS", beat:.48})` | Dark left panel, gold kicker + rule, one name per beat (default `GFX3.HOUSES`) with red dash + index; previous names dim, all relight after the last; exits at t+dur. Needs dur >= 0.48*(n+1)+0.8 (7 names: ~4.3 s). Returns `{beats}` (SFX cue times). |
| `lowerThird3(t, dur, {name:"REIN", full:"Reinald Goh", tag:"UHNW Clienteling Expert"})` | Red rule, name rises, sub-line slides in. y 672-832, left x 120. |
| `captions3(words, {offset, keywords, max:3, gap:.18, hold:.35, y:858, scrim:true})` | Whisper words `[{w\|text,start,end}]` -> 2-4 word groups, white Inter 700 72 px, keyword white on a red box, bottom scrim. y 858-962. One group at a time. Under a letterbox pass `y: 800`. |
| `outroTag(t, dur, {line:["Energise","Excite","Excel"], beat:.48, fadeDur:1.1})` | Scrim, RISE 2.0 tracks in + sweep, gold rule, phrases one per beat, fully black at t+dur. Needs >= 4 s. Returns `{phrases, black}`. |
| `grain(t0, t1, {fps:24, opacity:.10})` | Overlay-blended noise tile jumping position each frame (stepped tween). |
| `leak(t, {dur:.8, dir:"right"\|"left", peak:.9})` | Anamorphic warm/red glow + thin streak sweeps across, brightest at t (cut there). |
| `flash(t, {peak:1, inDur:.06, outDur:.35})` | White flash peaking at t. |
| `kenBurns(el, t, dur, {from:1.02, to:1.09, x, y, origin})` | Slow linear push for photos/footage (on the `<img>/<video>`). |

## Notes
- Do not put the HSBC logo in graphics; the real one is in the footage.
- Captions sit at y 858-962 and the lower third ends at 832: they never overlap. With a 2.39 letterbox the bottom bar starts at 941: lift captions with `{y:800}` or drop the matte during soundbites.
- Sound cues: impact-bass-2 at openTitle end-0.36; whoosh at each `leak` t-0.3; pop/click-hi per `housesList().beats`; soft sparkle at outro `phrases`.
- `hyperframes check`: 0 errors. Warnings: `nested_structure_needs_subcomposition` (test photo wrappers) and `negative_z_index` (caption key box, intended).
