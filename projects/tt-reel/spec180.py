"""3-minute landscape spec on "Ambient Uplift". Section starts from marks180.json, beats from music/ambient-beats.json."""
import json, os
import numpy as np
M = json.load(open("marks180.json"))
BEATS = np.array(json.load(open("music/ambient-beats.json")))
EDL = json.load(open("edl180.json"))["shots"]
DUR = 182.0
BASE, NAT, MUSIC = "media/base180.mp4", "media/base180-nat.wav", "music/bed180.wav"
MUSIC_VOL, NAT_VOL = 0.55, 0.28
END_AT = M["end"]
OUT = "index.html"
def r(x): return round(float(x), 3)
def bt(t, n=0):  # beat time n beats after the beat nearest t
    i = int(np.argmin(np.abs(BEATS - t))); return r(BEATS[min(i + n, len(BEATS) - 1)])
def shot_start(file_part, tin):
    t = 0.0
    for s in EDL:
        if file_part in s["file"] and s.get("in") == tin: return t
        t += s["dur"]
    raise KeyError(file_part)

# ---- soundbites: name -> (start, dur, captions relative to start)
REL = {
 "v1-energy": (4.1, [(.09, 1.5, "HIGHEST ENERGY", 0), (1.5, 2.85, "WINS.", 1), (2.88, 3.98, "HIGHEST ENERGY", 0), (3.98, 4.95, "WINS.", 1)]),
 "v2-feedback": (3.95, [(.1, .85, "IN LIFE,", 0), (.85, 1.6, "THERE IS NO", 0), (1.6, 2.5, "FAILURE.", 1), (2.5, 3.12, "THERE IS ONLY", 0), (3.12, 4.8, "FEEDBACK.", 1)]),
 "v3-noise": (4.2, [(.02, 1.2, "TEAM ONE,", 0), (1.2, 3.5, "MAKE SOME NOISE!", 1)]),
 "v4-excellent": (5.75, [(.02, 1.35, "YOU CAN ALL BE", 0), (1.35, 2.76, "EXCELLENT.", 1), (2.76, 3.6, "JUST MAKE THE", 0), (3.6, 4.8, "DECISION", 1), (4.8, 5.2, "TO BE", 0), (5.2, 6.8, "EXCELLENT.", 1)]),
 "v7-fail": (5.34, [(.07, 1.0, "WHEN I FAIL,", 0), (1.0, 2.02, "I LEARN.", 1), (2.02, 3.02, "IT'S NOT THE END.", 0), (3.02, 3.92, "MY EFFORT & ATTITUDE", 0), (3.92, 4.42, "DETERMINE", 0), (4.42, 6.3, "EVERYTHING.", 1)]),
 "v5-everything": (3.3, [(.23, 1.55, "HOW WE DO ANYTHING", 0), (1.55, 2.34, "IS HOW WE DO", 0), (2.34, 3.8, "EVERYTHING.", 1)]),
 "v8-mindset": (2.0, [(.3, 1.18, "CHANGE YOUR MINDSET,", 0), (1.18, 2.8, "CHANGE YOUR ACTIONS.", 1)]),
 "v6-applause": (3.15, [(.024, 1.364, "GIVE YOURSELF A HUGE", 0), (1.364, 3.364, "ROUND OF APPLAUSE!", 1)]),
}
mt_applause = shot_start("mt-vid20250513", 33.0) - 0.05
STARTS = {"v1-energy": 3.3, "v2-feedback": M["build"] + 0.65, "v3-noise": 43.6, "v4-excellent": M["breakdown"] + 0.5,
          "v7-fail": M["breakdown"] + 7.9, "v5-everything": M["proof"] + 0.3, "v8-mindset": M["finale"] + 0.25, "v6-applause": mt_applause}
VOICE, CAPS = [], []
for n, st in STARTS.items():
    d, caps = REL[n]; VOICE.append((n, r(st), d))
    CAPS += [(r(st + a), r(st + b), t, bool(g)) for a, b, t, g in caps]

