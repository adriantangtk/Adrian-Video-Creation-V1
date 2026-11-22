#!/usr/bin/env python3
"""Writes index.html: graphics + captions + audio over the cut footage (media/base75.mp4)."""
DUR = 75.0

# ---------- captions (2-3 word pills, timed to the soundbites) ----------
# (start, end, text, gold?)
CAPS = [
    (3.09, 4.50, "HIGHEST ENERGY", False), (4.50, 5.85, "WINS.", True),
    (5.88, 6.98, "HIGHEST ENERGY", False), (6.98, 7.95, "WINS.", True),
    (15.70, 16.45, "IN LIFE,", False), (16.45, 17.20, "THERE IS NO", False), (17.20, 18.10, "FAILURE.", True),
    (18.10, 18.72, "THERE IS ONLY", False), (18.72, 20.40, "FEEDBACK.", True),
    (22.92, 24.10, "TEAM ONE,", False), (24.10, 26.40, "MAKE SOME NOISE!", True),
    (30.62, 31.95, "YOU CAN ALL BE", False), (31.95, 33.36, "EXCELLENT.", True),
    (33.36, 34.20, "JUST MAKE THE", False), (34.20, 35.40, "DECISION", True),
    (35.40, 35.80, "TO BE", False), (35.80, 37.40, "EXCELLENT.", True),
    (45.63, 46.95, "HOW WE DO ANYTHING", False), (46.95, 47.74, "IS HOW WE DO", False),
    (47.74, 49.20, "EVERYTHING.", True),
    (52.56, 53.90, "GIVE YOURSELF A HUGE", False), (53.90, 55.90, "ROUND OF APPLAUSE!", True),
]
# ---------- module labels on the drop ----------
LABELS = [(8.00, "TEAM BUILDING"), (9.86, "ENERGISERS"), (11.72, "TEAM CULTURE"), (13.58, "RETREATS")]
# ---------- audio ----------
VOICE = [("v1-energy", 3.00, 4.10), ("v2-feedback", 15.60, 3.95), ("v3-noise", 22.90, 4.20),
         ("v4-excellent", 30.60, 5.75), ("v5-everything", 45.40, 3.30), ("v6-applause", 52.536, 3.15)]
B, G0 = 0.4644, 0.109
def beat(k): return round(G0 + k * B, 3)
SFX = [  # (file, start, volume, duration)
    ("sx-impact-bass-2", 0.0, 0.55, 2.0), ("sx-whoosh", 0.45, 0.5, 0.6), ("sx-pop", 1.2, 0.5, 0.4), ("sx-pop-3", 1.6, 0.6, 0.4),
    ("sx-whoosh-cinematic", 2.8, 0.55, 1.2),
    ("sx-riser", 5.9, 0.5, 2.1), ("sx-impact-bass-1", 7.95, 0.55, 1.6),
    ("sx-pop", 8.05, 0.45, 0.4), ("sx-pop-2", 9.9, 0.45, 0.4), ("sx-pop-3", 11.76, 0.45, 0.4), ("sx-pop-4", 13.62, 0.45, 0.4),
    ("sx-whoosh-soft", 15.35, 0.5, 0.8), ("sx-click-hi", 15.65, 0.35, 0.3),
    ("sx-impact-bass-2", 22.5, 0.45, 1.6), ("sx-whoosh-soft", 30.2, 0.5, 0.8),
    ("sx-riser", 35.9, 0.45, 1.9), ("sx-impact-bass-2", 37.4, 0.55, 1.8),
    ("sx-pop-2", 38.2, 0.6, 0.4), ("sx-pop-3", 38.9, 0.6, 0.4), ("sx-pop-4", 39.6, 0.6, 0.4), ("sx-sparkle", 40.0, 0.5, 1.4),
    ("sx-whoosh-cinematic", 41.3, 0.5, 1.2), ("sx-impact-bass-1", 43.25, 0.45, 1.4), ("sx-sparkle", 43.4, 0.4, 1.4),
    ("sx-whoosh", 49.0, 0.5, 0.6), ("sx-click", 49.3, 0.3, 0.2), ("sx-impact-bass-1", 50.55, 0.45, 1.4),
    ("sx-whoosh-soft", 52.5, 0.45, 0.8), ("sx-whoosh", 56.05, 0.45, 0.6),
    ("sx-impact-bass-2", 59.65, 0.5, 1.8), ("sx-pop-3", 61.2, 0.5, 0.4), ("sx-whoosh-cinematic", 63.7, 0.5, 1.2),
    ("sx-impact-bass-2", 67.1, 0.55, 2.0), ("sx-sparkle", 67.7, 0.5, 1.4), ("sx-chime", 70.0, 0.35, 1.5),
]

