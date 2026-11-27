"""QC of a rendered version: specs, black/frozen frames, loudness and peaks, review stills."""
import json, re
from pathlib import Path
from .common import active_project, rj, wj, run, now, die, FORMATS
from .media import probe, contact_sheet


def qc_file(path, fmt, stills_dir=None, n_stills=8):
    W, H = FORMATS[fmt]
    p = probe(path)
    v, au = p.get("video", {}), p.get("audio", {})
    issues = []
    if (v.get("w"), v.get("h")) != (W, H):
        issues.append(f"resolution {v.get('w')}x{v.get('h')} != {W}x{H}")
    if v.get("codec") != "h264":
        issues.append(f"video codec {v.get('codec')} (want h264)")
    if v.get("pix_fmt") != "yuv420p":
        issues.append(f"pix_fmt {v.get('pix_fmt')}")
    if au.get("codec") != "aac":
        issues.append(f"audio codec {au.get('codec')} (want aac)")
    r = run(["ffmpeg", "-v", "info", "-nostdin", "-i", str(path), "-vf", "blackdetect=d=0.12:pix_th=0.08,freezedetect=n=-55dB:d=1.5",
             "-af", "ebur128=peak=true", "-f", "null", "-"], check=False)
    err = r.stderr
    black = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]
    freeze = re.findall(r"freeze_start: ([\d.]+)", err)
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    tp = re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", err)
    lufs = float(lufs[-1]) if lufs else None
    tpv = float(tp[-1]) if tp and tp[-1] not in ("-inf", "inf") else None
    if black:
        issues.append(f"black frames at {', '.join(f'{a:.2f}-{b:.2f}' for a, b in black[:6])}")
    if freeze:
        issues.append(f"frozen picture from {', '.join(freeze[:6])} s (fine if it is a photo or hold)")
    if lufs is not None and not (-15.5 <= lufs <= -12.5):
        issues.append(f"loudness {lufs} LUFS (target -14)")
    if tpv is not None and tpv > -0.9:
        issues.append(f"true peak {tpv} dBFS (risk of clipping)")
    res = {"file": str(path), "format": fmt, "checked": now(), "probe": p, "lufs": lufs, "true_peak": tpv,
           "black": black, "freeze_starts": freeze, "issues": issues, "size_mb": round(Path(path).stat().st_size / 1e6, 2)}
    if stills_dir:
        sd = Path(stills_dir)
        sd.mkdir(parents=True, exist_ok=True)
        dur = p["duration"]
        ts = [round(dur * (i + 0.5) / n_stills, 2) for i in range(n_stills)]
        imgs = []
        for t in ts:
            f = sd / f"{fmt}-{int(t * 1000):07d}.jpg"
            run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", str(t), "-i", str(path), "-frames:v", "1", "-vf",
                 "scale='if(gt(iw,ih),640,-2)':'if(gt(iw,ih),-2,640)'", "-q:v", "4", str(f)])
            imgs.append(f)
        sheet = contact_sheet(imgs, [f"{t:.1f}s" for t in ts], sd / f"{fmt}-review.jpg", cols=4, cell=420, title=f"QC {Path(path).name}")
        res["review_sheet"] = str(sheet)
    return res


def cmd_qc(a):
    pr = active_project(a.project)
    v = a.version or pr.meta().get("current_version") or die("no version")
    vdir = pr.p("versions", v)
    if a.file:
        files = [(Path(a.file), a.format or "vertical")]
    else:
        files = [(f, fmt) for fmt in FORMATS for f in sorted(vdir.glob(f"*-{fmt}-{v}.mp4"))]
    if not files:
        die(f"nothing rendered in {v}")
    rep = rj(vdir / "qc.json", {})
    for f, fmt in files:
        r = qc_file(f, fmt, vdir / "stills" if not a.file else Path(a.file).parent / "stills")
        rep[fmt if not a.file else f.name] = r
        print(f"{f.name}: {r['probe']['duration']:.2f}s {r['probe']['video']['w']}x{r['probe']['video']['h']} "
              f"{r['probe']['video']['fps']}fps {r['size_mb']}MB  {r['lufs']} LUFS  TP {r['true_peak']}")
        for i in r["issues"]:
            print(f"  ! {i}")
        if not r["issues"]:
            print("  specs/black/loudness OK")
        print(f"  review sheet: {r.get('review_sheet')}")
    if not a.file:
        wj(vdir / "qc.json", rep)
