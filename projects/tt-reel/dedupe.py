import json, sys
p = sys.argv[1]; e = json.load(open(p))
N, C = "media/nov26/", "media/clients/"
ALT = [(N+"wsb_PXL_20261120_075153223.mp4", 14.0), (N+"wsb_PXL_20261120_075426549.mp4", 36.0), (N+"wsb_PXL_20261121_015050579.mp4", 3.0),
       (C+"zsep17d1/20250917_111045.mp4", 14.0), (C+"jan26/20260125_154133.mp4", 5.0), (N+"uob_PXL_20261120_113506110.mp4", 6.0),
       (C+"zsep25d1/20250925_110220.mp4", 12.0), (N+"wsb_PXL_20261120_075153223.mp4", 36.0), (N+"wsb_PXL_20261121_014957264.mp4", 18.0),
       (C+"zsep25d1/20250925_152742.mp4", 12.0), (N+"wsb_PXL_20261120_075426549.mp4", 2.0), (C+"jan26/20260125_153936.mp4", 6.0)]
k = 0; n = 0; sh = e["shots"]
for i, s in enumerate(sh):
    if not s.get("still") or "Event.jpg" in s["file"] or i >= len(sh) - 1: continue
    if any(x["file"] == s["file"] for x in sh[max(0, i - 14):i]):
        f, t = ALT[k % len(ALT)]; k += 1; n += 1
        for x in ("still", "zoom", "fx", "fy"): s.pop(x, None)
        s["file"], s["in"] = f, t
json.dump(e, open(p, "w"), indent=1); print("deduped", n)
