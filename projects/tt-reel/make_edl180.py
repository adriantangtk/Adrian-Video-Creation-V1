#!/usr/bin/env python3
"""3-minute landscape cut on "Ambient Uplift" (Soundrider/Dope, 183.8 s, 129.2 BPM).
Cuts land on detected beats. Every source moment is used once (checked)."""
import json, os, sys
import numpy as np
VID = {int(l.split()[0]): "media/" + l.split()[1].split("media/")[-1] if "media/" in l else l.split()[1]
       for l in open("catalog/vids_n.txt")}
def V(n): return VID[n]
W, C, N = "assets/web/", "media/clients/", "media/nov26/"
beats = json.load(open("music/ambient-beats.json"))
B = np.array(beats)
def bi(t): return int(np.argmin(np.abs(B - t)))      # nearest beat index

SEC = {}           # name -> start time
plan = []          # (section, [(file, in, beats, opts)])
def section(name, t, shots): plan.append((name, t, shots))
def s(f, t, b, **o): return (f, t, b, o)

# ---------------- plan ----------------
section("hook", 0.0, [
    *[s(V(n), t, 0.25, grade="bw") for n, t in [(100, .6), (39, 3.2), (95, 12.4), (25, 14.2), (98, 7.2), (94, 6.4), (86, 2.2), (99, 10.4)]],
    s(W+"Event.jpg", None, 4.5),
    s(V(100), 5.6, 3, nat=.8), s(V(94), 4.5, 2, nat=.5), s(V(95), 9.5, 2, nat=.5),
    s(V(25), 10.0, 2, nat=.4), s(V(39), 1.6, 2, nat=.4), s(V(98), 3.6, 2, nat=.4), s(V(99), 13.2, 2)])
section("build", 10.2, [
    s(V(158), 1.5, 4, zoom=1.25, fx=.62), s(V(157), 30.5, 4), s(V(71), 2.0, 4), s(V(149), 2.0, 4),
    s(W+"IMG_20241128_142909-1-scaled.jpg", None, 4), s(W+"D3I08044-1-scaled.jpg", None, 4),
    s(V(74), 3.0, 4), s(V(59), 1.0, 4), s(V(64), 5.0, 4)])
section("drop", 26.0, [
    s(V(94), 20.0, 2, nat=.3), s(V(89), .5, 2, nat=.3), s(V(29), 19.0, 2), s(V(40), 2.0, 2),
    s(W+"IMG-20250722-WA0006.jpg", None, 2), s(V(32), 4.0, 2), s(W+"MOS06378-scaled.jpg", None, 2), s(V(16), 10.0, 2),
    s(V(33), 10.0, 2), s(V(34), 15.0, 2), s(V(19), 4.0, 2), s(V(15), 4.0, 2)])
section("trusted", 36.59, [
    s(V(72), 5.0, 6), s(V(75), 4.0, 6), s(V(141), 2.0, 4),
    s(V(99), 20.0, 2, nat=.3), s(V(98), 15.0, 2), s(V(96), 3.0, 2), s(V(100), 1.0, 2), s(V(101), 3.0, 2), s(V(46), 1.0, 2), s(V(47), .6, 2), s(V(30), 7.0, 2)])
section("coaches", 51.59, "COACHES")
section("pillars", 66.59, [
    s(V(156), 7.0, 4), s(V(164), 58.0, 4), s(V(2), 28.0, 4), s(V(63), 8.0, 4),
    s(V(95), 44.0, 4), s(V(90), 1.0, 4), s(V(53), 2.0, 4), s(V(58), 4.0, 4)])
section("exp", 81.59, [
    s(W+"IMG_20260415_144847-scaled.jpg", None, 2), s(V(12), 8.0, 2), s(V(17), 3.0, 2), s(V(93), .3, 2),
    s(V(84), .3, 2), s(V(79), 1.0, 2), s(V(88), .3, 2), s(V(91), 1.0, 2), s(V(13), 4.0, 2)])
section("breakdown", 90.3, [
    s(V(97), 6.5, 6, speed=.4), s(C+"photos/still_zurich_handshake_energiser.jpg", None, 4), s(V(83), 8.5, 4, speed=.6),
    s(V(45), 1.0, 4), s(W+"Image-5-1.jpg", None, 4), s(N+"photos/uob_20261121_092022.jpg", None, 4),
    s(W+"Image-5-5.jpg", None, 4), s(V(36), 6.0, 4, speed=.5)])
