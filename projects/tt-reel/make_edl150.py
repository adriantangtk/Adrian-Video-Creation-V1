#!/usr/bin/env python3
"""2.5 min landscape cut on the 150 s bed (Inspiring Progress, looped on phrase boundaries).
Beat 0.4644 s, grid 0.109 s; sections are 16 beats (7.43 s) after a 17-beat hook."""
import json, os, sys
B, G0 = 0.4644, 0.109
C, N, V, W = "media/clients/", "media/nov26/", "media/voice/", "assets/web/"
TR = json.load(open("trainer_shots.json")) if os.path.exists("trainer_shots.json") else None
shots, marks = [], {}
def add(f, t, beats, **o):
    shots.append(dict(file=f, **({"in": t} if t is not None else {"still": True}), beats=beats, **o))
def sec(name): marks[name] = sum(s["beats"] for s in shots)

# S0 HOOK (17 beats): B&W flash cold open -> colour arms-up
sec("hook")
for f, t in [(N+"wsb_PXL_20261121_015136670.mp4", 0.5), (C+"zsep17d1/20250917_110918.mp4", 3.0), (N+"wsb_PXL_20261120_075426549.mp4", 12.0),
             (C+"zoct21d1/IMG_1045.MOV", 14.0), (N+"wsb_PXL_20261121_014957264.mp4", 7.0), (N+"wsb_PXL_20261120_075153223.mp4", 6.0),
             (N+"uob_PXL_20261120_113506110.mp4", 2.0), (N+"wsb_PXL_20261121_015050579.mp4", 10.0)]:
    add(f, t, 0.25, grade="bw")
add(N+"wsb_PXL_20261121_015136670.mp4", 5.6, 4, nat=0.8)
add(N+"wsb_PXL_20261120_075153223.mp4", 4.5, 2, nat=0.5)
add(N+"wsb_PXL_20261120_075426549.mp4", 9.5, 2, nat=0.5)
add(C+"zoct21d1/IMG_1045.MOV", 10.0, 2, nat=0.4)
add(C+"zsep17d1/20250917_110918.mp4", 2.0, 2, nat=0.4)
add(N+"wsb_PXL_20261121_014957264.mp4", 6.5, 1.25, nat=0.4)
add(N+"wsb_PXL_20261121_015050579.mp4", 9.0, 0.6)
add(N+"wsb_PXL_20261120_075426549.mp4", 23.0, 0.6)
add(N+"wsb_PXL_20261120_075153223.mp4", 30.0, 0.55)
# S1 DROP: what we do
sec("drop")
add(N+"wsb_PXL_20261120_075153223.mp4", 20.0, 2, nat=0.3)
add(N+"wsb_PXL_20261120_033022217.mp4", 0.5, 2, nat=0.3)
add(W+"IMG-20250722-WA0006.jpg", None, 2)
add(C+"zoct22d2/20251022_155716.mp4", 4.0, 2)
add(C+"zsep25d1/20250925_152714.mp4", 12.0, 2)
add(C+"zsep17d1/20250917_111045.mp4", 2.0, 2)
add(W+"MOS06378-scaled.jpg", None, 2)
add(W+"IMG_20260415_144847-scaled.jpg", None, 2)
# S2 MICHAEL: "no failure, only feedback"
sec("michael")
add(V+"mt-img1057.mov", 1.5, 4, zoom=1.25, fx=0.62)
add(W+"Event.jpg", None, 4, zoom=1.0)
add(W+"IMG_20241128_142909-1-scaled.jpg", None, 4)
add(N+"rise_20261120_133644.mp4", 2.0, 4)
# S3 WHO WE ARE: stats over footage
sec("stats")
add(W+"D3I08044-1-scaled.jpg", None, 8)
add(N+"wsb_PXL_20261120_075153223.mp4", 28.0, 8)
# S4 MONTAGE + "Team one, make some noise!"
sec("noise")
add(C+"zsep26d2/video6257767053919262675.mp4", 2.0, 2, nat=0.3)
add(C+"zsep17d1/20250917_110842.mp4", 4.0, 2)
add(C+"zsep17d1/20250917_111045.mp4", 8.0, 2)
add(C+"jan26/20260125_113946.mp4", 8.0, 2)
add(N+"wsb_PXL_20261121_015050579.mp4", 20.0, 2)
add(N+"uob_PXL_20261120_114722714.mp4", 9.0, 2)
add(N+"uob_PXL_20261120_113506110.mp4", 1.0, 2)
add(N+"wsb_PXL_20261120_075426549.mp4", 23.5, 2)
# S5-S6 COACHES (replaced by trainer_shots.json when available)
sec("coaches")
if TR:
    for s in TR: add(s["file"], s.get("in"), s["beats"], **{k: v for k, v in s.items() if k in ("zoom", "fx", "fy", "speed", "grade", "blur")})
