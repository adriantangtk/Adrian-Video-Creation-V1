#!/usr/bin/env python3
"""75 s cut: shot list on the music's beat grid -> edl75.json (+ prints section times).
Music: Inspiring Progress (track offset 1.4 s), 129.2 BPM -> beat 0.4644 s, grid starts 0.109 s."""
import json
B = 0.4644
G0 = 0.109
C, N = "media/clients/", "media/nov26/"
V = "media/voice/"
def beat(k): return G0 + k * B

# (file, in, beats, opts)  -- beats may be fractional
shots = []
def add(f, t, beats, **o): shots.append(dict(file=f, **({"in": t} if t is not None else {}), beats=beats, **o))

# A. HOOK  0 -> beat 17 (8.0 s): "What if Monday felt like this?" + "Highest energy wins."
add(N+"wsb_PXL_20261121_015136670.mp4", 5.5, 6, nat=0.9, grade="warm", zoom=1.1)          # arms up, roar
add(N+"wsb_PXL_20261120_075153223.mp4", 4.5, 2, nat=0.5)                                   # relay sprint
add(N+"wsb_PXL_20261120_075426549.mp4", 9.5, 2, nat=0.5)                                   # crash past lens
add(C+"zoct21d1/IMG_1045.MOV", 10.0, 2, nat=0.4)                                           # ballroom hands up
add(C+"zsep17d1/20250917_110918.mp4", 2.0, 2, nat=0.4)                                     # hugs + laughs
add(N+"wsb_PXL_20261121_014957264.mp4", 6.5, 1.25, nat=0.5)                                # hijab laugh
add(N+"wsb_PXL_20261121_015050579.mp4", 9.0, 0.6)                                          # flash
add(N+"wsb_PXL_20261120_075426549.mp4", 23.0, 0.6)                                         # flash
add(N+"wsb_PXL_20261120_075153223.mp4", 30.0, 0.55)                                                 # flash
# B. DROP montage  beat 17 -> 33 : modules
add(N+"wsb_PXL_20261120_075153223.mp4", 20.0, 2, nat=0.3)        # TEAM BUILDING
add(N+"wsb_PXL_20261120_033022217.mp4", 0.5, 2, nat=0.3)
add(N+"uob_PXL_20261120_070557700.mp4", 0.3, 2)
add(C+"zsep25d1/20250925_152714.mp4", 12.0, 2)                          # ENERGISERS
add(C+"zsep25d1/20250925_152714.mp4", 4.0, 2)
add(N+"uob_PXL_20261120_114722714.mp4", 4.0, 2)
add(N+"uob_20261121_081604.mp4", 1.0, 2)     # OUTDOOR
add(C+"zsep17d1/20250917_111045.mp4", 2.0, 2)
# C. SPEAKER  beat 33 -> 49 : "In life, there is no failure. There is only feedback."
add(V+"mt-img1057.mov", 1.5, 4, fx=0.97, zoom=1.35, fy=0.4)                         # Michael on stage, batik, wide
add(N+"rise_20261120_133644.mp4", 2.0, 4)                         # Michael in red blazer in the crowd
add(C+"zsep25d1/20250925_110313.mp4", 2.0, 4)
add(V+"mt-img1057.mov", 6.5, 4, fx=0.55)
# D. MONTAGE 2  beat 49 -> 65 : "Team one, make some noise!"
add(C+"zsep26d2/video6257767053919262675.mp4", 2.0, 2, nat=0.3)
add(C+"zsep17d1/20250917_110842.mp4", 4.0, 2)
add(C+"zsep17d1/20250917_111045.mp4", 8.0, 2)
add(C+"jan26/20260125_113946.mp4", 8.0, 2)
add(N+"wsb_PXL_20261121_015050579.mp4", 20.0, 2)
add(N+"uob_PXL_20261120_114722714.mp4", 9.0, 2)
add(N+"uob_PXL_20261120_113506110.mp4", 1.0, 2)
add(N+"wsb_PXL_20261120_075426549.mp4", 23.5, 2)
# E. EMOTIONAL  beat 65 -> 81 : "You can all be excellent..."
add(N+"wsb_PXL_20261121_011811672.mp4", 6.5, 6, speed=0.4, grade="warm")
add(C+"photos/still_zurich_handshake_energiser.jpg", None, 4, still=True)
add(C+"zsep17d1/20250917_110918.mp4", 22.0, 4, speed=0.5)
add(N+"photos/uob_PXL_20261121_011752035.jpg", None, 2, still=True)
# F. AWARDS  beat 81 -> 97 : HRVOTY cards over blurred SOBA ballroom, then SOBA stage
add(V+"soba-img0912.mov", 5.0, 8, grade="cool", fit="cover", speed=0.6)   # ballroom, darkened by overlay
add(V+"soba-img0912.mov", 22.0, 4)                                        # Michael walks up in red suit
add(V+"soba-img0912.mov", 62.0, 4)                                        # on stage: BEST EMPLOYER
# G. PROOF  beat 97 -> 113 : "How we do anything is how we do everything."
add(C+"jan26/20260125_113946.mp4", 28.0, 4)
add(C+"zsep25d1/20250925_152742.mp4", 4.0, 4)
add(C+"photos/still_zurich_hands_up.jpg", None, 4, still=True)
add(C+"jan26/20260125_113946.mp4", 2.0, 4)
# H. FINALE  beat 113 -> 129 : "Give yourself a huge round of applause, everybody!"
add(V+"mt-vid20250513.mp4", 33.0, 6, fx=0.5, zoom=1.25)
add(C+"jan26/20260125_160002.mp4", 2.0, 3, fx=0.3)
add(C+"zsep17d1/20250917_110918.mp4", 6.0, 2)
add(N+"wsb_PXL_20261120_075426549.mp4", 44.0, 2)
add(N+"uob_PXL_20261120_113506110.mp4", 3.5, 3)
# I. CTA  beat 129 -> 145
add(N+"photos/wsb_PXL_20261121_014528213.jpg", None, 8, still=True, fy=0.1)
add(N+"photos/uob_20261121_092022.jpg", None, 8, still=True)
# J. END CARD  (navy, graphics only) beat 145 -> end 75.0
add(N+"photos/uob_PXL_20261121_001503006.jpg", None, 16.3, still=True, grade="cool")

t = 0.0
out = []
for s in shots:
    dur = round(s.pop("beats") * B + (G0 if not out else 0), 4)
    s["dur"] = dur
    s.setdefault("grade", "warm")
    out.append(s)
    t += dur
json.dump({"fps": 30, "shots": out}, open("edl75.json", "w"), indent=1)
print(f"total {t:.2f}s, {len(out)} shots")
for name, k in [("drop", 17), ("speaker", 33), ("montage2", 49), ("emotional", 65), ("awards", 81),
                ("proof", 97), ("finale", 113), ("cta", 129), ("end", 145)]:
    print(name, round(beat(k), 3))