d0, p0 = M["drop"], M["pillars"]
LABELS = [(bt(d0), "TEAM BUILDING", ""), (bt(d0, 4), "ENERGISERS", ""), (bt(d0, 8), "LEADERSHIP WORKSHOPS", ""),
          (bt(d0, 12), "ADVENTURE & OUTDOOR", ""), (bt(d0, 16), "LIVE EVENTS", ""), (bt(d0, 20), "AMAZING RACES", "")]
pl = [("LEADERSHIP DEVELOPMENT", "Clarity, confidence and practical tools"), ("CORPORATE TRAINING", "Aligning people, processes and culture"),
      ("TEAM BUILDING", "Teams that perform together"), ("SALES & BUSINESS DEVELOPMENT", "Stronger pipelines, consistent growth")]
for i, (a, b) in enumerate(pl):
    t = bt(p0, 8 * i); LABELS.append((t, a, b, r(bt(p0, 8 * (i + 1)) - t - 0.05)))

ITEMS = []
def it(t, d, html, style="", **k): ITEMS.append(dict(t=r(t), d=r(d), html=html, style=style, **k))
# hook
for i, (txt, top, fs, t, gold) in enumerate([("WHAT IF", 250, 92, 0.12, 0), ("MONDAY", 345, 210, 0.45, 0), ("FELT LIKE", 575, 92, 1.15, 0), ("THIS?", 670, 220, 1.55, 1)]):
    it(t, 2.95 - t, f'<span class="{"g" if gold else ""}">{txt}</span>', f"top:{top}px;font-size:{fs}px;background:none", id=f"hk{i}", drift=False)
# build: Michael + stats
b0 = M["build"]
it(b0 + 0.08, 1.75, "<b>Michael Teoh</b><small>Founder &amp; CEO, Thriving Talents</small>", cls="lt", anim="up", id="tagMT", drift=False)
s0 = bt(b0 + 7.6)
it(s0, M["drop"] - s0 - 0.05, "", cls="dim", anim="fade", drift=False, id="stDim")
it(s0 + 0.1, M["drop"] - s0 - 0.2, '<span class="kick">SINCE 2012</span>HELPING PEOPLE GROW.<br><span class="g">HELPING ORGANIZATIONS THRIVE.</span>',
   "top:150px;font-size:70px;background:none", anim="up", drift=False, id="stHead")
it(s0 + 1.0, M["drop"] - s0 - 1.1, '<div class="stats"><div class="stat"><b>0K+</b><small>Training sessions</small></div><div class="stat"><b>0+</b><small>Expert coaches</small></div>'
   '<div class="stat"><b>0+</b><small>Countries reached</small></div><div class="stat"><b>RM0M+</b><small>Value delivered</small></div></div>',
   "top:520px;opacity:1;text-shadow:none;background:none", anim="fade", drift=False, id="stRow",
   stagger=[(f".stat:nth-child({i+1})", r(s0 + 1.0 + 0.6 * i)) for i in range(4)],
   counters=[(".stat:nth-child(1) b", 0, 5, r(s0 + 1.0), 1.2, "", "K+"), (".stat:nth-child(2) b", 0, 60, r(s0 + 1.6), 1.2, "", "+"),
             (".stat:nth-child(3) b", 0, 43, r(s0 + 2.2), 1.2, "", "+"), (".stat:nth-child(4) b", 0, 10, r(s0 + 2.8), 1.2, "RM", "M+")])
