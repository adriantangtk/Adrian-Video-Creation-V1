"""2.5 min landscape spec. Section starts from marks150.json. All claims from brand.md / thrivingtalents.com."""
import json, os
M = json.load(open("marks150.json"))
DUR = 150.0
BASE, NAT, MUSIC = "media/base150.mp4", "media/base150-nat.wav", "music/bed150.wav"
MUSIC_VOL, NAT_VOL = 0.55, 0.28
END_AT = M["end"]
B, G0 = 0.4644, 0.109
def r(x): return round(x, 3)

# ---- voice: (file, start, dur)
VOICE = [("v1-energy", 3.0, 4.1), ("v2-feedback", 15.6, 3.95), ("v3-noise", 30.9, 4.2),
         ("v4-excellent", 67.75, 5.75), ("v7-fail", 75.28, 5.34), ("v5-everything", 97.42, 3.3),
         ("v8-mindset", 108.1, 2.0), ("v6-applause", 119.41, 3.15)]
def sh(lst, d): return [(r(a + d), r(b + d), t, g) for a, b, t, g in lst]
CAPS = [(3.09, 4.50, "HIGHEST ENERGY", False), (4.50, 5.85, "WINS.", True),
        (5.88, 6.98, "HIGHEST ENERGY", False), (6.98, 7.95, "WINS.", True),
        (15.70, 16.45, "IN LIFE,", False), (16.45, 17.20, "THERE IS NO", False), (17.20, 18.10, "FAILURE.", True),
        (18.10, 18.72, "THERE IS ONLY", False), (18.72, 20.40, "FEEDBACK.", True),
        (30.92, 32.10, "TEAM ONE,", False), (32.10, 34.40, "MAKE SOME NOISE!", True)]
CAPS += sh([(30.62, 31.95, "YOU CAN ALL BE", False), (31.95, 33.36, "EXCELLENT.", True), (33.36, 34.20, "JUST MAKE THE", False),
            (34.20, 35.40, "DECISION", True), (35.40, 35.80, "TO BE", False), (35.80, 37.40, "EXCELLENT.", True)], 37.15)
CAPS += [(75.35, 76.28, "WHEN I FAIL,", False), (76.28, 77.30, "I LEARN.", True), (77.30, 78.30, "IT'S NOT THE END.", False),
         (78.30, 79.20, "MY EFFORT & ATTITUDE", False), (79.20, 79.70, "DETERMINE", False), (79.70, 81.60, "EVERYTHING.", True)]
CAPS += sh([(45.63, 46.95, "HOW WE DO ANYTHING", False), (46.95, 47.74, "IS HOW WE DO", False), (47.74, 49.20, "EVERYTHING.", True)], 52.02)
CAPS += [(108.40, 109.28, "CHANGE YOUR MINDSET,", False), (109.28, 110.90, "CHANGE YOUR ACTIONS.", True)]
CAPS += sh([(52.56, 53.90, "GIVE YOURSELF A HUGE", False), (53.90, 55.90, "ROUND OF APPLAUSE!", True)], 66.874)

p = M["pillars"]
LABELS = [(M["drop"], "TEAM BUILDING", ""), (r(M["drop"] + 4 * B), "LEADERSHIP WORKSHOPS", ""),
          (r(M["drop"] + 8 * B), "ENERGISERS", ""), (r(M["drop"] + 12 * B), "ADVENTURE & RETREATS", ""),
          (p, "LEADERSHIP DEVELOPMENT", "Clarity, confidence and practical tools"),
          (r(p + 4 * B), "CORPORATE TRAINING", "Aligning people, processes and culture"),
          (r(p + 8 * B), "TEAM BUILDING", "Teams that perform together"),
          (r(p + 12 * B), "SALES & BUSINESS DEVELOPMENT", "Stronger pipelines, consistent growth")]