def esc(s): return s.replace("&", "&amp;")
cap_html = "\n".join(
    f'  <div class="cap clip{" gold" if g else ""}" id="cap{i}" data-start="{a}" data-duration="{round(b-a,3)}" data-track-index="20"><span>{esc(t)}</span></div>'
    for i, (a, b, t, g) in enumerate(CAPS))
lab_html = "\n".join(
    f'  <div class="lab clip" id="lab{i}" data-start="{a}" data-duration="1.82" data-track-index="21"><i></i><span>{t}</span></div>'
    for i, (a, t) in enumerate(LABELS))
aud_html = "\n".join(
    [f'  <audio id="{n}" src="voice/{n}.wav" data-role="voice" data-start="{s}" data-duration="{d}" data-volume="1.0"></audio>' for n, s, d in VOICE]
    + [f'  <audio id="fx{i}" src="sfx/{f}.wav" data-start="{s}" data-volume="{v}" data-duration="{d}"></audio>' for i, (f, s, v, d) in enumerate(SFX)])

html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="vendor/gsap.min.js"></script>
<style>
  @font-face {{ font-family: "Inter"; src: url("fonts/inter-latin-500-normal.woff2"); font-weight: 500; }}
  @font-face {{ font-family: "Inter"; src: url("fonts/inter-latin-600-normal.woff2"); font-weight: 600; }}
  @font-face {{ font-family: "Inter"; src: url("fonts/inter-latin-700-normal.woff2"); font-weight: 700; }}
  :root {{ --navy: #0B1533; --navy2: #141F4A; --gold: #F5B623; --amber: #E8961E; --blue: #2F6BFF; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--navy); }}
  #root {{ width: 100%; height: 100%; position: relative; overflow: hidden; font-family: "Inter", Arial, sans-serif; color: #fff; }}
  .full {{ position: absolute; inset: 0; width: 1080px; height: 1920px; }}
  #base {{ object-fit: cover; }}
  #vig {{ background:
      linear-gradient(180deg, rgba(11,21,51,.55) 0%, rgba(11,21,51,0) 18%, rgba(11,21,51,0) 55%, rgba(11,21,51,.75) 100%); }}
  #flash {{ background: #fff; opacity: 0; }}
  /* hook */
  .hk {{ position: absolute; left: 60px; width: 880px; text-align: center; font-weight: 700; line-height: .95;
        letter-spacing: -0.03em; text-shadow: 0 8px 40px rgba(0,0,0,.55); opacity: 0; }}
  #hk1 {{ top: 640px; font-size: 104px; }}
  #hk2 {{ top: 750px; font-size: 190px; }}
  #hk3 {{ top: 950px; font-size: 104px; }}
  #hk4 {{ top: 1060px; font-size: 210px; color: var(--gold); }}
  /* captions */
  .cap {{ position: absolute; left: 60px; width: 880px; top: 1180px; text-align: center; opacity: 0; }}
  .cap span {{ display: inline-block; padding: 18px 34px 20px; border-radius: 22px; background: rgba(11,21,51,.82);
        font-weight: 700; font-size: 76px; line-height: 1; letter-spacing: -0.02em; box-shadow: 0 10px 40px rgba(0,0,0,.35); }}
  .cap.gold span {{ background: var(--gold); color: var(--navy); font-size: 96px; }}
  /* module labels */
  .lab {{ position: absolute; left: 60px; top: 300px; opacity: 0; display: flex; align-items: center; gap: 22px; }}
  .lab i {{ display: block; width: 14px; height: 92px; background: var(--gold); border-radius: 3px; }}
  .lab span {{ font-weight: 700; font-size: 84px; letter-spacing: -0.02em; line-height: 1; text-shadow: 0 6px 30px rgba(0,0,0,.6); }}
  /* name tag */
  #tag {{ position: absolute; left: 60px; top: 290px; opacity: 0; padding: 22px 30px; background: rgba(11,21,51,.85);
        border-left: 10px solid var(--gold); border-radius: 6px; }}
  #tag b {{ display: block; font-size: 54px; font-weight: 700; letter-spacing: -0.01em; }}
  #tag small {{ display: block; margin-top: 8px; font-size: 32px; font-weight: 500; color: #D9DEEA; }}
  .big {{ position: absolute; left: 60px; width: 880px; text-align: center; font-weight: 700; letter-spacing: -0.03em;
        line-height: .98; text-shadow: 0 8px 40px rgba(0,0,0,.6); opacity: 0; }}
  .gold-t {{ color: var(--gold); }}
  /* awards */
  #awBg {{ background: radial-gradient(ellipse at 50% 40%, rgba(20,31,74,.55), rgba(11,21,51,.92) 70%); opacity: 0; }}
  #awK {{ position: absolute; top: 270px; left: 60px; width: 880px; text-align: center; opacity: 0; }}
  #awK small {{ display: block; font-size: 34px; font-weight: 600; letter-spacing: .28em; color: var(--gold); }}
  #awK b {{ display: block; margin-top: 14px; font-size: 76px; font-weight: 700; letter-spacing: -0.02em; line-height: 1; }}
  .card {{ position: absolute; width: 430px; height: 430px; border-radius: 26px; overflow: hidden; opacity: 0;
        box-shadow: 0 30px 80px rgba(0,0,0,.6), 0 0 0 4px rgba(245,182,35,.65); }}
  .card img {{ width: 100%; height: 100%; object-fit: cover; }}
  #cG {{ left: 325px; top: 520px; z-index: 3; }}
  #cS {{ left: 80px; top: 890px; z-index: 2; }}
  #cB {{ left: 570px; top: 890px; z-index: 2; }}
  .medal {{ position: absolute; left: 0; right: 0; bottom: 0; padding: 12px; text-align: center; font-weight: 700; font-size: 34px;
        background: linear-gradient(0deg, rgba(11,21,51,.95), rgba(11,21,51,0)); }}
  #soba {{ position: absolute; left: 60px; top: 1120px; width: 880px; opacity: 0; text-align: center; }}
  #soba small {{ display: block; font-size: 36px; font-weight: 600; letter-spacing: .22em; color: var(--gold); }}
  #soba b {{ display: inline-block; margin-top: 14px; padding: 14px 30px; background: var(--gold); color: var(--navy);
        font-size: 80px; font-weight: 700; border-radius: 16px; letter-spacing: -0.02em; }}
  #soba em {{ display: block; margin-top: 14px; font-style: normal; font-size: 40px; font-weight: 600; }}
  /* stats */
  #stBg {{ background: rgba(11,21,51,.72); opacity: 0; }}
  #st {{ position: absolute; left: 60px; width: 880px; top: 470px; text-align: center; opacity: 0; }}
  #stN {{ font-size: 380px; font-weight: 700; line-height: .9; color: var(--gold); letter-spacing: -0.05em; }}
  #stL {{ font-size: 88px; font-weight: 700; letter-spacing: -0.02em; margin-top: 10px; }}
  #stY {{ display: flex; justify-content: center; gap: 26px; margin-top: 46px; }}
  #stY div {{ padding: 14px 26px; border: 3px solid var(--gold); border-radius: 14px; font-size: 52px; font-weight: 700; opacity: 0; }}
  #stS {{ font-size: 44px; font-weight: 600; color: #D9DEEA; margin-top: 40px; }}
  #trust {{ top: 560px; font-size: 92px; }}
  /* end card */
  #endBg {{ background: radial-gradient(ellipse at 50% 38%, #1B2A63 0%, var(--navy) 62%); opacity: 0; }}
  #logo {{ position: absolute; left: 90px; top: 520px; width: 900px; opacity: 0; }}
  #endT {{ position: absolute; left: 60px; width: 880px; top: 900px; text-align: center; opacity: 0;
        font-size: 42px; font-weight: 600; line-height: 1.35; color: #D9DEEA; }}
  #endT b {{ color: #fff; }}
  #cta {{ position: absolute; left: 140px; width: 800px; top: 1130px; text-align: center; opacity: 0;
        padding: 30px 0 32px; background: var(--gold); color: var(--navy); border-radius: 999px; font-size: 62px; font-weight: 700; }}
  #credit {{ position: absolute; left: 60px; width: 880px; top: 1360px; text-align: center; opacity: 0;
        font-size: 24px; font-weight: 500; color: rgba(217,222,234,.7); }}
  #bar {{ position: absolute; left: 0; top: 0; height: 8px; width: 1080px; background: var(--gold); transform-origin: left center; }}
