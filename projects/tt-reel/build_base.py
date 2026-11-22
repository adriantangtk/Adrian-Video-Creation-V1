#!/usr/bin/env python3
"""Cut the footage edit (EDL) into one vertical 1080x1920 base video + a natural-sound track.

usage: python3 build_base.py edl.json out_base.mp4 [--draft]

edl.json: {"fps":30, "shots":[{
   "file":"media/nov26/x.mp4", "in":12.3, "dur":0.8,       # dur = length ON THE TIMELINE (s)
   "speed":1.0,                                            # 0.5 = slow-mo, 2 = fast
   "fx":0.5, "fy":0.5,                                     # crop focus (0..1) when the frame is cropped to 9:16
   "zoom":1.0,                                             # extra punch-in
   "fit":"cover|blur",                                     # blur = full frame over a blurred copy (for wide shots)
   "blur":[[x,y,w,h], ...],                                 # boxes to blur in OUTPUT pixels (logos)
   "grade":"warm|cool|bw|none", "nat":0.0,                  # nat = volume of the clip's own sound (0 = off)
   "still":false                                           # true for photos (slow push-in)
}]}
"""
import json, subprocess, sys, os, tempfile

edl_path, out = sys.argv[1], sys.argv[2]
draft = "--draft" in sys.argv
edl = json.load(open(edl_path))
fps = edl.get("fps", 30)
W, H = 1080, 1920
root = os.path.dirname(os.path.abspath(__file__))  # file paths are relative to the project
import hashlib
tmp = os.path.join(root, "media", "segcache"); os.makedirs(tmp, exist_ok=True)
GRADES = {
    "warm": "eq=contrast=1.08:saturation=1.18:gamma=0.98,colorbalance=rs=0.04:bs=-0.04:rh=0.03:bh=-0.03",
    "cool": "eq=contrast=1.08:saturation=1.08,colorbalance=bs=0.04:rs=-0.02",
    "bw": "hue=s=0,eq=contrast=1.25:gamma=0.95",
    "none": "null",
}
segs, nat = [], []
t = 0.0
for i, s in enumerate(edl["shots"]):
    dur, speed = float(s["dur"]), float(s.get("speed", 1.0))
    src = os.path.join(root, s["file"])
    z = float(s.get("zoom", 1.0))
    fx, fy = float(s.get("fx", 0.5)), float(s.get("fy", 0.5))
    grade = GRADES[s.get("grade", "warm")]
    key = hashlib.md5((json.dumps(s, sort_keys=True) + str(draft) + str(fps)).encode()).hexdigest()[:12]
    seg = os.path.join(tmp, f"v_{key}.mp4")
    if s.get("still"):
        # photo: cover-crop + slow push-in over the shot
        n = max(1, round(dur * fps))
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z='{z}+0.06*on/{n}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d={n}:s={W}x{H}:fps={fps}")
        inp = ["-i", src]
    else:
        span = dur * speed
        inp = ["-ss", f"{float(s['in']):.3f}", "-t", f"{span + 0.2:.3f}", "-i", src]
        speedf = f"setpts=(PTS-STARTPTS)/{speed},fps={fps},trim=duration={dur:.3f}"
        if s.get("fit") == "blur":
            vf = (f"{speedf},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"boxblur=30:3,eq=brightness=-0.12[bg];[b]scale={W}*{z}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
        else:
            cw, ch = f"{W}*{z}", f"{H}*{z}"
            vf = (f"{speedf},scale='max({cw},{ch}*iw/ih)':'max({ch},{cw}*ih/iw)',"
                  f"crop={W}:{H}:'(iw-{W})*{fx}':'(ih-{H})*{fy}'")
    vf += f",{grade}"
    for k, (bx, by, bw, bh) in enumerate(s.get("blur", [])):
        vf += (f",split[m{k}][c{k}];[c{k}]crop={bw}:{bh}:{bx}:{by},boxblur=25:4[b{k}];"
               f"[m{k}][b{k}]overlay={bx}:{by}")
    vf += ",setsar=1,format=yuv420p"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inp, "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]",
           "-an", "-c:v", "libx264", "-preset", "veryfast" if draft else "medium", "-crf", "22" if draft else "17",
           "-g", "1", "-r", str(fps), seg]
    if not os.path.exists(seg):
        subprocess.run(cmd[:-1] + [seg + ".tmp.mp4"], check=True)
        os.replace(seg + ".tmp.mp4", seg)
    segs.append(seg)
    if float(s.get("nat", 0)) > 0 and not s.get("still"):
        a = os.path.join(tmp, f"a_{key}.wav")
        span = dur * speed
        tempo = []
        sp = speed
        while sp > 2.0: tempo.append("atempo=2.0"); sp /= 2.0
        while sp < 0.5: tempo.append("atempo=0.5"); sp /= 0.5
        tempo.append(f"atempo={sp}")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{float(s['in']):.3f}", "-t", f"{span:.3f}",
                            "-i", src, "-vn", "-af", ",".join(tempo) + f",afade=t=in:d=0.03,afade=t=out:st={max(0, dur-0.05):.3f}:d=0.05,volume={s['nat']}",
                            "-ar", "48000", "-ac", "2", a])
        if r.returncode == 0 and os.path.exists(a):
            nat.append((a, t))
    t += dur
    print(f"\rshot {i+1}/{len(edl['shots'])}", end="", flush=True)
print()
lst = os.path.join(tmp, os.path.basename(out) + ".list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
if nat:
    natout = out.replace(".mp4", "-nat.wav")
    ins, fl = [], []
    for k, (a, st) in enumerate(nat):
        ins += ["-i", a]
        ms = round(st * 1000)
        fl.append(f"[{k}:a]adelay={ms}|{ms}[n{k}]")
    fl.append("".join(f"[n{k}]" for k in range(len(nat))) + f"amix=inputs={len(nat)}:normalize=0,apad,atrim=0:{t:.3f}[o]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fl), "-map", "[o]", natout], check=True)
    print("nat track:", natout)
print(f"base: {out} ({t:.2f}s)")
