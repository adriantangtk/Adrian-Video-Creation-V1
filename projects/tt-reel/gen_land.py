#!/usr/bin/env python3
"""Landscape (1920x1080) graphics/captions/audio layer.  usage: python3 gen_land.py spec150  -> index.html
A spec module defines: DUR, BASE, NAT, MUSIC, CAPS, LABELS, VOICE, SFX, ITEMS (list of dicts), FLASH, PULSE."""
import importlib, sys, json
S = importlib.import_module(sys.argv[1])
DUR = S.DUR

def esc(s): return s.replace("&", "&amp;")

blocks, js = [], []
ti = [20]
def track():
    ti[0] += 1; return ti[0]

# ---------- captions ----------
for i, (a, b, t, g) in enumerate(S.CAPS):
    blocks.append(f'<div class="cap clip{" gold" if g else ""}" id="cap{i}" data-start="{a}" data-duration="{round(b-a,3)}" data-track-index="5"><span>{esc(t)}</span></div>')
# ---------- module labels ----------
for i, (a, t, sub) in enumerate(S.LABELS):
    blocks.append(f'<div class="lab clip" id="lab{i}" data-start="{a}" data-duration="1.8" data-track-index="6"><i></i><div><span>{esc(t)}</span>'
                  + (f'<small>{esc(sub)}</small>' if sub else '') + '</div></div>')
# ---------- free items ----------
for k, it in enumerate(S.ITEMS):
    iid = it.get("id", f"it{k}")
    cls = it.get("cls", "big")
    blocks.append(f'<div id="{iid}" class="{cls} clip" data-start="{it["t"]}" data-duration="{it["d"]}" data-track-index="{track()}" style="{it.get("style","")}">{it["html"]}</div>')
    anim = it.get("anim", "pop")
    t0, t1 = it["t"], round(it["t"] + it["d"], 3)
    if anim == "pop":
        js.append(f'tl.fromTo("#{iid}", {{opacity:0, scale:1.35, filter:"blur(12px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.32, ease:"expo.out"}}, {t0});')
    elif anim == "up":
        js.append(f'tl.fromTo("#{iid}", {{opacity:0, y:70}}, {{opacity:1, y:0, duration:.38, ease:"expo.out"}}, {t0});')
    elif anim == "tilt":
        js.append(f'tl.fromTo("#{iid}", {{opacity:0, rotationX:-70, y:60, transformPerspective:900}}, {{opacity:1, rotationX:0, y:0, duration:.5, ease:"back.out(1.4)"}}, {t0});')
    elif anim == "fade":
        js.append(f'tl.fromTo("#{iid}", {{opacity:0}}, {{opacity:1, duration:.3}}, {t0});')
    if it.get("drift", True) and anim != "fade":
        js.append(f'tl.to("#{iid}", {{scale:1.04, duration:{max(0.3, it["d"]-0.6):.2f}, ease:"none"}}, {t0 + 0.4});')
    if not it.get("hold"):
        js.append(f'tl.to("#{iid}", {{opacity:0, duration:.14, ease:"power2.in"}}, {t1 - 0.14:.3f});')
    for sub in it.get("stagger", []):   # (selector, time)
        js.append(f'tl.fromTo("#{iid} {sub[0]}", {{opacity:0, y:40, scale:.8}}, {{opacity:1, y:0, scale:1, duration:.3, ease:"back.out(2)"}}, {sub[1]});')
    for cnt in it.get("counters", []):  # (selector, from, to, time, dur, prefix, suffix)
        sel, a, b, tt, dd, pre, suf = cnt
        js.append(f'(() => {{ const o={{v:{a}}}, el=document.querySelector("#{iid} {sel}"); tl.fromTo(o,{{v:{a}}},{{v:{b},duration:{dd},ease:"power2.out",onUpdate:()=>{{el.textContent="{pre}"+Math.round(o.v).toLocaleString("en-US")+"{suf}";}}}},{tt}); tl.call(()=>{{el.textContent="{pre}{b}{suf}";}},null,{tt+dd+0.01}); }})();')