</style>
</head>
<body>
<div id="root" data-composition-id="tt-reel" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">
  <video id="base" class="full clip" src="media/base75.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
  <div id="vig" class="full clip" data-start="0" data-duration="{DUR}" data-track-index="1"></div>

  <div id="hk1" class="hk clip" data-start="0" data-duration="2.95" data-track-index="10">WHAT IF</div>
  <div id="hk2" class="hk clip" data-start="0" data-duration="2.95" data-track-index="11">MONDAY</div>
  <div id="hk3" class="hk clip" data-start="0" data-duration="2.95" data-track-index="12">FELT LIKE</div>
  <div id="hk4" class="hk clip" data-start="0" data-duration="2.95" data-track-index="13">THIS?</div>

{lab_html}

  <div id="tag" class="clip" data-start="15.5" data-duration="1.8" data-track-index="22"><b>Michael Teoh</b><small>Founder &amp; CEO, Thriving Talents</small></div>
  <div id="kn" class="big clip" data-start="20.5" data-duration="2.3" data-track-index="23" style="top:560px;font-size:104px">KEYNOTES THAT<br><span class="gold-t">MOVE ROOMS.</span></div>
  <div id="one" class="big clip" data-start="26.4" data-duration="3.85" data-track-index="23" style="top:600px;font-size:118px">ONE ROOM.<br><span class="gold-t">ONE ENERGY.</span></div>

  <div id="awBg" class="full clip" data-start="37.72" data-duration="3.75" data-track-index="30"></div>
  <div id="awK" class="clip" data-start="37.72" data-duration="3.75" data-track-index="31"><small>HR VENDORS OF THE YEAR 2026</small><b>3 AWARDS. ONE NIGHT.</b></div>
  <div id="cS" class="card clip" data-start="37.72" data-duration="3.75" data-track-index="32"><img src="assets/hrv-silver.png"><div class="medal">SILVER · Management Training</div></div>
  <div id="cB" class="card clip" data-start="37.72" data-duration="3.75" data-track-index="33"><img src="assets/hrv-bronze.png"><div class="medal">BRONZE · Instructional Design</div></div>
  <div id="cG" class="card clip" data-start="37.72" data-duration="3.75" data-track-index="34"><img src="assets/hrv-gold.png"><div class="medal">GOLD · Best Team Building</div></div>
  <div id="soba" class="clip" data-start="41.43" data-duration="3.72" data-track-index="35"><small>THE STAR SOBA 2024</small><br><b>BEST EMPLOYER</b><em>Star Outstanding Business Awards</em></div>

  <div id="stBg" class="full clip" data-start="49.2" data-duration="3.38" data-track-index="40"></div>
  <div id="st" class="clip" data-start="49.2" data-duration="3.38" data-track-index="41">
    <div id="stN">7</div><div id="stL">INDUSTRY AWARDS</div>
    <div id="stY"><div>2024</div><div>2025</div><div>2026</div></div>
    <div id="stS">Award-winning, three years running</div>
  </div>
  <div id="trust" class="big clip" data-start="56.0" data-duration="3.9" data-track-index="42">TRUSTED BY<br><span class="gold-t">BANKS, INSURERS</span><br>&amp; GLOBAL BRANDS</div>

  <div id="ct1" class="big clip" data-start="60.0" data-duration="3.6" data-track-index="43" style="top:640px;font-size:150px">YOUR TEAM<br><span class="gold-t">IS NEXT.</span></div>
  <div id="ct2" class="big clip" data-start="63.72" data-duration="3.7" data-track-index="44" style="top:600px;font-size:104px">LET'S MAKE<br>MONDAY<br><span class="gold-t">FEEL LIKE THIS.</span></div>

  <div id="endBg" class="full clip" data-start="67.45" data-duration="{round(DUR-67.45,2)}" data-track-index="50"></div>
  <img id="logo" class="clip" src="assets/tt-logo.svg" data-start="67.45" data-duration="{round(DUR-67.45,2)}" data-track-index="51">
  <div id="endT" class="clip" data-start="67.45" data-duration="{round(DUR-67.45,2)}" data-track-index="52"><b>Team building · Keynotes · Leadership</b><br>HR Vendors of the Year 2026 · Gold</div>
  <div id="cta" class="clip" data-start="67.45" data-duration="{round(DUR-67.45,2)}" data-track-index="53">DM us to book your team</div>
  <div id="credit" class="clip" data-start="67.45" data-duration="{round(DUR-67.45,2)}" data-track-index="54">Music: “Inspiring Progress” by Soundrider/Dope · CC BY 3.0 · jamendo.com</div>