ITEMS = []
def it(t, d, html, style="", **k): ITEMS.append(dict(t=r(t), d=r(d), html=html, style=style, **k))
# hook
for i, (txt, top, fs, t, gold) in enumerate([("WHAT IF", 250, 92, 0.12, 0), ("MONDAY", 345, 210, 0.45, 0),
                                              ("FELT LIKE", 575, 92, 1.15, 0), ("THIS?", 670, 220, 1.55, 1)]):
    it(t, 2.9 - t, f'<span class="{"g" if gold else ""}">{txt}</span>', f"top:{top}px;font-size:{fs}px", id=f"hk{i}", drift=False)
# michael
it(M["michael"] + 0.08, 1.75, "<b>Michael Teoh</b><small>Founder &amp; CEO, Thriving Talents</small>", cls="lt", anim="up", id="tagMT", drift=False)
it(20.55, 2.25, 'KEYNOTES THAT<br><span class="g">MOVE ROOMS.</span>', "top:300px;font-size:120px")
# stats
s0 = M["stats"]
it(s0, 7.35, "", cls="dim", anim="fade", drift=False, id="stDim")
it(s0 + 0.1, 7.2, '<span class="kick">SINCE 2012</span>HELPING PEOPLE GROW.<br><span class="g">HELPING ORGANIZATIONS THRIVE.</span>',
   "top:150px;font-size:70px", anim="up", drift=False, id="stHead")
it(s0 + 1.2, 6.1, '<div class="stats"><div class="stat"><b>0K+</b><small>Training sessions</small></div><div class="stat"><b>0+</b><small>Expert coaches</small></div>'
   '<div class="stat"><b>0+</b><small>Countries reached</small></div><div class="stat"><b>RM0M+</b><small>Value delivered</small></div></div>',
   "top:520px;opacity:1;text-shadow:none;background:none", anim="fade", drift=False, id="stRow",
   stagger=[(".stat:nth-child(1)", r(s0 + 1.2)), (".stat:nth-child(2)", r(s0 + 1.65)), (".stat:nth-child(3)", r(s0 + 2.1)), (".stat:nth-child(4)", r(s0 + 2.55))],
   counters=[(".stat:nth-child(1) b", 0, 5, r(s0 + 1.2), 1.0, "", "K+"), (".stat:nth-child(2) b", 0, 60, r(s0 + 1.65), 1.0, "", "+"),
             (".stat:nth-child(3) b", 0, 43, r(s0 + 2.1), 1.0, "", "+"), (".stat:nth-child(4) b", 0, 10, r(s0 + 2.55), 1.0, "RM", "M+")])
# noise
it(34.6, 3.0, 'ONE ROOM.<br><span class="g">ONE ENERGY.</span>', "top:330px;font-size:130px", anim="up")
# coaches title
c0 = M["coaches"]
it(c0 + 0.1, 1.8, '<span class="kick">60+ EXPERT COACHES</span>MEET THE PEOPLE<br><span class="g">BEHIND THE ENERGY.</span>', "top:300px;font-size:110px", anim="tilt")
TRAINER_TAGS = json.load(open("trainer_tags.json")) if os.path.exists("trainer_tags.json") else []
for k, (t, name, role) in enumerate(TRAINER_TAGS):
    it(t, 1.8, f"<b>{name}</b><small>{role}</small>", cls="lt", anim="up", id=f"trT{k}", drift=False)
# experiential
e0 = M["exp"]
it(e0 + 0.15, 3.5, '<span class="kick">WHY CLIENTS CHOOSE US</span>EXPERIENTIAL LEARNING<br><span class="g">THAT STICKS.</span>', "top:300px;font-size:116px", anim="tilt")
it(e0 + 3.9, 3.4, 'SIMULATIONS · CHALLENGES<br><span class="g">REAL-WORLD SCENARIOS</span>', "top:360px;font-size:84px", anim="up")
# awards 2026
a0 = M["awards"]
it(a0, 3.72, "", cls="navy", anim="fade", drift=False, id="awBg")
it(a0 + 0.1, 3.6, '<span class="kick">HR VENDORS OF THE YEAR 2026 · MALAYSIA</span>3 AWARDS. ONE NIGHT.', "top:90px;font-size:82px", anim="up", drift=False, id="awHead")
it(a0 + 0.5, 3.2, '<div class="cards"><div class="card"><img src="assets/hrv-gold.png"><div class="m">GOLD · Best Team Building</div></div>'
   '<div class="card"><img src="assets/hrv-silver.png"><div class="m">SILVER · Management Training</div></div>'
   '<div class="card"><img src="assets/hrv-bronze.png"><div class="m">BRONZE · Instructional Design</div></div></div>',
   "top:280px;opacity:1;text-shadow:none;background:none", anim="fade", drift=False, id="awCards",
   stagger=[(".card:nth-child(1)", r(a0 + 0.55)), (".card:nth-child(2)", r(a0 + 1.05)), (".card:nth-child(3)", r(a0 + 1.55))])