caps_js = '''
document.querySelectorAll(".cap").forEach(el => { const s=+el.dataset.start, d=+el.dataset.duration;
  tl.fromTo(el,{opacity:0,scale:.7,y:16},{opacity:1,scale:1,y:0,duration:.16,ease:"back.out(2.2)"},s);
  tl.to(el,{opacity:0,duration:.06},s+d-.06); });
document.querySelectorAll(".lab").forEach(el => { const s=+el.dataset.start;
  tl.fromTo(el.querySelector("i"),{scaleY:0},{scaleY:1,duration:.18,ease:"power3.out"},s);
  tl.fromTo(el,{opacity:0,x:-90},{opacity:1,x:0,duration:.26,ease:"expo.out"},s);
  tl.to(el,{opacity:0,x:60,duration:.15,ease:"power2.in"},s+1.64); });
'''
flash_js = "".join(f'tl.fromTo("#flash",{{opacity:.8}},{{opacity:0,duration:.35,ease:"power2.out",immediateRender:false}},{t});' for t in S.FLASH)
leak_js = "".join(f'tl.fromTo("#leak",{{opacity:0,x:-500}},{{opacity:.85,x:200,duration:.35,ease:"power1.in",immediateRender:false}},{t-0.3});'
                  f'tl.to("#leak",{{opacity:0,x:700,duration:.45,ease:"power1.out"}},{t+0.05});' for t in getattr(S, "LEAKS", []))
# beat pulse on the footage: quick punch-in on chosen beats
pulse_js = "".join(f'tl.fromTo("#base",{{scale:1.045}},{{scale:1,duration:.32,ease:"power2.out",immediateRender:false}},{t});' for t in S.PULSE)
# letterbox bars
bars_js = "".join(f'tl.fromTo([".lb"],{{scaleY:0}},{{scaleY:1,duration:.4,ease:"power2.out",immediateRender:false}},{a});tl.to([".lb"],{{scaleY:0,duration:.3,ease:"power2.in"}},{b-0.3});' for a, b in getattr(S, "LETTERBOX", []))

voice = [f'<audio id="{n}" src="voice/{n}.wav" data-role="voice" data-start="{s}" data-duration="{d}" data-volume="{getattr(S,"VOICE_VOL",1.0)}"></audio>' for n, s, d in S.VOICE]
sfx = [f'<audio id="fx{i}" src="sfx/{f}.wav" data-start="{s}" data-volume="{v}" data-duration="{d}"></audio>' for i, (f, s, v, d) in enumerate(S.SFX)]

