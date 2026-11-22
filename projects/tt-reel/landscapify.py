#!/usr/bin/env python3
"""Replace portrait-source shots in a landscape EDL with landscape footage/photos (keeps timing).
usage: python3 landscapify.py in.json out.json [keep-substring ...]"""
import json, subprocess, sys
src, dst, keep = sys.argv[1], sys.argv[2], sys.argv[3:] + ["soba-img0912", "mt-vid20250513"]
C, N, W = "media/clients/", "media/nov26/", "assets/web/"
POOL = [(C+"zsep25d1/20250925_110220.mp4", 1.0), (W+"IMG-20250722-WA0006.jpg", None), (W+"D3I08044-1-scaled.jpg", None),
        (C+"zoct21d1/20251021_100454.mp4", 10.0), (W+"IMG_20241128_142909-1-scaled.jpg", None), (C+"photos/fwd_20260125_113938.jpg", None),
        (N+"wsb_PXL_20261121_015050579.mp4", 15.0), (C+"zsep17d1/20250917_110918.mp4", 12.0), (W+"Image-5-5.jpg", None),
        (N+"uob_PXL_20261120_113506110.mp4", 5.0), (C+"jan26/20260125_153936.mp4", 2.0), (N+"wsb_PXL_20261120_075153223.mp4", 12.0),
        (C+"zsep17d1/20250917_111045.mp4", 4.0), (W+"MOS06378-scaled.jpg", None), (C+"jan26/20260125_154133.mp4", 2.0),
        (N+"wsb_PXL_20261120_075426549.mp4", 30.0), (C+"zsep25d1/20250925_110220.mp4", 4.5), (W+"IMG-20250722-WA0006.jpg", None)]
asp = {}
def aspect(f):
    if f not in asp:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                            "-of", "json", f], capture_output=True, text=True)
        st = json.loads(r.stdout)["streams"][0]; w, h = st["width"], st["height"]
        rot = abs(int(float(next((d.get("rotation", 0) for d in st.get("side_data_list", []) if "rotation" in d), 0))))
        if rot in (90, 270): w, h = h, w
        asp[f] = w / h
    return asp[f]
e = json.load(open(src)); k = 0; n = 0
for s in e["shots"]:
    if aspect(s["file"]) >= 1.2 or any(x in s["file"] for x in keep) or s.get("grade") == "bw":
        continue
    f, t = POOL[k % len(POOL)]; k += 1; n += 1
    s["file"] = f
    for x in ("in", "still", "fx", "fy", "zoom", "fit", "speed"): s.pop(x, None)
    if t is None: s["still"] = True
    else: s["in"] = t
# logo fixups for the wider landscape frame
for s in e["shots"]:
    if "20250917_110918" in s["file"]: s["zoom"] = 1.3; s["fx"] = 1.0
    if "20251021_100454" in s["file"]: s["file"], s["in"] = C+"zsep25d1/20250925_110220.mp4", 8.0
    if "015136670" in s["file"] and s.get("grade") != "bw" and s["dur"] > 1.5:
        s["file"] = W+"Event.jpg"; s.pop("in", None); s["still"] = True; s["zoom"] = 1.0; s.pop("nat", None)
json.dump(e, open(dst, "w"), indent=1)
print(f"replaced {n} portrait shots")
