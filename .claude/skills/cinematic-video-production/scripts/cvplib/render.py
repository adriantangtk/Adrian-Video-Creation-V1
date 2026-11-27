"""FFmpeg editor: storyboard JSON -> cached per-shot intermediates -> one assembly pass (transitions, mix, captions)."""
import json, re, shutil, statistics
from pathlib import Path
from .common import active_project, rj, wj, run, now, die, FORMATS, SAFE, short_hash, fmt_t

RENDERER = "cvp-render-1"
XFADE = {"dissolve": "fade", "crossfade": "fade", "fade": "fadeblack", "black": "fadeblack", "flash": "fadewhite",
         "white": "fadewhite", "whip": "smoothleft", "whip-left": "smoothleft", "whip-right": "smoothright",
         "wipe": "wipeleft", "slide": "slideleft", "zoom": "zoomin", "circle": "circleopen", "blur": "hblur",
         "push-up": "slideup", "push-down": "slidedown"}


def _even(x):
    return int(round(x / 2) * 2)


def _fps_for(pr, sb):
    if sb.get("fps"):
        return float(sb["fps"])
    rates = []
    for s in sb["shots"]:
        ix = rj(pr.idx(s["clip"]) / "index.json", {})
        f = ix.get("probe", {}).get("video", {}).get("fps")
        if f and ix.get("kind") == "video":
            rates.append(f)
    if not rates:
        return 30.0
    med = statistics.median(rates)
    return min([23.976, 24, 25, 29.97, 30, 50, 59.94, 60], key=lambda r: abs(r - med))


def _atempo(speed):
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0"); s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5"); s /= 0.5
    parts.append(f"atempo={s:.5f}")
    return ",".join(parts)


def _has_speech(pr, s):
    if "speech" in s:
        return bool(s["speech"])
    tr = rj(pr.idx(s["clip"]) / "transcript.json")
    if not tr or s.get("kind") == "photo":
        return False
    return sum(1 for w in tr["words"] if s["in"] <= w["s"] < s["out"]) >= 2


