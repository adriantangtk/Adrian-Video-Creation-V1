"""Indexing: probe, frame-by-frame index, scenes, thumbnails, contact sheets, audio stats, transcripts, digests."""
import gzip, json, os, re, shutil, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .common import active_project, rj, wj, run, now, fmt_t, die, tool

SCENE_THR = 0.30
MAX_THUMBS = 48


# ---------------------------------------------------------------- probe

def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    d = json.loads(r.stdout)
    fmt = d.get("format", {})
    out = {"duration": float(fmt.get("duration") or 0), "size": int(fmt.get("size") or 0),
           "format": fmt.get("format_name"), "created": (fmt.get("tags") or {}).get("creation_time")}
    for s in d.get("streams", []):
        if s["codec_type"] == "video" and "video" not in out and s.get("disposition", {}).get("attached_pic", 0) == 0:
            rot = 0
            for sd in s.get("side_data_list", []) or []:
                if "rotation" in sd:
                    rot = int(sd["rotation"])
            rot = int((s.get("tags") or {}).get("rotate", rot))
            w, h = s.get("width"), s.get("height")
            if abs(rot) % 180 == 90:
                w, h = h, w
            num, den = (s.get("avg_frame_rate") or "0/1").split("/")
            fps = float(num) / float(den) if float(den) else 0
            out["video"] = {"codec": s.get("codec_name"), "w": w, "h": h, "fps": round(fps, 3), "rotation": rot,
                            "pix_fmt": s.get("pix_fmt"), "frames": int(s.get("nb_frames") or 0) or None,
                            "hdr": s.get("color_transfer") in ("smpte2084", "arib-std-b67")}
        elif s["codec_type"] == "audio" and "audio" not in out:
            out["audio"] = {"codec": s.get("codec_name"), "rate": int(s.get("sample_rate") or 0), "channels": s.get("channels")}
    return out


# ---------------------------------------------------------------- per-kind indexing

def _frame_pass(src, out_gz):
    """One decode pass: every frame's number, pts, scene score, luma and saturation."""
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as tf:
        txt = tf.name
    esc = txt.replace(":", "\\:")
    run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(src), "-map", "0:v:0", "-an", "-vf",
         f"scale=160:-2,signalstats,select='gte(scene\\,0)',metadata=print:file={esc}", "-f", "null", "-"])
    rows, cur = [], None
    with open(txt) as f:
        for line in f:
            if line.startswith("frame:"):
                m = re.match(r"frame:(\d+)\s+pts:\S+\s+pts_time:(\S+)", line)
                cur = {"n": int(m.group(1)), "t": round(float(m.group(2)), 4)}
                rows.append(cur)
            elif cur is not None and "=" in line:
                k, v = line.strip().split("=", 1)
                if k == "lavfi.scene_score":
                    cur["scene"] = round(float(v), 4)
                elif k == "lavfi.signalstats.YAVG":
                    cur["y"] = round(float(v), 1)
                elif k == "lavfi.signalstats.SATAVG":
                    cur["sat"] = round(float(v), 1)
    os.unlink(txt)
    with gzip.open(out_gz, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    return rows


def _scenes(rows, dur):
    bounds, last = [0.0], 0.0
    for r in rows:
        if r.get("scene", 0) >= SCENE_THR and r["t"] - last >= 0.8:
            bounds.append(r["t"]); last = r["t"]
    return [{"start": round(b, 3), "end": round(bounds[i + 1] if i + 1 < len(bounds) else dur, 3)} for i, b in enumerate(bounds)]


def _thumb(src, t, dest, long_side=320):
    vf = f"scale='if(gt(iw,ih),{long_side},-2)':'if(gt(iw,ih),-2,{long_side})'"
    run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", "-vf", vf,
         "-q:v", "4", str(dest)])