# trusted: logo wall
tw = M["trusted"]
LOGOS = ["AmBank.png", "uob.webp", "Hong_Leong_Bank.svg-scaled.png", "Prudential-Logo.jpg", "SL_CLR_RGB-3.png", "Etiqa_Insurance_and_Takaful.png",
         "unnamed-qzxjp51arqrs93tp06k5h0ab3g6ad0cewfeimjd3wg.png", "images-4.png", "Novartis-Logo.svg.png", "Abbott-Logo-500x281-1.webp",
         "107300973-1694714293835-Untitled-3-scaled.jpg", "images-12.jpg", "Schlumberger.svg-scaled.png", "FrieslandCampina_Logo_2020.svg-scaled.png",
         "22bbd905004dd3a3c3edbcfeea3972ba.png", "KLK-OLEO-Header-Logo-1.png", "KPJ-Logo-1024x213-1.png", "CelcomDigi-Logo.webp",
         "Principal_AM_full_rgb_sm.png", "af09cf72aa26ff6edf5448756f4554dc.webp", "images-1.png", "images-2.png", "images-3.png",
         "images-5.png", "images-6.png", "975930ca-7c97-11ef-b217-c62686c7f5fd.png", "WhatsApp-Image-2026-04-27-at-3.12.56-PM.jpeg",
         "CHINHIN.webp", "46b240181043e1393532f7f93c420c2066aae9e55e5e5.jpg", "223780_12d2616ef2d2431b936fb504f0fc7bc4mv2.png", "images-11.jpg", "converted_image.png"]
LOGOS = [l for l in LOGOS if os.path.exists("assets/logos/" + l)][:32]
wall_end = r(43.45)
it(tw, wall_end - tw, "", cls="navy", anim="fade", drift=False, id="wallBg")
it(tw + 0.1, wall_end - tw - 0.1, '<span class="kick">ORGANIZATIONS THAT TAKE GROWTH SERIOUSLY</span>TRUSTED BY <span class="g">LEADING BRANDS</span>',
   "top:70px;font-size:74px;background:none", anim="up", drift=False, id="wallHead")
it(tw + 0.4, wall_end - tw - 0.4, '<div class="wall">' + "".join(f'<div><img src="assets/logos/{l}"></div>' for l in LOGOS) + "</div>",
   "top:300px;opacity:1;text-shadow:none;background:none;left:80px;width:1760px", anim="fade", drift=False, id="wall",
   stagger=[(f"div:nth-child({i+1})", r(tw + 0.45 + 0.055 * i)) for i in range(len(LOGOS))])
# coaches
c0 = M["coaches"]
it(c0 + 0.1, 1.8, '<span class="kick">60+ EXPERT COACHES</span>MEET THE PEOPLE<br><span class="g">BEHIND THE ENERGY.</span>', "top:300px;font-size:110px", anim="tilt")
for k, (t, name, role) in enumerate(json.load(open("trainer_tags180.json")) if os.path.exists("trainer_tags180.json") else []):
    it(t, 1.75, f"<b>{name}</b><small>{role}</small>", cls="lt", anim="up", id=f"trT{k}", drift=False)
# experiential
e0 = M["exp"]
it(e0 + 0.1, 3.6, '<span class="kick">WHY CLIENTS CHOOSE US</span>EXPERIENTIAL LEARNING<br><span class="g">THAT STICKS.</span>', "top:300px;font-size:116px", anim="tilt")
it(e0 + 3.9, M["breakdown"] - e0 - 4.1, 'SIMULATIONS · CHALLENGES<br><span class="g">REAL-WORLD SCENARIOS</span>', "top:360px;font-size:84px", anim="up")
# awards
a0 = M["awards"]; sb = M["soba"]
it(a0, sb - a0 - 0.05, "", cls="navy", anim="fade", drift=False, id="awBg")
it(a0 + 0.1, sb - a0 - 0.2, '<span class="kick">HR VENDORS OF THE YEAR 2026 · MALAYSIA</span>3 AWARDS. ONE NIGHT.', "top:90px;font-size:82px;background:none", anim="up", drift=False, id="awHead")
it(a0 + 0.4, sb - a0 - 0.5, '<div class="cards"><div class="card"><img src="assets/hrv-gold.png"><div class="m">GOLD · Best Team Building</div></div>'
   '<div class="card"><img src="assets/hrv-silver.png"><div class="m">SILVER · Management Training</div></div>'
   '<div class="card"><img src="assets/hrv-bronze.png"><div class="m">BRONZE · Instructional Design</div></div></div>',
   "top:280px;opacity:1;text-shadow:none;background:none", anim="fade", drift=False, id="awCards",
   stagger=[(".card:nth-child(1)", bt(a0, 2)), (".card:nth-child(2)", bt(a0, 4)), (".card:nth-child(3)", bt(a0, 6))])