def _shot(pr, s, fmt, fps, draft, man):
    W, H = FORMATS[fmt]
    e = man["media"][s["clip"]]
    src = pr.local_file(e)
    ix = rj(pr.idx(s["clip"]) / "index.json")
    photo = s["kind"] == "photo"
    speed = float(s.get("speed", 1.0))
    length = float(s.get("dur", 3.0)) if photo else (s["out"] - s["in"]) / speed
    N = max(1, round(length * fps))
    z0 = float(s.get("zoom", 1.0))
    z1 = float(s.get("zoom_to", 1.06 if photo else z0))
    fx0, fy0 = s.get("focus", [0.5, 0.5])
    fx1, fy1 = s.get("focus_to", [fx0, fy0])
    has_audio = "audio" in ix["probe"] and not photo and s.get("audio", "source") != "mute"
    gain = s.get("audio_gain_db", 0 if _has_speech(pr, s) else -8)
    key = dict(r=RENDERER, sha=e.get("sha256"), s={k: s.get(k) for k in ("in", "out", "dur", "speed", "zoom", "zoom_to", "focus",
               "focus_to", "grade", "audio", "motion_blur")}, gain=gain, W=W, H=H, fps=fps, draft=draft)
    out = pr.cache / "shots" / f"{short_hash(key)}.mkv"
    if out.exists():
        return out, N / fps
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = []
    if not photo:
        vf.append(f"setpts=(PTS-STARTPTS)/{speed}")
        if speed >= 1.5 and s.get("motion_blur", True):
            vf.append("tmix=frames=3:weights='1 2 1'")
    zm = max(z0, z1)
    pan = (fx0, fy0) != (fx1, fy1)
    if zm <= 1.0001 and not pan:
        vf.append(f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}:(iw-ow)*{fx0}:(ih-oh)*{fy0}")
    else:
        zm = max(zm, 1.0)
        CW, CH = _even(W * zm * 1.5), _even(H * zm * 1.5)  # oversample so zoompan only downsizes
        fxe = f"({fx0}+({fx1}-{fx0})*on/{N})"
        fye = f"({fy0}+({fy1}-{fy0})*on/{N})"
        vf.append(f"scale={CW}:{CH}:force_original_aspect_ratio=increase:flags=lanczos,crop={CW}:{CH}:(iw-ow)*{fx0}:(ih-oh)*{fy0}")
        vf.append(f"fps={fps}")
        # zoom is relative to the cover frame; a panned shot needs headroom: use at least 1.08
        za, zb = (max(z0, 1.08), max(z1, 1.08)) if pan else (z0, z1)
        vf.append(f"zoompan=z='{za}+({zb}-{za})*on/{N}':x='(iw-iw/zoom)*{fxe}':y='(ih-ih/zoom)*{fye}':d=1:s={W}x{H}:fps={fps}")
    vf.append(f"fps={fps}")
    if s.get("grade"):
        vf.append(s["grade"])
    vf.append("setsar=1,format=yuv420p")
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-y"]
    if photo:
        cmd += ["-loop", "1", "-framerate", str(fps), "-t", f"{length + 0.5:.3f}", "-i", str(src)]
    else:
        cmd += ["-ss", f"{s['in']:.3f}", "-t", f"{(s['out'] - s['in']) + 0.25:.3f}", "-i", str(src)]
    if has_audio:
        af = f"[0:a]asetpts=PTS-STARTPTS,{_atempo(speed)},volume={gain}dB,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{N / fps:.4f}[a]"
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        af = f"[1:a]atrim=0:{N / fps:.4f}[a]"
    graph = f"[0:v]{','.join(vf)}[v];{af}"
    enc = ["-c:v", "libx264", "-preset", "ultrafast" if draft else "veryfast", "-crf", "26" if draft else "12", "-g", str(int(fps))]
    cmd += ["-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(N), *enc, "-c:a", "pcm_s16le", str(out)]
    run(cmd)
    return out, N / fps


# ---------------------------------------------------------------- captions / overlays (ASS)

def _ass_col(hexcol, alpha=0):
    h = hexcol.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _ts(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _vis(s):
    return len(re.sub(r"\{[^}]*\}", "", s))


def _wrap(text, size, width):
    maxc = max(8, int(width / (size * 0.56)))
    out = []
    for para in text.split("\\N"):
        line = ""
        for w in para.split():
            if line and _vis(line) + 1 + _vis(w) > maxc:
                out.append(line); line = w
            else:
                line = f"{line} {w}".strip()
        out.append(line)
    return "\\N".join(out)


def build_ass(pr, sb, fmt, shots_t):
    W, H = FORMATS[fmt]
    x0, y0, x1, y1 = SAFE[fmt]
    br = {"accent": "#FFD60A", "text": "#FFFFFF", "box": "#111111", "font": "Inter", **(sb.get("brand") or {})}
    vert = fmt == "vertical"
    cs = sb.get("captions") or {}
    csize = cs.get("size", 66 if vert else 56)
    cap_y = cs.get("y", 1300 if vert else 960)
    styles = {
        "Caption": (br["font"], csize, br["text"], "#9A9A9A", "#000000", 1, 1, 4.5, 1.5, 2, x0, W - x1, H - cap_y),
        "Hook": (br["font"], 96 if vert else 84, br["text"], br["accent"], "#000000", 1, 1, 5, 2, 5, x0, W - x1, 0),
        "Kinetic": (br["font"], 128 if vert else 110, br["text"], br["accent"], "#000000", 1, 1, 5, 2, 5, x0, W - x1, 0),
        "Lower": (br["font"], 46 if vert else 42, br["text"], br["accent"], br["box"], 1, 3, 14, 0, 1, x0, W - x1, H - (1380 if vert else 990)),
        "Callout": (br["font"], 44 if vert else 40, br["text"], br["accent"], br["box"], 1, 3, 12, 0, 5, x0, W - x1, 0),
    }
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
             "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"]
    for n, (font, size, pc, sc, oc, bold, bs, outl, shad, al, ml, mr, mv) in styles.items():
        lines.append(f"Style: {n},{font},{size},{_ass_col(pc)},{_ass_col(sc)},{_ass_col(oc)},{_ass_col('#000000', 0x60)},"
                     f"{-1 if bold else 0},0,0,0,100,100,0,0,{bs},{outl},{shad},{al},{ml},{mr},{mv},1")
    lines += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    acc = _ass_col(br["accent"])
    kws = {k.lower() for k in cs.get("keywords", [])}
    fixes = {k.lower(): v for k, v in (cs.get("fixes") or {}).items()}
    maxw = cs.get("max_words", 3 if vert else 6)
    events = []
    # spoken captions from transcripts, remapped to the output timeline
    if cs.get("enabled", True):
        for s, (t0, L) in zip(sb["shots"], shots_t):
            if s.get("captions") == "none" or s["kind"] == "photo":
                continue
            if isinstance(s.get("captions"), list):
                for c in s["captions"]:
                    events.append((t0 + c["start"], t0 + c["end"], "Caption", _wrap(c["text"], csize, x1 - x0), ""))
                continue
            tr = rj(pr.idx(s["clip"]) / "transcript.json")
            if not tr:
                continue
            sp = float(s.get("speed", 1.0))
            ws = [dict(w, s=t0 + (w["s"] - s["in"]) / sp, e=t0 + (min(w["e"], s["out"]) - s["in"]) / sp)
                  for w in tr["words"] if s["in"] <= w["s"] < s["out"] - 0.05]
            chunks, cur = [], []
            for w in ws:
                if cur and (len(cur) >= maxw or w["s"] - cur[-1]["e"] > 0.35 or re.search(r"[.!?,]$", cur[-1]["w"])):
                    chunks.append(cur); cur = []
                cur.append(w)
            if cur:
                chunks.append(cur)
            for i, c in enumerate(chunks):
                end = min(c[-1]["e"] + 0.25, chunks[i + 1][0]["s"] if i + 1 < len(chunks) else t0 + L)
                txt = ""
                for w in c:
                    word = fixes.get(re.sub(r"[^\w']", "", w["w"].lower()), w["w"])
                    k = max(1, int(round((w["e"] - w["s"]) * 100)))
                    if re.sub(r"[^\w']", "", word.lower()) in kws:
                        txt += f"{{\\k{k}\\c{acc}\\fscx118\\fscy118}}{word.upper() if cs.get('upper_keywords', True) else word}{{\\r}} "
                    else:
                        txt += f"{{\\k{k}}}{word} "
                pop = "{\\fad(50,40)\\fscx86\\fscy86\\t(0,90,\\fscx100\\fscy100)}"
                events.append((c[0]["s"] - 0.04, end, "Caption", pop + txt.strip(), ""))
    # overlays: per-shot (relative) and global (absolute)
    ovs = [(t0 + o.get("start", 0), o) for s, (t0, L) in zip(sb["shots"], shots_t) for o in s.get("overlay", [])]
    ovs += [(o.get("start", 0), o) for o in sb.get("overlays", [])]
    for st, o in ovs:
        style = {"hook": "Hook", "kinetic": "Kinetic", "lower": "Lower", "lower-third": "Lower", "callout": "Callout"}.get(o.get("style", "hook"), "Hook")
        size = {"Hook": 96 if vert else 84, "Kinetic": 128 if vert else 110, "Lower": 46, "Callout": 44}[style]
        px, py = o.get("pos", {"Hook": [W / 2, 420 if vert else 200], "Kinetic": [W / 2, 860 if vert else 540],
                               "Lower": [x0 + 10, 1380 if vert else 990], "Callout": [W / 2, 700 if vert else 300]}[style])
        px, py = min(max(px, x0), x1), min(max(py, y0), y1)
        text = _wrap(o["text"], size, (x1 - x0) if style != "Lower" else (x1 - x0) * 0.8)
        for h_ in o.get("highlight", []):
            text = re.sub(re.escape(h_), lambda m: "{\\c" + acc + "}" + m.group(0) + "{\\r}", text, flags=re.I)
        an = o.get("anim", "pop")
        align = "\\an1" if style == "Lower" else "\\an5"
        if an == "slide":
            tag = f"{{{align}\\move({px - 90},{py},{px},{py},0,260)\\fad(120,160)}}"
        elif an == "fade":
            tag = f"{{{align}\\pos({px},{py})\\fad(220,220)}}"
        elif an == "type":
            tag = f"{{{align}\\pos({px},{py})\\fad(0,160)}}"
            n = max(1, len(o["text"]))
            step = max(20, int(min(900, o.get("dur", 1.8) * 400) / n))
            out, ci = "", 0
            for ch in text:  # reveal character by character
                out += f"{{\\alpha&HFF&\\t({ci * step},{ci * step + 1},\\alpha&H00&)}}{ch}" if ch not in "{}\\" else ch
                ci += 1
            text = out if "{" not in o["text"] else text
        else:
            tag = f"{{{align}\\pos({px},{py})\\fscx40\\fscy40\\t(0,140,\\fscx108\\fscy108)\\t(140,230,\\fscx100\\fscy100)\\fad(0,160)}}"
        events.append((st, st + float(o.get("dur", 1.8)), style, tag + text, ""))
    for st, en, style, txt, _ in sorted(events):
        lines.append(f"Dialogue: {1 if style != 'Caption' else 0},{_ts(st)},{_ts(en)},{style},,0,0,0,,{txt}")
    return "\n".join(lines) + "\n", len(events)


# ---------------------------------------------------------------- EDL (editable timeline for Premiere/Resolve)

def _tc(t, fps):
    f = int(round(t * fps)); r = int(round(fps))
    return f"{f // (3600 * r):02d}:{f // (60 * r) % 60:02d}:{f // r % 60:02d}:{f % r:02d}"


def build_edl(sb, shots_t, fps, man, title):
    out = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]
    for i, (s, (t0, L)) in enumerate(zip(sb["shots"], shots_t), 1):
        name = man["media"][s["clip"]]["name"]
        sin = 0 if s["kind"] == "photo" else s["in"]
        sout = sin + (L if s["kind"] == "photo" else (s["out"] - s["in"]))
        tr = "C   " if s.get("transition", "cut") == "cut" or i == 1 else f"D    {int(round(float(s.get('transition_dur', 0.3)) * fps)):03d}"
        out.append(f"{i:03d}  {Path(name).stem[:8].upper():8s} V     {tr} {_tc(sin, fps)} {_tc(sout, fps)} {_tc(t0, fps)} {_tc(t0 + L, fps)}")
        out.append(f"* FROM CLIP NAME: {name}")
        if abs(float(s.get("speed", 1)) - 1) > 1e-3:
            out.append(f"M2   {Path(name).stem[:8].upper():8s}       {float(s['speed']) * fps:05.1f}                {_tc(sin, fps)}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- versions

def _loudness_trim(path, target):
    """Single-pass loudnorm undershoots on short edits: measure, then apply the remaining gain (video stream copied)."""
    r = run(["ffmpeg", "-v", "info", "-nostdin", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], check=False)
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    if not i or abs(float(i[-1]) - target) <= 0.7:
        return
    gain = target - float(i[-1])
    tmp = path.with_name(path.stem + ".lt.mp4")
    run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", str(path), "-c:v", "copy", "-af",
         f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false,aresample=48000", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(tmp)])
    tmp.replace(path)


def cmd_version_new(a):
    pr = active_project(a.project)
    m = pr.meta()
    nums = [int(p.name[1:]) for p in pr.p("versions").glob("v[0-9][0-9][0-9]")]
    v = f"v{(max(nums) + 1 if nums else 1):03d}"
    d = pr.p("versions", v)
    d.mkdir(parents=True)
    (d / "notes.md").write_text(f"# {v}\ncreated {now()}\n\n{a.note or ''}\n")
    m["current_version"] = v
    pr.save_meta(m)
    pr.log("version", {"version": v, "note": a.note})
    print(f"{v} created: {d}")


def cmd_render(a):
    pr = active_project(a.project)
    meta = pr.meta()
    v = meta.get("current_version") or die("no version: run `version-new` first")
    vdir = pr.p("versions", v)
    fmt = a.format
    sb = rj(pr.p("storyboards", f"{fmt}.json")) or die(f"no validated {fmt} storyboard (run `storyboard`)")
    man = pr.manifest()
    W, H = FORMATS[fmt]
    fps = _fps_for(pr, sb)
    base = f"{meta['client']}-{meta['project']}-{fmt}-{v}"
    if a.draft:
        dd = vdir / "drafts"
        dd.mkdir(exist_ok=True)
        n = len(list(dd.glob(f"{fmt}-draft*.mp4"))) + 1
        out = dd / f"{fmt}-draft{n}.mp4"
    else:
        out = vdir / f"{base}.mp4"
        if out.exists():
            die(f"{out.name} exists: versions are never overwritten. Run `version-new` for the next version.")
    print(f"rendering {fmt} {W}x{H} @ {fps} fps, {len(sb['shots'])} shots{' (draft)' if a.draft else ''}")
    parts = []
    for s in sb["shots"]:
        parts.append(_shot(pr, s, fmt, fps, a.draft, man))
    # timeline from real (frame-quantised) lengths
    starts, cur = [], 0.0
    for i, (s, (_, L)) in enumerate(zip(sb["shots"], parts)):
        if i == 0:
            starts.append(0.0); cur = L; continue
        d = 0.0 if s.get("transition", "cut") == "cut" else min(float(s.get("transition_dur", 0.3)), L / 2, cur / 2)
        s["_d"] = d
        starts.append(cur - d); cur = cur - d + L
    total = cur
    shots_t = [(st, L) for st, (_, L) in zip(starts, parts)]
    inputs, g = [], []
    for p, _ in parts:
        inputs += ["-i", str(p)]
    n = len(parts)
    for i in range(n):
        g.append(f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
    curv, curlen = "[v0]", parts[0][1]
    for i in range(1, n):
        s = sb["shots"][i]
        if s.get("_d", 0) <= 0:
            g.append(f"{curv}[v{i}]concat=n=2:v=1:a=0[c{i}]")
        else:
            tr = XFADE.get(s.get("transition"), s.get("transition"))
            g.append(f"{curv}[v{i}]xfade=transition={tr}:duration={s['_d']:.3f}:offset={curlen - s['_d']:.3f}[c{i}]")
            curlen -= s["_d"]
        curlen += parts[i][1]
        curv = f"[c{i}]"
    # captions/overlays
    ass, nev = build_ass(pr, sb, fmt, shots_t)
    ass_path = (vdir / "drafts" if a.draft else vdir) / f"{fmt}-captions.ass"
    ass_path.parent.mkdir(exist_ok=True)
    ass_path.write_text(ass)
    vbase = curv
    # audio: natural sound per shot, speech bus for ducking, music, sfx
    nat, speech = [], []
    duck = bool((sb.get("music") or {}).get("track"))
    for i, (s, (st, L)) in enumerate(zip(sb["shots"], shots_t)):
        dl = int(round(st * 1000))
        fin = s.get("_d", 0) or 0.012
        fout = (sb["shots"][i + 1].get("_d", 0) if i + 1 < n else 0) or 0.012
        chain = f"[{i}:a]afade=t=in:d={fin:.3f},afade=t=out:st={max(0, L - fout):.3f}:d={fout:.3f},adelay={dl}|{dl}"
        if duck and s["kind"] != "photo" and _has_speech(pr, s):
            g.append(f"{chain},asplit=2[n{i}][sp{i}]")
            speech.append(f"[sp{i}]")
        else:
            g.append(f"{chain}[n{i}]")
        nat.append(f"[n{i}]")
    g.append(f"{''.join(nat)}amix=inputs={n}:normalize=0:dropout_transition=0,apad,atrim=0:{total:.4f}[nat]")
    mixes = ["[nat]"]
    k = n
    mus = sb.get("music") or {}
    music_report = None
    if mus.get("track"):
        tm = rj(pr.p("music", mus["track"], "track.json")) or die(f"unknown music {mus['track']}")
        inputs += ["-i", str(pr.dir / tm["file"])]
        fo = float(mus.get("fade_out", 1.5))
        g.append(f"[{k}:a]atrim=start={float(mus.get('start', 0)):.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                 f"volume={mus.get('gain_db', -10)}dB,apad,atrim=0:{total:.4f},afade=t=in:d=0.25,afade=t=out:st={max(0, total - fo):.3f}:d={fo}[mus]")
        k += 1
        if speech:
            g.append(f"{''.join(speech)}amix=inputs={len(speech)}:normalize=0,apad,atrim=0:{total:.4f}[spb]")
            g.append(f"[mus][spb]sidechaincompress=threshold={mus.get('duck_threshold', 0.02)}:ratio={mus.get('duck_ratio', 8)}:attack=15:release=450[musd]")
            mixes.append("[musd]")
        else:
            mixes.append("[mus]")
        music_report = {k2: tm.get(k2) for k2 in ("id", "title", "artist", "source", "license", "license_verified")}
    sfx = list(sb.get("sfx", [])) + [dict(x, at=st + x.get("at", 0)) for s, (st, L) in zip(sb["shots"], shots_t) for x in s.get("sfx", [])]
    for j, x in enumerate(sfx):
        f = Path(x["file"])
        f = f if f.is_absolute() else (pr.dir / f if (pr.dir / f).exists() else Path.cwd() / f)
        if not f.exists():
            die(f"sfx file not found: {x['file']}")
        inputs += ["-i", str(f)]
        dl = int(round(max(0, x["at"]) * 1000))
        trim = f",atrim=0:{x['dur']},afade=t=out:st={max(0, x['dur'] - 0.08)}:d=0.08" if x.get("dur") else ""
        g.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo{trim},volume={x.get('gain_db', -6)}dB,adelay={dl}|{dl}[fx{j}]")
        mixes.append(f"[fx{j}]")
        k += 1
    # logo / image overlays (e.g. end card): {"file","start","dur","width","pos":[cx,cy],"fade"}
    for j, lg in enumerate(sb.get("logos", [])):
        f = Path(lg["file"])
        f = f if f.is_absolute() else pr.dir / f
        if not f.exists():
            die(f"logo file not found: {lg['file']}")
        inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(f)]
        st, du, fd = float(lg.get("start", 0)), float(lg.get("dur", 3)), float(lg.get("fade", 0.4))
        cx, cy = lg.get("pos", [FORMATS[fmt][0] / 2, FORMATS[fmt][1] / 2])
        g.append(f"[{k}:v]format=rgba,scale={int(lg.get('width', 600))}:-1:flags=lanczos,"
                 f"fade=t=in:st={st:.3f}:d={fd}:alpha=1,fade=t=out:st={st + du - fd:.3f}:d={fd}:alpha=1[lg{j}]")
        g.append(f"{vbase}[lg{j}]overlay=x={cx}-w/2:y={cy}-h/2:enable='between(t,{st:.3f},{st + du:.3f})'[vl{j}]")
        vbase = f"[vl{j}]"
        k += 1
    if nev:
        g.append(f"{vbase}ass=filename='{ass_path}':fontsdir='/usr/share/fonts'[vout]")
    else:
        g.append(f"{vbase}null[vout]")
    g.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0:duration=first,"
             f"loudnorm=I={sb.get('loudness', -14)}:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false,aresample=48000[aout]")
    script = (vdir / "drafts" if a.draft else vdir) / f"{fmt}-graph.txt"
    script.write_text(";\n".join(g))
    crf = {"landscape": 19, "vertical": 20}[fmt]
    maxrate = {"landscape": "14M", "vertical": "10M"}[fmt] if not sb.get("maxrate") else sb["maxrate"]
    venc = (["-preset", "veryfast", "-crf", "27"] if a.draft else
            ["-preset", "slow", "-crf", str(sb.get("crf", crf)), "-maxrate", maxrate, "-bufsize", "20M"])
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-y", *inputs, "-filter_complex_script", str(script), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", *venc, "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(int(round(fps * 2))),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
           "-metadata", f"title={meta.get('title', '')} ({fmt}, {v})", "-t", f"{total:.4f}", str(out)]
    run(cmd)
    _loudness_trim(out, float(sb.get("loudness", -14)))
    if not a.draft:
        shutil.copy(pr.p("storyboards", f"{fmt}.json"), vdir / f"{fmt}-storyboard.json")
        (vdir / f"{fmt}.edl").write_text(build_edl(sb, shots_t, fps, man, base))
        rep = rj(vdir / "render.json", {})
        rep[fmt] = {"file": out.name, "fps": fps, "size": [W, H], "duration": round(total, 3), "shots": n,
                    "captions_events": nev, "music": music_report, "rendered": now(), "renderer": RENDERER}
        wj(vdir / "render.json", rep)
        pr.log("render", {"version": v, "format": fmt, "file": out.name})
    mb = out.stat().st_size / 1e6
    print(f"{out}  {total:.2f}s  {mb:.1f} MB")
    if mb > 95:
        print("warning: over 95 MB, GitHub rejects files over 100 MB: raise crf in the storyboard (\"crf\": 22) or set \"maxrate\"")
