"""75 s landscape spec (same cut as the vertical v1, re-laid out for 1920x1080, with website-verified claims)."""
DUR = 75.0
BASE, NAT, MUSIC = "media/base75l.mp4", "media/base75l-nat.wav", "music/bed75.wav"
MUSIC_VOL, NAT_VOL = 0.55, 0.28
END_AT = 67.45
B, G0 = 0.4644, 0.109
def r(x): return round(x, 3)
VOICE = [("v1-energy", 3.00, 4.10), ("v2-feedback", 15.60, 3.95), ("v3-noise", 22.90, 4.20),
         ("v4-excellent", 30.60, 5.75), ("v5-everything", 45.40, 3.30), ("v6-applause", 52.536, 3.15)]
CAPS = [(3.09, 4.50, "HIGHEST ENERGY", False), (4.50, 5.85, "WINS.", True), (5.88, 6.98, "HIGHEST ENERGY", False), (6.98, 7.95, "WINS.", True),
        (15.70, 16.45, "IN LIFE,", False), (16.45, 17.20, "THERE IS NO", False), (17.20, 18.10, "FAILURE.", True),
        (18.10, 18.72, "THERE IS ONLY", False), (18.72, 20.40, "FEEDBACK.", True),
        (22.92, 24.10, "TEAM ONE,", False), (24.10, 26.40, "MAKE SOME NOISE!", True),
        (30.62, 31.95, "YOU CAN ALL BE", False), (31.95, 33.36, "EXCELLENT.", True), (33.36, 34.20, "JUST MAKE THE", False),
        (34.20, 35.40, "DECISION", True), (35.40, 35.80, "TO BE", False), (35.80, 37.40, "EXCELLENT.", True),
        (45.63, 46.95, "HOW WE DO ANYTHING", False), (46.95, 47.74, "IS HOW WE DO", False), (47.74, 49.20, "EVERYTHING.", True),
        (52.56, 53.90, "GIVE YOURSELF A HUGE", False), (53.90, 55.90, "ROUND OF APPLAUSE!", True)]
LABELS = [(8.00, "TEAM BUILDING", ""), (9.86, "ENERGISERS", ""), (11.72, "TEAM CULTURE", ""), (13.58, "RETREATS", "")]
ITEMS = []
def it(t, d, html, style="", **k): ITEMS.append(dict(t=r(t), d=r(d), html=html, style=style, **k))
for i, (txt, top, fs, t, gold) in enumerate([("WHAT IF", 250, 92, 0.12, 0), ("MONDAY", 345, 210, 0.45, 0),
                                              ("FELT LIKE", 575, 92, 1.15, 0), ("THIS?", 670, 220, 1.55, 1)]):
    it(t, 2.9 - t, f'<span class="{"g" if gold else ""}">{txt}</span>', f"top:{top}px;font-size:{fs}px;background:none", id=f"hk{i}", drift=False)
it(15.5, 1.75, "<b>Michael Teoh</b><small>Founder &amp; CEO, Thriving Talents</small>", cls="lt", anim="up", id="tagMT", drift=False)
it(20.55, 2.25, 'KEYNOTES THAT<br><span class="g">MOVE ROOMS.</span>', "top:300px;font-size:120px")
it(26.45, 3.75, 'ONE ROOM.<br><span class="g">ONE ENERGY.</span>', "top:310px;font-size:130px", anim="up")
a0 = 37.72
it(a0, 3.72, "", cls="navy", anim="fade", drift=False, id="awBg")
it(a0 + 0.1, 3.6, '<span class="kick">HR VENDORS OF THE YEAR 2026 · MALAYSIA</span>3 AWARDS. ONE NIGHT.', "top:90px;font-size:82px;background:none", anim="up", drift=False, id="awHead")
it(a0 + 0.4, 3.3, '<div class="cards"><div class="card"><img src="assets/hrv-gold.png"><div class="m">GOLD · Best Team Building</div></div>'
   '<div class="card"><img src="assets/hrv-silver.png"><div class="m">SILVER · Management Training</div></div>'
   '<div class="card"><img src="assets/hrv-bronze.png"><div class="m">BRONZE · Instructional Design</div></div></div>',
   "top:280px;opacity:1;text-shadow:none;background:none", anim="fade", drift=False, id="awCards",
   stagger=[(".card:nth-child(1)", r(a0 + 0.45)), (".card:nth-child(2)", r(a0 + 0.95)), (".card:nth-child(3)", r(a0 + 1.45))])
it(41.6, 3.4, '<span class="kick">15TH STAR OUTSTANDING BUSINESS AWARDS</span><span style="display:inline-block;padding:12px 30px;background:var(--gold);color:var(--navy);border-radius:14px">BEST EMPLOYER</span>',
   "top:780px;font-size:76px;background:none", anim="up")