else:
    add(C+"zsep18d2/20250918_104103.mp4", 32.0, 4)
    add(C+"zsep25d1/20250925_110313.mp4", 2.0, 4)
    add(N+"cag_20261114_164349.mp4", 2.0, 4)
    add(N+"rise_20261120_133644.mp4", 6.0, 4)
    add(C+"zsep25d1/20250925_103214.mp4", 4.0, 4)
    add(C+"zsep17d1/20250917_121145.mp4", 1.0, 4)
    add(N+"photos/wsb_PXL_20261120_115154444.jpg", None, 4)
    add(C+"zsep18d2/20250918_104103.mp4", 50.0, 4)
# S7 SOLUTIONS: four pillars
sec("pillars")
add(C+"zoct22d2/20251022_155716.mp4", 14.0, 4)
add(C+"jan26/20260125_113946.mp4", 2.0, 4)
add(N+"wsb_PXL_20261120_075426549.mp4", 44.0, 4)
add(C+"zsep25d1/20250925_152742.mp4", 4.0, 4)
# S8 EXPERIENTIAL
sec("exp")
add(W+"MOS06378-scaled.jpg", None, 4, zoom=1.1)
add(N+"wsb_PXL_20261120_033113845.mp4", 0.3, 2)
add(N+"uob_PXL_20261120_070557700.mp4", 0.3, 2)
add(N+"wsb_PXL_20261120_032749664.mp4", 0.3, 2)
add(N+"uob_20261121_081604.mp4", 1.0, 2)
add(N+"photos/uob_PXL_20261121_011752035.jpg", None, 2)
add(W+"Image-5-5.jpg", None, 2)
# S9 EMOTIONAL 1: "You can all be excellent"
sec("emo1")
add(N+"wsb_PXL_20261121_011811672.mp4", 6.5, 6, speed=0.4)
add(C+"photos/still_zurich_handshake_energiser.jpg", None, 4)
add(C+"zsep17d1/20250917_110918.mp4", 22.0, 4, speed=0.5)
add(N+"photos/uob_PXL_20261121_001503006.jpg", None, 2)
# S10 EMOTIONAL 2: "When I fail, I learn"
sec("emo2")
add(W+"Image-5-1.jpg", None, 4)
add(N+"wsb_PXL_20261121_014957264.mp4", 6.3, 4, speed=0.5)
add(N+"photos/uob_20261121_092022.jpg", None, 4)
add(W+"Image-5-5.jpg", None, 4, zoom=1.08, fx=0.3)
# S11 AWARDS 2026 + SOBA
sec("awards")
add(V+"soba-img0912.mov", 5.0, 8, speed=0.6, grade="cool")
add(V+"soba-img0912.mov", 22.0, 4)
add(V+"soba-img0912.mov", 62.0, 4)
# S12 TIMELINE of honours (graphic over dimmed gala photo)
sec("timeline")
add(W+"Image-5-2.jpg", None, 16, grade="cool")
# S13 PROOF: "How we do anything..."
sec("proof")
add(C+"jan26/20260125_113946.mp4", 28.0, 4)
add(C+"zsep25d1/20250925_152742.mp4", 8.0, 4)
add(C+"photos/still_zurich_hands_up.jpg", None, 4)
add(C+"photos/fwd_20260125_113938.jpg", None, 4)
# S14 HIGH ENERGY: 1-beat cuts + "Change your mindset"
sec("energy")
for f, t, b in [(N+"wsb_PXL_20261121_015136670.mp4", 0.3, 1), (C+"zoct21d1/IMG_1045.MOV", 12.0, 1), (C+"zsep17d1/20250917_110918.mp4", 24.0, 1),
                (N+"wsb_PXL_20261121_015050579.mp4", 9.0, 1), (N+"wsb_PXL_20261121_014957264.mp4", 15.0, 1), (C+"zsep26d2/video6257767053919262675.mp4", 6.0, 1),
                (N+"wsb_PXL_20261120_075426549.mp4", 10.0, 1), (N+"uob_PXL_20261120_113457097.mp4", 0.3, 1),
                (N+"uob_PXL_20261120_114722714.mp4", 5.0, 2), (N+"wsb_PXL_20261120_075153223.mp4", 22.0, 2),
                (C+"zsep17d1/20250917_111045.mp4", 12.0, 2), (C+"jan26/20260125_160002.mp4", 3.0, 2, )]:
    add(f, t, b, fx=0.3 if "160002" in f else 0.5)