def contact_sheet(images, labels, dest, cols=6, cell=320, title=""):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    if not images:
        return None
    rows = (len(images) + cols - 1) // cols
    top = 28 if title else 0
    try:  # cell height follows the frames' aspect ratio
        w0, h0 = Image.open(images[0]).size
        cellh = int(min(cell * 1.8, max(cell * 0.5, cell * h0 / w0))) + 22
    except Exception:
        cellh = cell
    sheet = Image.new("RGB", (cols * cell, rows * cellh + top), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((8, 7), title, fill=(230, 230, 230))
    for i, (img, lab) in enumerate(zip(images, labels)):
        try:
            im = Image.open(img).convert("RGB")
        except Exception:
            continue
        im.thumbnail((cell - 6, cellh - 22))
        x, y = (i % cols) * cell, (i // cols) * cellh + top
        sheet.paste(im, (x + (cell - im.width) // 2, y + 3))
        d.rectangle([x + 3, y + cellh - 19, x + 3 + 7 * len(lab) + 6, y + cellh - 4], fill=(0, 0, 0))
        d.text((x + 6, y + cellh - 18), lab, fill=(255, 214, 10))
    sheet.save(dest, quality=82)
    return dest


def _audio_stats(src, has_video):
    r = run(["ffmpeg", "-v", "info", "-nostdin", "-i", str(src), "-map", "0:a:0", "-vn", "-af",
             "silencedetect=noise=-32dB:d=0.35,ebur128=peak=true", "-f", "null", "-"], check=False)
    err = r.stderr
    sil = [(float(a), float(b)) for a, b in zip(re.findall(r"silence_start: ([\d.]+)", err), re.findall(r"silence_end: ([\d.]+)", err))]
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    peak = re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", err)
    return {"lufs": float(lufs[-1]) if lufs else None, "true_peak": peak[-1] if peak else None,
            "silences": [[round(a, 2), round(b, 2)] for a, b in sil][:400]}


def index_video(pr, e, src, d):
    info = probe(src)
    dur = info["duration"]
    rows = _frame_pass(src, d / "frames.jsonl.gz")
    scenes = _scenes(rows, dur)
    ys = [r["y"] for r in rows if "y" in r]
    q = {"frames_decoded": len(rows), "luma_mean": round(sum(ys) / len(ys), 1) if ys else None,
         "dark_pct": round(100 * sum(y < 35 for y in ys) / len(ys), 1) if ys else None,
         "bright_pct": round(100 * sum(y > 215 for y in ys) / len(ys), 1) if ys else None,
         "sat_mean": round(sum(r.get("sat", 0) for r in rows) / max(1, len(rows)), 1)}
    if "audio" in info:
        q["audio"] = _audio_stats(src, True)
    interval = 2.0 if dur <= 60 else 4.0 if dur <= 180 else max(6.0, dur / MAX_THUMBS)
    ts = sorted({round(min(0.1, dur / 2), 2)} | {round(s["start"] + 0.15, 2) for s in scenes[1:]}
                | {round(i * interval, 2) for i in range(1, int(dur / interval) + 1)})
    keep = []
    for t in ts:
        if t < dur - 0.05 and (not keep or t - keep[-1] >= 0.6):
            keep.append(t)
    if len(keep) > MAX_THUMBS:
        step = len(keep) / MAX_THUMBS
        keep = [keep[int(i * step)] for i in range(MAX_THUMBS)]
    th = d / "thumbs"
    th.mkdir(exist_ok=True)
    thumbs = []
    for t in keep:
        p = th / f"t{int(t * 1000):07d}.jpg"
        if not p.exists():
            _thumb(src, t, p)
        why = "scene" if any(abs(s["start"] + 0.15 - t) < 0.01 for s in scenes) else "interval"
        thumbs.append({"t": t, "file": f"thumbs/{p.name}", "why": why})
    contact_sheet([d / x["file"] for x in thumbs], [fmt_t(x["t"]) for x in thumbs], d / "contact.jpg", title=f"{e['id']}  {e['name']}")
    return {"probe": info, "scenes": scenes, "quality": q, "thumbs": thumbs}


def index_photo(pr, e, src, d):
    info = {"kind": "photo"}
    th = d / "thumbs"
    th.mkdir(exist_ok=True)
    try:
        from PIL import Image, ImageOps, ImageStat
        im = Image.open(src)
        exif = im.getexif()
        info.update(w=im.width, h=im.height, taken=exif.get(36867) or exif.get(306))
        im = ImageOps.exif_transpose(im).convert("RGB")
        info["w"], info["h"] = im.width, im.height
        info["luma_mean"] = round(ImageStat.Stat(im.convert("L")).mean[0], 1)
        im.thumbnail((320, 320))
        im.save(th / "t0000000.jpg", quality=82)
    except Exception:
        _thumb(src, 0, th / "t0000000.jpg")
        info.update(probe(src).get("video", {}))
    return {"probe": info, "thumbs": [{"t": 0, "file": "thumbs/t0000000.jpg", "why": "photo"}], "scenes": [], "quality": {}}


def index_audio(pr, e, src, d):
    info = probe(src)
    return {"probe": info, "quality": {"audio": _audio_stats(src, False)}, "thumbs": [], "scenes": []}


def _index_one(pr, e):
    src = pr.local_file(e)
    if not src or not Path(src).exists():
        return e["id"], "missing local file (run fetch)"
    d = pr.idx(e["id"])
    d.mkdir(parents=True, exist_ok=True)
    try:
        fn = {"video": index_video, "photo": index_photo, "audio": index_audio}[e["kind"]]
        res = fn(pr, e, src, d)
        res.update(id=e["id"], name=e["name"], kind=e["kind"], sha256=e.get("sha256"), indexed=now())
        wj(d / "index.json", res)
        return e["id"], None
    except Exception as ex:
        return e["id"], str(ex)[-400:]


def cmd_index(a):
    pr = active_project(a.project)
    man = pr.manifest()
    todo = []
    for e in man["media"].values():
        if e.get("status") == "removed" or e.get("duplicate_of") or e.get("status") == "pending":
            continue
        if a.ids and e["id"] not in a.ids:
            continue
        if not a.force and e.get("stages", {}).get("index") == e.get("sha256") and pr.idx(e["id"]).joinpath("index.json").exists():
            continue
        todo.append(e)
    print(f"indexing {len(todo)} item(s) with {a.jobs} worker(s)")
    errors = []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for mid, err in ex.map(lambda e: _index_one(pr, e), todo):
            if err:
                errors.append((mid, err))
    with pr.lock():
        man = pr.manifest()
        for e in todo:
            if e["id"] not in dict(errors):
                man["media"][e["id"]].setdefault("stages", {})["index"] = e.get("sha256")
                man["media"][e["id"]]["status"] = "indexed"
        pr.save_manifest(man)
    pr.log("index", {"done": len(todo) - len(errors), "errors": errors})
    print(f"done {len(todo) - len(errors)}, errors {len(errors)}")
    for m, err in errors:
        print(f"  {m}: {err}")


# ---------------------------------------------------------------- transcripts

def ensure_model(model):
    """HyperFrames' own model fetch can hit a CDN host the network blocks; curl follows a reachable mirror."""
    d = Path.home() / ".cache" / "hyperframes" / "whisper" / "models"
    f = d / f"ggml-{model}.bin"
    if f.exists() and f.stat().st_size > 10_000_000:
        return f
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading whisper model {model} (one time)")
    run(["curl", "-sSL", "--retry", "4", "-C", "-", "-o", str(f) + ".part",
         f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{model}.bin"], check=True, timeout=1800)
    os.replace(str(f) + ".part", f)
    return f


def _hf_transcribe(wav, model, lang):
    ensure_model(model)
    with tempfile.TemporaryDirectory() as td:
        cmd = ["npx", "--yes", "hyperframes@0.8.116", "transcribe", str(wav), "-m", model, "--json", "-d", td]
        if lang:
            cmd += ["-l", lang]
        r = run(cmd, check=False, timeout=3600)
        txt = r.stdout
        data = None
        for p in sorted(Path(td).rglob("*.json")):
            try:
                data = json.loads(p.read_text()); break
            except Exception:
                pass
        if data is None:
            i = txt.find("{"); j = txt.find("[")
            k = min(x for x in (i, j) if x >= 0) if max(i, j) >= 0 else -1
            if k < 0:
                raise RuntimeError((r.stderr or txt)[-600:])
            data = json.loads(txt[k:])
    if isinstance(data, dict) and data.get("ok") is False:
        raise RuntimeError(f"transcriber error: {data.get('error')}")
    return data


def _norm_words(data):
    """Normalise any whisper/HyperFrames JSON into [{w,s,e}]."""
    words = []

    def walk(o):
        if isinstance(o, dict):
            w = o.get("text", o.get("word"))
            s = o.get("start", o.get("s"))
            e = o.get("end", o.get("e"))
            if isinstance(w, str) and isinstance(s, (int, float)) and isinstance(e, (int, float)) and " " not in w.strip():
                words.append({"w": w.strip(), "s": round(float(s), 3), "e": round(float(e), 3)})
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)
    words = [w for w in words if w["w"]]
    words.sort(key=lambda x: x["s"])
    return words


HALLUCINATIONS = ("thanks for watching", "thank you for watching", "subscribe", "like and subscribe", "see you next time",
                  "bye", "you", "thank you", "music", "applause", "blank_audio", "silence")


def _drop_hallucinations(words):
    """Whisper invents stock phrases over music/noise: drop sparse segments that are only such phrases."""
    kept, dropped = [], []
    for seg in _segments(words):
        txt = re.sub(r"[^a-z_ ]", "", seg["text"].lower()).strip()
        span = max(0.01, seg["e"] - seg["s"])
        n = len(seg["text"].split())
        bracket = re.fullmatch(r"\s*[\[(].*[\])]\s*", seg["text"]) is not None
        if bracket or (txt in HALLUCINATIONS and (n / span < 1.2 or span > 3)):
            dropped.append(seg["text"])
        else:
            kept += [w for w in words if seg["s"] <= w["s"] <= seg["e"]]
    return kept, dropped


def _segments(words):
    segs, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > 0.6 or re.search(r"[.!?]$", cur[-1]["w"]) or len(cur) >= 24):
            segs.append(cur); cur = []
        cur.append(w)
    if cur:
        segs.append(cur)
    return [{"s": s[0]["s"], "e": s[-1]["e"], "text": " ".join(x["w"] for x in s)} for s in segs]


def cmd_transcribe(a):
    pr = active_project(a.project)
    man = pr.manifest()
    model = a.model or ("small.en" if (a.language or "en").startswith("en") else "small")
    todo = [e for e in man["media"].values() if e["kind"] in ("video", "audio") and e.get("status") not in ("pending", "removed")
            and not e.get("duplicate_of") and (not a.ids or e["id"] in a.ids)
            and (a.force or e.get("stages", {}).get("transcribe") != e.get("sha256"))]
    wavdir = pr.cache / "wav"
    wavdir.mkdir(parents=True, exist_ok=True)
    done = 0
    for e in todo:
        info = rj(pr.idx(e["id"]) / "index.json", {})
        if "audio" not in info.get("probe", {}):
            continue
        wav = wavdir / f"{e['id']}.wav"
        run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", str(pr.local_file(e)), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
        try:
            words, dropped = _drop_hallucinations(_norm_words(_hf_transcribe(wav, model, a.language)))
        except Exception as ex:
            print(f"  {e['id']} transcription failed: {str(ex)[-300:]}")
            continue
        wj(pr.idx(e["id"]) / "transcript.json", {"model": model, "words": words, "segments": _segments(words), "made": now(), "dropped_as_hallucination": dropped,
                                                 "note": "machine transcript: verify names and quotes before use"})
        with pr.lock():
            m2 = pr.manifest()
            m2["media"][e["id"]].setdefault("stages", {})["transcribe"] = e.get("sha256")
            m2["media"][e["id"]]["status"] = "indexed"
            pr.save_manifest(m2)
        done += 1
        print(f"  {e['id']} {len(words)} words" + (f" (dropped likely hallucination: {dropped})" if dropped else ""))
    pr.log("transcribe", {"done": done, "model": model})
    print(f"transcribed {done}/{len(todo)}")


# ---------------------------------------------------------------- compact views for the model

def cmd_digest(a):
    pr = active_project(a.project)
    man = pr.manifest()
    ann = rj(pr.p("annotations.json"), {})
    if a.id:
        e = man["media"].get(a.id) or die(f"unknown id {a.id}")
        d = pr.idx(a.id)
        ix = rj(d / "index.json", {})
        print(f"{a.id} {e['name']} [{e['kind']}] path={e.get('path')}")
        print("probe:", json.dumps(ix.get("probe", {}), separators=(",", ":")))
        print("quality:", json.dumps({k: v for k, v in ix.get("quality", {}).items() if k != "audio"}, separators=(",", ":")),
              "audio:", json.dumps({k: v for k, v in ix.get("quality", {}).get("audio", {}).items() if k != "silences"}))
        sc = ix.get("scenes", [])
        print(f"scenes ({len(sc)}): " + " ".join(f"{fmt_t(s['start'])}" for s in sc[:60]))
        print(f"contact sheet: {d / 'contact.jpg'}" if (d / 'contact.jpg').exists() else "contact sheet: none")
        print(f"thumbs: {d / 'thumbs'} ({len(ix.get('thumbs', []))})")
        tr = rj(d / "transcript.json")
        if tr:
            print("transcript:")
            for s in tr["segments"]:
                if a.since is None or s["e"] >= a.since:
                    print(f"  [{s['s']:.2f}-{s['e']:.2f}] {s['text']}")
        if a.id in ann:
            print("annotations:", json.dumps(ann[a.id], ensure_ascii=False)[:3000])
        return
    print("id        kind  dur    res        fps   scenes speech status    name")
    for e in sorted(man["media"].values(), key=lambda x: x.get("path", "")):
        if e.get("status") == "removed" and not a.all:
            continue
        if a.new and e.get("stages", {}).get("annotated") == e.get("sha256"):
            continue
        ix = rj(pr.idx(e["id"]) / "index.json", {})
        p = ix.get("probe", {})
        v = p.get("video", p)
        tr = rj(pr.idx(e["id"]) / "transcript.json")
        words = len(tr["words"]) if tr else "-"
        dup = f" dup-of:{e['duplicate_of']}" if e.get("duplicate_of") else ""
        print(f"{e['id']} {e['kind'][:5]:5s} {p.get('duration', 0):6.1f} {str(v.get('w', '-')) + 'x' + str(v.get('h', '-')):10s} "
              f"{v.get('fps', '-')!s:5s} {len(ix.get('scenes', [])):6d} {words!s:6s} {e.get('status', '?'):9s} {e.get('path', e['name'])}{dup}"
              f"{'  [annotated]' if e['id'] in ann else ''}")


def cmd_find(a):
    pr = active_project(a.project)
    q = a.text.lower().split()
    for tp in sorted(pr.p("index").glob("*/transcript.json")):
        w = rj(tp)["words"]
        toks = [re.sub(r"[^\w']", "", x["w"].lower()) for x in w]
        for i in range(len(toks) - len(q) + 1):
            if all(toks[i + j].startswith(q[j]) for j in range(len(q))):
                s = max(0, i - 8); e = min(len(w), i + len(q) + 12)
                print(f"{tp.parent.name} {w[i]['s']:.2f}  ..." + " ".join(x["w"] for x in w[s:e]) + "...")


def cmd_frame(a):
    """Full-resolution still(s) for close visual analysis, on demand."""
    pr = active_project(a.project)
    e = pr.manifest()["media"].get(a.id) or die(f"unknown id {a.id}")
    out = pr.cache / "frames"
    out.mkdir(parents=True, exist_ok=True)
    for t in a.times:
        dest = out / f"{a.id}_{int(t * 1000):07d}.jpg"
        vf = [] if a.full else ["-vf", "scale='if(gt(iw,ih),1280,-2)':'if(gt(iw,ih),-2,1280)'"]
        run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", f"{t:.3f}", "-i", str(pr.local_file(e)), "-frames:v", "1", *vf, "-q:v", "3", str(dest)])
        print(dest)


def cmd_sheet(a):
    """Contact sheet of a time range at a fixed step: zoom into a moment without loading many images."""
    pr = active_project(a.project)
    e = pr.manifest()["media"].get(a.id) or die(f"unknown id {a.id}")
    src = pr.local_file(e)
    tmp = Path(tempfile.mkdtemp())
    ts, t = [], a.start
    while t <= a.end + 1e-6 and len(ts) < 36:
        ts.append(round(t, 3)); t += a.step
    imgs = []
    for t in ts:
        p = tmp / f"{t:.3f}.jpg"
        _thumb(src, t, p)
        imgs.append(p)
    out = pr.cache / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{a.id}_{a.start:.2f}-{a.end:.2f}.jpg"
    contact_sheet(imgs, [fmt_t(t) for t in ts], dest, cols=min(6, len(ts)), title=f"{a.id} {e['name']}")
    shutil.rmtree(tmp)
    print(dest)