html = f'''<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="vendor/gsap.min.js"></script>
<style>
  @font-face {{ font-family: "Inter"; src: url("fonts/inter-latin-500-normal.woff2"); font-weight: 500; }}
  @font-face {{ font-family: "Inter"; src: url("fonts/inter-latin-600-normal.woff2"); font-weight: 600; }}
  @font-face {{ font-family: "Inter"; src: url("fonts/inter-latin-700-normal.woff2"); font-weight: 700; }}
  :root {{ --navy:#0B1533; --navy2:#141F4A; --gold:#F5B623; --amber:#E8961E; --blue:#2F6BFF; --mist:#D9DEEA; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1920px; height:1080px; overflow:hidden; background:var(--navy); }}
  #root {{ width:100%; height:100%; position:relative; overflow:hidden; font-family:"Inter", Arial, sans-serif; color:#fff; }}
  .full {{ position:absolute; inset:0; width:1920px; height:1080px; }}
  #base {{ object-fit:cover; transform-origin:50% 50%; }}
  #vig {{ background: radial-gradient(ellipse at 50% 50%, rgba(11,21,51,0) 55%, rgba(11,21,51,.55) 100%),
          linear-gradient(180deg, rgba(11,21,51,.35) 0%, rgba(11,21,51,0) 22%, rgba(11,21,51,0) 62%, rgba(11,21,51,.7) 100%); }}
  #flash {{ background:#fff; opacity:0; }}
  #leak {{ position:absolute; top:-200px; left:0; width:1100px; height:1480px; opacity:0; mix-blend-mode:screen;
          background: radial-gradient(ellipse at 50% 50%, rgba(255,170,60,.9) 0%, rgba(255,120,30,.45) 35%, rgba(255,90,20,0) 70%); }}
  .lb {{ position:absolute; left:0; width:1920px; height:120px; background:#000; transform:scaleY(0); }}
  #lbT {{ top:0; transform-origin:top; }} #lbB {{ bottom:0; transform-origin:bottom; }}
  /* captions */
  .cap {{ position:absolute; left:160px; width:1600px; top:850px; text-align:center; opacity:0; }}
  .cap span {{ display:inline-block; padding:14px 34px 17px; border-radius:20px; background:rgba(11,21,51,.84);
        font-weight:700; font-size:62px; line-height:1; letter-spacing:-.02em; box-shadow:0 10px 40px rgba(0,0,0,.35); }}
  .cap.gold span {{ background:var(--gold); color:var(--navy); font-size:76px; }}
  /* labels */
  .lab {{ position:absolute; left:120px; top:110px; opacity:0; display:flex; align-items:center; gap:22px; }}
  .lab i {{ display:block; width:12px; height:104px; background:var(--gold); border-radius:3px; }}
  .lab span {{ display:block; font-weight:700; font-size:72px; letter-spacing:-.02em; line-height:1; text-shadow:0 6px 30px rgba(0,0,0,.6); }}
  .lab small {{ display:block; margin-top:8px; font-size:30px; font-weight:600; color:var(--mist); letter-spacing:.02em; text-shadow:0 4px 20px rgba(0,0,0,.7); }}
  /* big centred type */
  .big {{ position:absolute; left:160px; width:1600px; text-align:center; font-weight:700; letter-spacing:-.03em; line-height:.98;
        text-shadow:0 6px 30px rgba(0,0,0,.75), 0 0 2px rgba(0,0,0,.5); opacity:0; padding:46px 0 50px;
        background: radial-gradient(ellipse 62% 58% at 50% 50%, rgba(8,14,36,.78) 0%, rgba(8,14,36,.45) 55%, rgba(8,14,36,0) 100%); }}
  .g {{ color:var(--gold); }}
  .kick {{ display:block; font-size:30px; font-weight:600; letter-spacing:.3em; color:var(--gold); margin-bottom:18px; }}
  .panel {{ position:absolute; opacity:0; }}
  .dim {{ position:absolute; inset:0; width:1920px; height:1080px; background:rgba(11,21,51,.78); opacity:0; }}
  .navy {{ position:absolute; inset:0; width:1920px; height:1080px; background:radial-gradient(ellipse at 50% 40%, #1B2A63 0%, var(--navy) 65%); opacity:0; }}
  /* lower third */
  .lt {{ position:absolute; left:120px; top:800px; opacity:0; padding:18px 30px 20px; background:rgba(11,21,51,.86);
        border-left:10px solid var(--gold); border-radius:6px; }}
  .lt b {{ display:block; font-size:46px; font-weight:700; }}
  .lt small {{ display:block; margin-top:6px; font-size:27px; font-weight:500; color:var(--mist); }}
  /* stats */
  .stats {{ display:flex; justify-content:center; gap:46px; }}
  .stat {{ width:340px; text-align:center; opacity:0; }}
  .stat b {{ display:block; font-size:118px; font-weight:700; color:var(--gold); letter-spacing:-.04em; line-height:1; }}
  .stat small {{ display:block; margin-top:10px; font-size:32px; font-weight:600; color:#fff; }}
  /* award cards */
  .cards {{ display:flex; justify-content:center; gap:44px; }}
  .card {{ width:480px; height:480px; border-radius:24px; overflow:hidden; position:relative; opacity:0;
        box-shadow:0 30px 80px rgba(0,0,0,.6), 0 0 0 4px rgba(245,182,35,.7); }}
  .card img {{ width:100%; height:100%; object-fit:cover; }}
  .card .m {{ position:absolute; left:0; right:0; bottom:0; padding:16px 10px; text-align:center; font-weight:700; font-size:32px;
        background:linear-gradient(0deg, rgba(11,21,51,.96), rgba(11,21,51,0)); }}
  /* timeline */
  .tline {{ display:flex; justify-content:center; gap:28px; }}
  .yr {{ width:400px; opacity:0; }}
  .yr .ph {{ width:400px; height:280px; border-radius:16px; overflow:hidden; box-shadow:0 0 0 3px rgba(245,182,35,.6); }}
  .yr .ph img {{ width:100%; height:100%; object-fit:cover; }}
  .yr b {{ display:block; margin-top:16px; font-size:60px; color:var(--gold); font-weight:700; }}
  .yr small {{ display:block; margin-top:6px; font-size:28px; font-weight:600; line-height:1.25; color:#fff; }}
  /* pillars */
  .pill4 {{ display:flex; justify-content:center; gap:24px; }}
  .pill4 div {{ width:380px; padding:26px 20px; border-radius:18px; background:rgba(11,21,51,.82); border-top:8px solid var(--gold);
        font-size:36px; font-weight:700; line-height:1.15; opacity:0; text-align:center; }}
  /* end card */
  #logo {{ position:absolute; left:610px; top:200px; width:700px; opacity:0; }}
  #bar {{ position:absolute; left:0; top:0; height:6px; width:1920px; background:var(--gold); transform-origin:left center; }}
</style>
</head>
<body>
<div id="root" data-composition-id="tt-reel" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1920" data-height="1080">
  <video id="base" class="full clip" src="{S.BASE}" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
  <div id="vig" class="full clip" data-start="0" data-duration="{DUR}" data-track-index="1"></div>
  <div id="leak" class="clip" data-start="0" data-duration="{DUR}" data-track-index="2"></div>
  <div id="lbT" class="lb clip" data-start="0" data-duration="{DUR}" data-track-index="3"></div>
  <div id="lbB" class="lb clip" data-start="0" data-duration="{DUR}" data-track-index="4"></div>
  {chr(10).join("  " + b for b in blocks)}
  <img id="logo" class="clip" src="assets/tt-logo.svg" data-start="{S.END_AT}" data-duration="{round(DUR-S.END_AT,3)}" data-track-index="90">
  <div id="flash" class="full clip" data-start="0" data-duration="{DUR}" data-track-index="98"></div>
  <div id="bar" class="clip" data-start="0" data-duration="{DUR}" data-track-index="99"></div>
  <audio id="music" src="{S.MUSIC}" data-start="0" data-duration="{DUR}" data-volume="{S.MUSIC_VOL}"></audio>
  <audio id="nat" src="{S.NAT}" data-start="0" data-duration="{DUR}" data-volume="{S.NAT_VOL}"></audio>
  {chr(10).join("  " + a for a in voice + sfx)}
</div>
<script>
  const tl = gsap.timeline({{ paused: true }});
  tl.set("#flash", {{ opacity: 0 }}, 0); tl.set("#leak", {{ opacity: 0 }}, 0); tl.set("#base", {{ scale: 1 }}, 0);
  tl.fromTo("#bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {DUR}, ease: "none" }}, 0);
  {caps_js}
  {flash_js}
  {leak_js}
  {pulse_js}
  {bars_js}
  {chr(10).join("  " + j for j in js)}
  tl.fromTo("#logo", {{ opacity: 0, scale: .82 }}, {{ opacity: 1, scale: 1, duration: .6, ease: "expo.out" }}, {S.END_AT + 0.15});
  window.__timelines = window.__timelines || {{}};
  window.__timelines["tt-reel"] = tl;
  tl.seek(0);
</script>
</body>
</html>
'''
open(getattr(S, "OUT", "index.html"), "w").write(html)
print("written", getattr(S, "OUT", "index.html"))