# S15 HIGH-PERFORMING UNITS (speed ramps)
sec("units")
add(N+"wsb_PXL_20261120_075153223.mp4", 4.5, 2, speed=1.6)
add(N+"wsb_PXL_20261120_075153223.mp4", 6.0, 2, speed=0.45)
add(N+"wsb_PXL_20261120_075426549.mp4", 44.0, 4)
add(C+"zoct21d1/IMG_1045.MOV", 15.0, 4)
add(N+"uob_PXL_20261120_113506110.mp4", 3.5, 4)
# S16 FINALE: Michael "Give yourself a huge round of applause" (lip-synced)
sec("finale")
add(V+"mt-vid20250513.mp4", 33.0, 6, zoom=1.3, fx=0.45, fy=0.3)
add(C+"jan26/20260125_160002.mp4", 2.0, 3, fx=0.3)
add(C+"zsep17d1/20250917_110918.mp4", 6.0, 2)
add(N+"wsb_PXL_20261120_075426549.mp4", 46.0, 2)
add(N+"uob_PXL_20261120_114722714.mp4", 10.0, 3)
# S17 PEOPLE GROW: photos
sec("grow")
add(N+"photos/wsb_PXL_20261121_014528213.jpg", None, 4)
add(W+"IMG_20260415_144847-scaled.jpg", None, 4)
add(N+"photos/uob_20261121_092022.jpg", None, 4)
add(C+"photos/still_fwd_hands_up_hall.jpg", None, 4)
# S18 CTA
sec("cta")
add(W+"Event.jpg", None, 8, zoom=1.05)
add(W+"D3I08044-1-scaled.jpg", None, 8)
# S19 END CARD
sec("end")
add(N+"photos/uob_PXL_20261121_001503006.jpg", None, 17.9, grade="cool")

out, t = [], 0.0
for s in shots:
    assert os.path.exists(s["file"]), s["file"]
    s = dict(s); dur = round(s.pop("beats") * B + (G0 if not out else 0), 4)
    s["dur"] = dur; s.setdefault("grade", "warm"); out.append(s); t += dur
json.dump({"fps": 30, "size": [1920, 1080], "shots": out}, open("edl150.json", "w"), indent=1)
json.dump({k: round(G0 + v * B, 3) if v else 0.0 for k, v in marks.items()}, open("marks150.json", "w"), indent=1)
print(f"total {t:.2f}s, {len(out)} shots"); print(json.load(open("marks150.json")))