it(a0 + 3.85, 3.4, '<span class="kick">15TH STAR OUTSTANDING BUSINESS AWARDS</span><span style="display:inline-block;padding:12px 30px;background:var(--gold);color:var(--navy);border-radius:14px">BEST EMPLOYER</span>',
   "top:780px;font-size:76px", anim="up")
# timeline
t0 = M["timeline"]
it(t0, 7.35, "", cls="navy", anim="fade", drift=False, id="tlBg")
it(t0 + 0.1, 7.2, '<span class="kick">A DECADE OF EXCELLENCE</span>AWARD-WINNING <span class="g">SINCE 2022</span>', "top:90px;font-size:84px", anim="up", drift=False, id="tlHead")
yrs = [("2022", "assets/web/Image-5-4.jpg", "CXP Best Customer Experience<br>HR Vendors of the Year"),
       ("2024", "assets/web/Image-5-3.jpg", "Best Management Training Provider<br>Malaysia Role Model Enterprise"),
       ("2025", "assets/web/Image-5-6.jpg", "Best Sales Training (Gold)<br>Leader of the Year · SOBA Best Employer"),
       ("2026", "assets/hrv-gold.png", "Gold · Best Team Building<br>+ Silver &amp; Bronze")]
it(t0 + 0.6, 6.7, '<div class="tline">' + "".join(f'<div class="yr"><div class="ph"><img src="{im}"></div><b>{y}</b><small>{tx}</small></div>' for y, im, tx in yrs) + "</div>",
   "top:260px;opacity:1;text-shadow:none;text-align:left;background:none", anim="fade", drift=False, id="tlRow",
   stagger=[(f".yr:nth-child({i+1})", r(t0 + 0.6 + 0.55 * i)) for i in range(4)])
# proof
it(99.4, 5.0, 'TRUSTED BY FORTUNE 500 BRANDS<br>&amp; LEADING ORGANISATIONS<br><span class="g">ACROSS 43+ COUNTRIES</span>', "top:250px;font-size:88px", anim="tilt")
# energy / units
it(M["energy"] + 0.05, 3.3, 'HIGHEST ENERGY<br><span class="g">WINS.</span>', "top:280px;font-size:150px")
u0 = M["units"]
it(u0 + 0.15, 3.4, 'TURN TEAMS INTO<br><span class="g">HIGH-PERFORMING UNITS.</span>', "top:320px;font-size:110px", anim="tilt")
it(u0 + 3.85, 3.4, "THEY DON'T JUST WORK TOGETHER.<br><span class=\"g\">THEY PERFORM TOGETHER.</span>", "top:340px;font-size:88px", anim="up")
# grow
it(M["grow"] + 0.2, 7.0, 'WHEN PEOPLE GROW,<br><span class="g">ORGANIZATIONS MOVE FORWARD.</span>', "top:330px;font-size:100px", anim="tilt")
# cta
it(M["cta"] + 0.1, 3.5, 'YOUR TEAM<br><span class="g">IS NEXT.</span>', "top:290px;font-size:170px")
it(M["cta"] + 3.8, 3.5, "LET'S MAKE MONDAY<br><span class=\"g\">FEEL LIKE THIS.</span>", "top:320px;font-size:130px", anim="up")
# end card
it(END_AT, DUR - END_AT, "", cls="navy", anim="fade", drift=False, hold=True, id="endBg")
it(END_AT + 0.8, DUR - END_AT - 0.8, '<span style="font-size:40px;font-weight:600;color:#D9DEEA">Award-winning corporate training · Since 2012</span><br>'
   '<span style="font-size:34px;font-weight:500;color:#D9DEEA">Leadership · Team Building · Corporate Training · Sales</span>',
   "top:500px;line-height:1.5;letter-spacing:0", anim="up", drift=False, hold=True, id="endT")