section("awards", 106.0, [s(V(169), 5.0, 12, speed=.6, grade="cool")])
section("soba", 111.6, [s(V(169), 22.0, 7), s(V(169), 62.0, 7)])
section("timeline", 118.2, [s(W+"Image-5-2.jpg", None, 18, grade="cool")])
section("proof", 126.6, [
    s(V(9), 2.0, 4, fx=.3), s(V(25), 15.0, 4), s(V(86), 3.5, 4), s(V(61), 4.0, 4),
    s(V(94), 8.5, 2, speed=1.6), s(V(94), 10.2, 2, speed=.45), s(V(62), 8.0, 4), s(V(65), 4.0, 4), s(V(66), 8.0, 4)])
section("finale", 141.6, [
    *[s(V(n), t, 1) for n, t in [(100, 13.0), (25, 20.0), (39, 24.0), (99, 6.0), (98, 21.0), (67, 6.0), (95, 30.0), (85, .3)]],
    s(V(159), 33.0, 7, zoom=1.3, fx=.45, fy=.3), s(V(9), 6.5, 3, fx=.3), s(V(87), 10.0, 3), s(V(134), 1.0, 3), s(V(44), 2.0, 3)])
section("grow", 156.6, [
    s(N+"photos/wsb_PXL_20261121_014528213.jpg", None, 4), s(C+"photos/still_fwd_hands_up_hall.jpg", None, 4),
    s(C+"photos/fwd_20260125_154323.jpg", None, 4), s(V(8), 2.0, 4),
    s(N+"photos/wsb_PXL_20261120_074833824.jpg", None, 4), s(V(3), 2.0, 4), s(C+"photos/still_zurich_hands_up.jpg", None, 4), s(V(86), .3, 4)])
section("end", 171.6, [s(N+"photos/uob_PXL_20261121_001503006.jpg", None, 30, grade="cool")])
END = 182.0

# coaches from trainer_shots180.json: list of {"file","in","beats", opts}
coach = json.load(open("trainer_shots180.json")) if os.path.exists("trainer_shots180.json") else [
    {"file": V(69), "in": 6.0, "beats": 4}, {"file": V(137), "in": 1.0, "beats": 4}, {"file": V(110), "in": 3.0, "beats": 4},
    {"file": V(124), "in": 10.0, "beats": 4}, {"file": V(159), "in": 160.0, "beats": 4, "zoom": 1.25, "fy": .3}]

# ---------------- build ----------------
shots, used, marks = [], {}, {}
for k, (name, t0, lst) in enumerate(plan):
    t1 = plan[k + 1][1] if k + 1 < len(plan) else END
    if lst == "COACHES":
        lst = [(c["file"], c.get("in"), c["beats"], {x: c[x] for x in c if x not in ("file", "in", "beats")}) for c in coach]
    b0 = bi(t0) if t0 > 0 else None
    start = 0.0 if t0 == 0 else float(B[b0])
    marks[name] = round(start, 3)
    end = float(B[bi(t1)]) if t1 < END else END
    def bt(x):  # time at fractional beat index x
        lo = int(np.floor(x)); lo = max(0, min(lo, len(B) - 2)); return float(B[lo] + (x - lo) * (B[lo + 1] - B[lo]))
    tcur = start; c = float(b0) if b0 is not None else None
    for j, (f, tin, nb, o) in enumerate(lst):
        last = j == len(lst) - 1
        if c is None: nxt = tcur + nb * 0.4644      # hook: plain grid from 0
        else: c += nb; nxt = bt(c)
        dur = (end - tcur) if last or nxt > end else (nxt - tcur)
        if dur <= 0.05: continue
        sh = {"file": f, "dur": round(dur, 4), **o}
        if tin is None: sh["still"] = True
        else: sh["in"] = tin
        sh.setdefault("grade", "warm")
        assert os.path.exists(f), f
        # uniqueness: photos once; video moments must not overlap
        span = (tin or 0, (tin or 0) + dur * float(o.get("speed", 1)))
        for a in used.get(f, []):
            if tin is None or not (span[1] <= a[0] or span[0] >= a[1]):
                sys.exit(f"DUPLICATE {f} {span} vs {a}")
        used.setdefault(f, []).append(span)
        shots.append(sh); tcur += dur
json.dump({"fps": 30, "size": [1920, 1080], "shots": shots}, open("edl180.json", "w"), indent=1)
json.dump(marks, open("marks180.json", "w"), indent=1)
print(f"total {sum(x['dur'] for x in shots):.2f}s, {len(shots)} shots, {len(used)} distinct sources")
print(marks)