s0 = 49.25
it(s0, 3.3, "", cls="dim", anim="fade", drift=False, id="stDim")
it(s0 + 0.05, 3.25, '<span class="kick">SINCE 2012</span>AWARD-WINNING <span class="g">CORPORATE TRAINING</span>', "top:170px;font-size:72px;background:none", anim="up", drift=False, id="stHead")
it(s0 + 0.3, 3.0, '<div class="stats"><div class="stat"><b>0K+</b><small>Training sessions</small></div><div class="stat"><b>0+</b><small>Expert coaches</small></div>'
   '<div class="stat"><b>0+</b><small>Countries reached</small></div><div class="stat"><b>RM0M+</b><small>Value delivered</small></div></div>',
   "top:480px;opacity:1;text-shadow:none;background:none", anim="fade", drift=False, id="stRow",
   stagger=[(f".stat:nth-child({i+1})", r(s0 + 0.3 + 0.3 * i)) for i in range(4)],
   counters=[(".stat:nth-child(1) b", 0, 5, r(s0 + 0.3), 0.9, "", "K+"), (".stat:nth-child(2) b", 0, 60, r(s0 + 0.6), 0.9, "", "+"),
             (".stat:nth-child(3) b", 0, 43, r(s0 + 0.9), 0.9, "", "+"), (".stat:nth-child(4) b", 0, 10, r(s0 + 1.2), 0.9, "RM", "M+")])
it(56.05, 3.85, 'TRUSTED BY FORTUNE 500 BRANDS<br><span class="g">ACROSS 43+ COUNTRIES</span>', "top:310px;font-size:96px", anim="tilt")
it(60.05, 3.45, 'YOUR TEAM<br><span class="g">IS NEXT.</span>', "top:290px;font-size:170px")
it(63.8, 3.5, "LET'S MAKE MONDAY<br><span class=\"g\">FEEL LIKE THIS.</span>", "top:320px;font-size:130px", anim="up")
it(END_AT, DUR - END_AT, "", cls="navy", anim="fade", drift=False, hold=True, id="endBg")
it(END_AT + 0.8, DUR - END_AT - 0.8, '<span style="font-size:40px;font-weight:600;color:#D9DEEA">Award-winning corporate training · Since 2012</span><br>'
   '<span style="font-size:34px;font-weight:500;color:#D9DEEA">Leadership · Team Building · Corporate Training · Sales</span>',
   "top:500px;line-height:1.5;letter-spacing:0;background:none", anim="up", drift=False, hold=True, id="endT")
it(END_AT + 1.4, DUR - END_AT - 1.4, '<span style="display:inline-block;padding:22px 56px;background:var(--gold);color:var(--navy);border-radius:999px">thrivingtalents.com</span>'
   '<br><span style="display:inline-block;margin-top:26px;font-size:44px;color:#fff">WhatsApp +60 11-5415 7656</span>',
   "top:660px;font-size:64px;letter-spacing:-.01em;background:none", anim="pop", drift=False, hold=True, id="endCta")
it(END_AT + 2.0, DUR - END_AT - 2.0, 'Music: “Inspiring Progress” by Soundrider/Dope · CC BY 3.0 · jamendo.com',
   "top:1000px;font-size:22px;font-weight:500;color:rgba(217,222,234,.7);letter-spacing:0;text-shadow:none;background:none", anim="fade", drift=False, hold=True, id="credit")
FLASH = [7.98, 37.70, 59.98, 67.43]
LEAKS = [15.43, 22.87, 45.16, 52.59]
LETTERBOX = [(30.30, 37.65)]
def beats(a, b, step=2): return [r(G0 + k * B) for k in range(0, 200, step) if a <= G0 + k * B < b - 0.05]
PULSE = beats(8.0, 15.4) + beats(22.87, 30.25)
SFX = [("sx-impact-bass-2", 0.0, 0.5, 2.0), ("sx-whoosh", 0.45, 0.45, 0.6), ("sx-pop", 1.2, 0.5, 0.4), ("sx-pop-3", 1.6, 0.6, 0.4),
       ("sx-whoosh-cinematic", 2.8, 0.5, 1.2), ("sx-riser", 5.9, 0.45, 2.1), ("sx-impact-bass-1", 7.95, 0.5, 1.6),
       ("sx-pop", 8.05, 0.42, 0.4), ("sx-pop-2", 9.9, 0.42, 0.4), ("sx-pop-3", 11.76, 0.42, 0.4), ("sx-pop-4", 13.62, 0.42, 0.4),
       ("sx-whoosh-soft", 15.3, 0.45, 0.8), ("sx-impact-bass-2", 22.5, 0.45, 1.6), ("sx-whoosh-soft", 30.15, 0.45, 0.8),
       ("sx-riser", 35.6, 0.42, 2.1), ("sx-impact-bass-2", 37.36, 0.5, 1.8),
       ("sx-pop-2", 38.17, 0.55, 0.4), ("sx-pop-3", 38.67, 0.55, 0.4), ("sx-pop-4", 39.17, 0.55, 0.4), ("sx-sparkle", 39.5, 0.45, 1.4),
       ("sx-whoosh-cinematic", 41.3, 0.45, 1.2), ("sx-sparkle", 41.7, 0.35, 1.4), ("sx-whoosh", 49.1, 0.45, 0.6)]
SFX += [("sx-click-hi", r(s0 + 0.3 + 0.3 * i), 0.35, 0.3) for i in range(4)]
SFX += [("sx-whoosh-soft", 52.45, 0.45, 0.8), ("sx-whoosh", 55.95, 0.45, 0.6), ("sx-impact-bass-2", 59.62, 0.5, 1.8), ("sx-whoosh-cinematic", 63.6, 0.45, 1.2),
        ("sx-impact-bass-2", 67.09, 0.5, 2.0), ("sx-sparkle", 68.0, 0.45, 1.4), ("sx-chime", 69.0, 0.3, 1.5)]
OUT = "index.html"