it(END_AT + 1.4, DUR - END_AT - 1.4, '<span style="display:inline-block;padding:22px 56px;background:var(--gold);color:var(--navy);border-radius:999px">thrivingtalents.com</span>'
   '<br><span style="display:inline-block;margin-top:26px;font-size:44px;color:#fff">WhatsApp +60 11-5415 7656</span>',
   "top:660px;font-size:64px;letter-spacing:-.01em", anim="pop", drift=False, hold=True, id="endCta")
it(END_AT + 2.0, DUR - END_AT - 2.0, 'Music: “Inspiring Progress” by Soundrider/Dope · CC BY 3.0 · jamendo.com',
   "top:1000px;font-size:22px;font-weight:500;color:rgba(217,222,234,.7);letter-spacing:0;text-shadow:none", anim="fade", drift=False, hold=True, id="credit")

FLASH = [M["drop"] - 0.02, M["awards"] - 0.02, M["cta"] - 0.02, M["energy"] - 0.02]
LEAKS = [M["michael"], M["noise"], M["pillars"], M["timeline"], M["units"], M["grow"]]
LETTERBOX = [(M["emo1"], M["awards"] - 0.05)]
def beats(a, b, step=2): return [r(G0 + k * B) for k in range(0, 400, step) if a <= G0 + k * B < b - 0.05]
PULSE = beats(M["drop"], M["michael"]) + beats(M["noise"], M["coaches"]) + beats(M["energy"], M["finale"])

SFX = [("sx-impact-bass-2", 0.0, 0.5, 2.0), ("sx-glitch-3", 0.02, 0.25, 0.9), ("sx-pop", 1.2, 0.5, 0.4), ("sx-pop-3", 1.6, 0.6, 0.4),
       ("sx-whoosh-cinematic", 2.8, 0.5, 1.2), ("sx-riser", 5.9, 0.45, 2.1), ("sx-impact-bass-1", M["drop"] - 0.05, 0.5, 1.6)]
SFX += [(f, r(t + 0.05), 0.42, 0.4) for (t, _, _), f in zip(LABELS, ["sx-pop", "sx-pop-2", "sx-pop-3", "sx-pop-4"] * 2)]
SFX += [("sx-whoosh-soft", r(t - 0.15), 0.45, 0.8) for t in LEAKS]
SFX += [("sx-click-hi", r(s0 + 1.2 + 0.45 * i), 0.35, 0.3) for i in range(4)]
SFX += [("sx-whoosh-cinematic", c0 - 0.1, 0.45, 1.2), ("sx-whoosh-cinematic", e0 - 0.1, 0.45, 1.2),
        ("sx-riser", r(a0 - 2.1), 0.42, 2.1), ("sx-impact-bass-2", r(a0 - 0.36), 0.5, 1.8),
        ("sx-pop-2", r(a0 + 0.55), 0.55, 0.4), ("sx-pop-3", r(a0 + 1.05), 0.55, 0.4), ("sx-pop-4", r(a0 + 1.55), 0.55, 0.4), ("sx-sparkle", r(a0 + 1.9), 0.45, 1.4),
        ("sx-sparkle", r(a0 + 3.9), 0.35, 1.4)]
SFX += [("sx-click", r(t0 + 0.6 + 0.55 * i), 0.35, 0.25) for i in range(4)]
SFX += [("sx-impact-bass-1", r(M["energy"] - 0.05), 0.45, 1.4), ("sx-riser", r(M["cta"] - 2.1), 0.42, 2.1),
        ("sx-impact-bass-2", r(M["cta"] - 0.36), 0.5, 1.8), ("sx-impact-bass-2", r(END_AT - 0.36), 0.5, 2.0),
        ("sx-sparkle", r(END_AT + 0.6), 0.45, 1.4), ("sx-chime", r(END_AT + 1.4), 0.3, 1.5)]