it(sb + 0.3, M["timeline"] - sb - 0.5, '<span class="kick">15TH STAR OUTSTANDING BUSINESS AWARDS</span><span style="display:inline-block;padding:12px 30px;background:var(--gold);color:var(--navy);border-radius:14px">BEST EMPLOYER</span>',
   "top:780px;font-size:76px;background:none", anim="up")
# timeline
t0 = M["timeline"]
it(t0, M["proof"] - t0 - 0.05, "", cls="navy", anim="fade", drift=False, id="tlBg")
it(t0 + 0.1, M["proof"] - t0 - 0.2, '<span class="kick">A DECADE OF EXCELLENCE</span>AWARD-WINNING <span class="g">SINCE 2022</span>', "top:90px;font-size:84px;background:none", anim="up", drift=False, id="tlHead")
yrs = [("2022", "assets/web/Image-5-4.jpg", "CXP Best Customer Experience<br>HR Vendors of the Year"),
       ("2024", "assets/web/Image-5-3.jpg", "Best Management Training Provider<br>Malaysia Role Model Enterprise"),
       ("2025", "assets/web/Image-5-6.jpg", "Best Sales Training (Gold)<br>Leader of the Year · SOBA Best Employer"),
       ("2026", "assets/hrv-gold.png", "Gold · Best Team Building<br>+ Silver &amp; Bronze")]
it(t0 + 0.5, M["proof"] - t0 - 0.6, '<div class="tline">' + "".join(f'<div class="yr"><div class="ph"><img src="{im}"></div><b>{y}</b><small>{tx}</small></div>' for y, im, tx in yrs) + "</div>",
   "top:260px;opacity:1;text-shadow:none;text-align:left;background:none", anim="fade", drift=False, id="tlRow",
   stagger=[(f".yr:nth-child({i+1})", bt(t0, 2 + 3 * i)) for i in range(4)])
# proof
p1 = M["proof"]
it(bt(p1, 9), 3.6, 'TURN TEAMS INTO<br><span class="g">HIGH-PERFORMING UNITS.</span>', "top:320px;font-size:110px", anim="tilt")
it(bt(p1, 17), 3.6, "THEY DON'T JUST WORK TOGETHER.<br><span class=\"g\">THEY PERFORM TOGETHER.</span>", "top:340px;font-size:88px", anim="up")
it(bt(p1, 25), M["finale"] - bt(p1, 25) - 0.1, 'TRUSTED ACROSS<br><span class="g">43+ COUNTRIES</span>', "top:320px;font-size:120px", anim="pop")
# finale
it(M["finale"] + 0.02, 1.8, 'HIGHEST ENERGY<br><span class="g">WINS.</span>', "top:280px;font-size:150px")
# grow + cta
g0 = M["grow"]
it(g0 + 0.2, 6.9, 'WHEN PEOPLE GROW,<br><span class="g">ORGANIZATIONS MOVE FORWARD.</span>', "top:330px;font-size:100px", anim="tilt")
it(bt(g0, 16), 3.5, 'YOUR TEAM<br><span class="g">IS NEXT.</span>', "top:290px;font-size:170px")
it(bt(g0, 24), END_AT - bt(g0, 24) - 0.1, "LET'S MAKE MONDAY<br><span class=\"g\">FEEL LIKE THIS.</span>", "top:320px;font-size:130px", anim="up")
# end card
it(END_AT, DUR - END_AT, "", cls="navy", anim="fade", drift=False, hold=True, id="endBg")
it(END_AT + 0.8, DUR - END_AT - 0.8, '<span style="font-size:40px;font-weight:600;color:#D9DEEA">Award-winning corporate training · Since 2012</span><br>'
   '<span style="font-size:34px;font-weight:500;color:#D9DEEA">Leadership · Team Building · Corporate Training · Sales</span>',
   "top:500px;line-height:1.5;letter-spacing:0;background:none", anim="up", drift=False, hold=True, id="endT")