{cap_html}
  <div id="flash" class="full clip" data-start="0" data-duration="{DUR}" data-track-index="60"></div>
  <div id="bar" class="clip" data-start="0" data-duration="{DUR}" data-track-index="61"></div>

  <audio id="music" src="music/bed75.wav" data-start="0" data-duration="{DUR}" data-volume="0.55"></audio>
  <audio id="nat" src="media/base75-nat.wav" data-start="0" data-duration="{DUR}" data-volume="0.28"></audio>
{aud_html}
</div>
<script>
  const tl = gsap.timeline({{ paused: true }});
  const B = {B}, G0 = {G0};
  // progress bar
  tl.fromTo("#bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {DUR}, ease: "none" }}, 0);
  // HOOK
  [["#hk1", 0.12], ["#hk2", 0.45], ["#hk3", 1.15], ["#hk4", 1.55]].forEach(([s, t]) =>
    tl.fromTo(s, {{ opacity: 0, scale: 1.6, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.28, ease: "expo.out" }}, t));
  tl.to("#hk4", {{ scale: 1.06, duration: 1.1, ease: "sine.inOut" }}, 1.85);
  tl.to([".hk"], {{ opacity: 0, y: -40, duration: 0.18, ease: "power2.in" }}, 2.75);
  // white flash on the drops
  [7.98, 37.70, 59.98, 67.43].forEach(t => tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.35, ease: "power2.out", immediateRender: false }}, t));
  tl.set("#flash", {{ opacity: 0 }}, 0);
  // captions: pop in, hold, quick out
  document.querySelectorAll(".cap").forEach(el => {{
    const s = +el.dataset.start, d = +el.dataset.duration;
    tl.fromTo(el, {{ opacity: 0, scale: 0.7, y: 18 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.16, ease: "back.out(2.2)" }}, s);
    tl.to(el, {{ opacity: 0, duration: 0.06 }}, s + d - 0.06);
  }});
  // module labels: slide in from left
  document.querySelectorAll(".lab").forEach(el => {{
    const s = +el.dataset.start;
    tl.fromTo(el.querySelector("i"), {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.18, ease: "power3.out" }}, s);
    tl.fromTo(el, {{ opacity: 0, x: -80 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "expo.out" }}, s);
    tl.to(el, {{ opacity: 0, x: 60, duration: 0.15, ease: "power2.in" }}, s + 1.65);
  }});
  // name tag + keynote line + one room
  tl.fromTo("#tag", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 15.55);
  tl.to("#tag", {{ opacity: 0, duration: 0.15 }}, 17.15);
  tl.fromTo("#kn", {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 20.55);
  tl.to("#kn", {{ opacity: 0, duration: 0.15 }}, 22.6);
  tl.fromTo("#one", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, 26.45);
  tl.to("#one", {{ opacity: 0, duration: 0.15 }}, 30.1);
  // AWARDS
  tl.fromTo("#awBg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 37.72);
  tl.fromTo("#awK", {{ opacity: 0, y: -40 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 37.8);
  [["#cG", 38.2, 0], ["#cS", 38.9, -6], ["#cB", 39.6, 6]].forEach(([s, t, r]) => {{
    tl.fromTo(s, {{ opacity: 0, scale: 1.7, rotation: r * 3, y: 120 }}, {{ opacity: 1, scale: 1, rotation: r, y: 0, duration: 0.42, ease: "back.out(1.6)" }}, t);
  }});
  tl.to(["#cG", "#cS", "#cB"], {{ y: -14, duration: 1.2, ease: "sine.inOut" }}, 40.1);
  tl.to(["#awBg", "#awK", "#cG", "#cS", "#cB"], {{ opacity: 0, duration: 0.15 }}, 41.3);
  tl.fromTo("#soba", {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 41.6);
  tl.to("#soba", {{ opacity: 0, duration: 0.15 }}, 44.95);
  // STATS
  tl.fromTo("#stBg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 49.2);
  tl.fromTo("#st", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 49.25);
  const cnt = {{ v: 0 }};
  tl.fromTo(cnt, {{ v: 0 }}, {{ v: 7, duration: 1.2, ease: "power2.out", onUpdate: () => {{ document.getElementById("stN").textContent = Math.round(cnt.v); }} }}, 49.3);
  tl.set("#stN", {{ textContent: "7" }}, 50.55);
  [50.55, 50.9, 51.25].forEach((t, i) => tl.fromTo(`#stY div:nth-child(${{i + 1}})`, {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "back.out(2)" }}, t));
  tl.to(["#stBg", "#st"], {{ opacity: 0, duration: 0.15 }}, 52.42);
  tl.fromTo("#trust", {{ opacity: 0, y: 50 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 56.05);
  tl.to("#trust", {{ opacity: 0, duration: 0.15 }}, 59.75);
  // CTA
  tl.fromTo("#ct1", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 60.05);
  tl.to("#ct1", {{ opacity: 0, duration: 0.15 }}, 63.45);
  tl.fromTo("#ct2", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 63.8);
  tl.to("#ct2", {{ opacity: 0, duration: 0.15 }}, 67.25);
  // END CARD
  tl.fromTo("#endBg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 67.45);
  tl.fromTo("#logo", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "expo.out" }}, 67.6);
  tl.fromTo("#endT", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }}, 68.3);
  tl.fromTo("#cta", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }}, 69.0);
  tl.to("#cta", {{ scale: 1.04, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 5 }}, 69.5);
  tl.fromTo("#credit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 69.4);
  window.__timelines = window.__timelines || {{}};
  window.__timelines["tt-reel"] = tl;
  tl.seek(0);
</script>
</body>
</html>
'''
open("index.html", "w").write(html)
print("index.html written")
