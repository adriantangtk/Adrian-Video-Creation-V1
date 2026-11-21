# GFX kit: ray-seminar-recap

Files: `gfx.css` (styles + @font-face), `gfx.js` (global `GFX`), `fonts/`, `vendor/gsap.min.js`.
`index.html` is a 14.8 s test composition that uses every component on placeholder shots.

## Drop-in
1. Copy `gfx.css`, `gfx.js` and `fonts/*` into the project (keep the `fonts/` folder name; GSAP is already in `vendor/`).
2. `<link rel="stylesheet" href="gfx.css">` in `<head>` (or paste it into `<style>`), and `<script src="gfx.js"></script>` after GSAP.
3. Paste the DOM blocks below (from `index.html`) inside `#root`, after the footage. Set each host's `data-start`/`data-duration`.
4. In your timeline script: `const tl = gsap.timeline({paused:true}); GFX.use(tl);` then the calls, then register `window.__timelines["main"] = tl`.

All times are absolute seconds on the main timeline. Everything is deterministic (seek-safe).

## z-order (z-index)
footage 1-9 | `#gfx-vignette` 20 | `#gfx-hook` 30 | `#gfx-lt` 32 | `#gfx-captions` 40 | `#gfx-leak` 60 | `#gfx-flash` 70 | `#gfx-outro` 80

## DOM hosts (all `class="clip"` with data-start/duration)
```html
<div id="gfx-vignette" class="clip" ...></div>                    <!-- optional top/bottom darkening for legibility -->
<div id="gfx-hook" class="clip" ...><div class="hook-kicker">SALES SEMINAR · 20.11.2026</div><div class="hook-rule"></div><div class="hook-sub">with <b>Ray</b>, ex-Prada</div></div>
<div id="gfx-lt" class="clip" ...><div class="lt-bar"></div><div class="lt-mask name"><div class="lt-name">RAY</div></div><div class="lt-mask tag"><div class="lt-tag">Ex-Prada · 12 yrs training luxury sales</div></div></div>
<div id="gfx-captions" class="clip" data-track-kind="captions" ...></div>   <!-- span the whole video; groups are built by script -->
<div id="gfx-leak" class="clip" ...><div class="leak-glow"></div><div class="leak-bar"></div></div>
<div id="gfx-flash" class="clip" ...></div>
<div id="gfx-outro" class="clip" ...> .out-kicker, .out-title > .out-line.serif|.bold > span (one per line), .out-rule, .out-counter, .out-handle </div>
```

## Functions
| Call | What |
|---|---|
| `GFX.use(tl)` | Bind the paused main timeline. Call first. |
| `GFX.chunkWords(words, {max:3, gap:0.15, keywords:[]})` | Whisper words `[{w\|text, start, end}]` -> groups `{words, starts, end, keywordIndex}`; breaks at 3 words, punctuation, pauses >= gap. |
| `GFX.captionsFromWords(words, {offset, keywords, max, gap, hold:0.35, style, y})` | Chunk + call captionPill for each group. `offset` = where the soundbite's t=0 sits on the main timeline. Never shows two groups at once. |
| `GFX.captionPill(words[], startTimes[], keywordIndex, t0, {end, size, style:"shadow"\|"pill", y:1190, host})` | One 2-3 word group: white Inter 700 (auto 54-88 px) with shadow; keyword in a red #DB0011 pill; word-by-word pop at each start; hard kill at `end`. Sits at y 1190-1330. |
| `GFX.hookTitle(t0, dur, {kicker, sub})` | Red kicker tag + white rule draws + Newsreader sub-line, top of frame (y 300-480); fades out at t0+dur. Hook line itself = captions. |
| `GFX.whipIn(el, t, dir, {dur:0.16, dist:380, blur:44, rot:3.5})` | el arrives FROM `dir` (left/right/up/down) with SVG directional motion blur + rotation. |
| `GFX.whipOut(el, t, dir, {dur:0.14,...})` | el leaves TOWARD dir, ends at t+dur. |
| `GFX.whip(a, b, tCut, dir)` | a whips out (0.08 s) into the cut, b whips in from the opposite side at tCut. |
| `GFX.punchIn(el, t, {to:1.12, settle})` | Beat zoom snap. |
| `GFX.flash(t, {peak:1, outDur:0.22})` | Flash-to-white peaking at the cut t (uses `#gfx-flash`). |
| `GFX.redWipe(t, {dur:0.42, dir:"right"\|"left"})` | Skewed red bar + light-leak glow; screen is fully red at t: cut there. |
| `GFX.kenBurns(el, t, dur, {from:1.04, to:1.16, x:30, y:-20, origin})` | Slow push + drift for photos. |
| `GFX.lowerThird(t, dur, {name, tag})` | Red bar grows, name rises from mask, tag slides in; exits at t+dur. y 930-1110 (above the captions). |
| `GFX.outro(t, {counter:"20.11.2026", handle:"@adriantang", counterDur:1.1})` | Hard cut to white at t; kicker, title lines rise in (0.2 s apart), red rule draws, mono counter rolls and locks digit by digit, handle fades in. Returns `{counterDone, handleIn}` for SFX cues (with 3 title lines: lock done ~t+2.1, handle ~t+2.3). Needs ~3.8 s. |

## Rules / gotchas
- Transforms: `whip*`, `punchIn` and `kenBurns` all set transform on the element. Do not stack whip and kenBurns/punchIn on the SAME element: put the whip on an untimed wrapper `<div class="shot">` and kenBurns/punch on the `<video>`/`<img>` inside (as in `index.html`: `#s1` wrapper, `#p1` content). Give wrappers `overflow:hidden` and the media `inset:-40px` so zooms never show edges.
- No CSS `transform` on any element these functions animate.
- Text stays in the safe zone x 60-940, y 250-1440; centred blocks centre on x=500 (the safe-zone centre).
- SFX cue ideas: whoosh at each `whip` tCut-0.08; impact-bass-2 at outro t-0.36; click-hi per locking digit (~t+1.4..t+2.1); sparkle at `handleIn`.
- `hyperframes check`: passes (0 errors). Remaining warnings are `nested_structure_needs_subcomposition` (by design) and contrast on the placeholder labels.