it(END_AT + 1.4, DUR - END_AT - 1.4, '<span style="display:inline-block;padding:22px 56px;background:var(--gold);color:var(--navy);border-radius:999px">thrivingtalents.com</span>'
   '<br><span style="display:inline-block;margin-top:26px;font-size:44px;color:#fff">WhatsApp +60 11-5415 7656</span>',
   "top:660px;font-size:64px;letter-spacing:-.01em;background:none", anim="pop", drift=False, hold=True, id="endCta")
it(END_AT + 2.0, DUR - END_AT - 2.0, 'Music: “Ambient Uplift” by Soundrider/Dope · CC BY 3.0 · jamendo.com',
   "top:1000px;font-size:22px;font-weight:500;color:rgba(217,222,234,.7);letter-spacing:0;text-shadow:none;background:none", anim="fade", drift=False, hold=True, id="credit")

FLASH = [r(M["drop"] - .02), r(M["awards"] - .02), r(M["finale"] - .02), r(END_AT - .02)]
LEAKS = [M["build"], M["trusted"], M["coaches"], M["pillars"], M["timeline"], M["grow"]]
LETTERBOX = [(M["breakdown"], M["awards"] - 0.05)]
def beats(a, b, step=2): return [r(x) for x in BEATS[::step] if a <= x < b - 0.05]
PULSE = beats(M["drop"], M["trusted"]) + beats(46.0, M["coaches"]) + beats(M["finale"], mt_applause - 0.2)

SFX = [("sx-impact-bass-2", 0.0, 0.5, 2.0), ("sx-glitch-3", 0.02, 0.25, 0.9), ("sx-pop", 1.2, 0.5, 0.4), ("sx-pop-3", 1.6, 0.6, 0.4),
       ("sx-whoosh-cinematic", 2.8, 0.5, 1.2), ("sx-riser", r(M["drop"] - 2.1), 0.45, 2.1), ("sx-impact-bass-1", r(M["drop"] - .05), 0.5, 1.6)]
SFX += [(f, r(lab[0] + .05), 0.4, 0.4) for lab, f in zip(LABELS, ["sx-pop", "sx-pop-2", "sx-pop-3", "sx-pop-4"] * 3)]
SFX += [("sx-whoosh-soft", r(t - .15), 0.45, 0.8) for t in LEAKS]
SFX += [("sx-click-hi", r(s0 + 1.0 + 0.6 * i), 0.35, 0.3) for i in range(4)]
SFX += [("sx-click-soft", r(tw + 0.45 + 0.22 * i), 0.18, 0.15) for i in range(0, 32, 4)]
SFX += [("sx-whoosh-cinematic", r(c0 - .1), 0.45, 1.2), ("sx-whoosh-cinematic", r(e0 - .1), 0.45, 1.2),
        ("sx-riser", r(a0 - 2.1), 0.42, 2.1), ("sx-impact-bass-2", r(a0 - 0.36), 0.5, 1.8),
        ("sx-pop-2", bt(a0, 2), 0.55, 0.4), ("sx-pop-3", bt(a0, 4), 0.55, 0.4), ("sx-pop-4", bt(a0, 6), 0.55, 0.4), ("sx-sparkle", r(bt(a0, 6) + .3), 0.45, 1.4),
        ("sx-sparkle", r(sb + .3), 0.35, 1.4)]
SFX += [("sx-click", bt(t0, 2 + 3 * i), 0.35, 0.25) for i in range(4)]
SFX += [("sx-impact-bass-1", r(M["finale"] - .05), 0.45, 1.4), ("sx-riser", r(bt(g0, 16) - 2.1), 0.4, 2.1),
        ("sx-impact-bass-2", r(bt(g0, 16) - 0.36), 0.5, 1.8), ("sx-impact-bass-2", r(END_AT - 0.36), 0.5, 2.0),
        ("sx-sparkle", r(END_AT + 0.6), 0.45, 1.4), ("sx-chime", r(END_AT + 1.4), 0.3, 1.5)]
