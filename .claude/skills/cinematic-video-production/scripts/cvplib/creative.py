"""Persist the model's creative decisions: annotations, hook scores, storyboards (validated, beat-snapped)."""
import json
from pathlib import Path
from .common import active_project, rj, wj, run, now, die, FORMATS, fmt_t

HOOK_KEYS = ["attention", "curiosity", "emotion", "clarity", "shareability", "av_impact"]


def _load_input(path):
    return json.loads(Path(path).read_text())


def _dur(pr, mid):
    ix = rj(pr.idx(mid) / "index.json")
    if not ix:
        die(f"{mid} is not indexed")
    return ix["probe"].get("duration") or 0, ix["kind"]


def cmd_annotate(a):
    """Merge semantic annotations {media_id: {...}} written by the model."""
    pr = active_project(a.project)
    new = _load_input(a.file)
    with pr.lock():
        ann = rj(pr.p("annotations.json"), {})
        man = pr.manifest()
        for mid, v in new.items():
            if mid not in man["media"]:
                die(f"unknown media id {mid}")
            v["annotated"] = now()
            v.setdefault("coverage", "sampled thumbnails/contact sheet (semantic notes are not per-frame)")
            ann[mid] = {**ann.get(mid, {}), **v}
            man["media"][mid].setdefault("stages", {})["annotated"] = man["media"][mid].get("sha256")
        wj(pr.p("annotations.json"), ann)
        pr.save_manifest(man)
    print(f"annotations merged for {len(new)} item(s)")


def cmd_hooks(a):
    """Input: list of hooks with clip, in, out, quote|action, speaker, overlay, scores{6 keys 0-10}, why."""
    pr = active_project(a.project)
    items = _load_input(a.file)
    old = rj(pr.p("hooks.json"), {"hooks": []})
    keyed = {(h["clip"], round(h["in"], 1)): h for h in (old["hooks"] if a.merge else [])}
    th = pr.p("index", "_hooks")
    th.mkdir(parents=True, exist_ok=True)
    man = pr.manifest()
    for h in items:
        dur, kind = _dur(pr, h["clip"])
        if kind == "video" and not (0 <= h["in"] < h["out"] <= dur + 0.05):
            die(f"hook {h.get('quote') or h.get('action')}: in/out outside clip ({dur:.2f}s)")
        miss = [k for k in HOOK_KEYS if k not in h.get("scores", {})]
        if miss:
            die(f"hook missing scores {miss}")
        if not (h.get("quote") or h.get("action")):
            die("hook needs an exact quote or a visual action")
        h["score"] = round(sum(float(h["scores"][k]) for k in HOOK_KEYS) / len(HOOK_KEYS), 2)
        thumb = th / f"{h['clip']}_{int(h['in'] * 1000):07d}.jpg"
        if not thumb.exists():
            src = pr.local_file(man["media"][h["clip"]])
            run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", f"{h['in'] + 0.1:.3f}", "-i", str(src), "-frames:v", "1",
                 "-vf", "scale='if(gt(iw,ih),480,-2)':'if(gt(iw,ih),-2,480)'", "-q:v", "4", str(thumb)])
        h["thumb"] = f"index/_hooks/{thumb.name}"
        keyed[(h["clip"], round(h["in"], 1))] = h
    hooks = sorted(keyed.values(), key=lambda x: -x["score"])
    for i, h in enumerate(hooks, 1):
        h["rank"] = i
    wj(pr.p("hooks.json"), {"updated": now(), "weights": "equal across " + ", ".join(HOOK_KEYS),
                            "note": "editorial estimates, not predictions", "hooks": hooks})
    for h in hooks[:10]:
        print(f"#{h['rank']} {h['score']:.1f}  {h['clip']} {h['in']:.2f}-{h['out']:.2f}  {(h.get('quote') or h.get('action'))[:70]}")


def _snap(t, grid, tol):
    if not grid:
        return t, None
    best = min(grid, key=lambda g: abs(g - t))
    return (best, round(best - t, 3)) if abs(best - t) <= tol else (t, None)


def cmd_storyboard(a):
    """Validate a storyboard, snap cut points to the beat grid, compute the output timeline, save it."""
    pr = active_project(a.project)
    sb = _load_input(a.file)
    fmt = sb.get("format") or a.format
    if fmt not in FORMATS:
        die(f"format must be one of {list(FORMATS)}")
    sb["format"] = fmt
    man = pr.manifest()
    bm = None
    mus = sb.get("music") or {}
    if mus.get("track"):
        bm = rj(pr.p("music", mus["track"], "beats.json"))
        if not bm:
            die(f"music track {mus['track']} has no beat map (run music-add / beats)")
    grid = []
    if bm:
        off = float(mus.get("start", 0))
        grid = [b - off for b in (bm["downbeats"] if a.snap == "bar" else bm["beats"]) if b >= off]
    t, problems, trans_total = 0.0, [], 0.0
    for i, s in enumerate(sb["shots"]):
        s.setdefault("id", f"s{i + 1:02d}")
        e = man["media"].get(s["clip"])
        if not e:
            problems.append(f"{s['id']}: unknown clip {s['clip']}"); continue
        dur, kind = _dur(pr, s["clip"])
        s["kind"] = kind
        speed = float(s.get("speed", 1.0))
        if kind == "photo":
            length = float(s.get("dur", 3.0))
        else:
            if not (0 <= s["in"] < s["out"] <= dur + 0.05):
                problems.append(f"{s['id']}: in/out {s['in']}-{s['out']} outside clip length {dur:.2f}")
            length = (s["out"] - s["in"]) / speed
        td = float(s.get("transition_dur", 0.0)) if i > 0 and s.get("transition", "cut") != "cut" else 0.0
        start = t - td
        if a.snap != "none" and grid and i > 0 and not s.get("no_snap"):
            ns, delta = _snap(start, grid, a.tolerance)
            p = sb["shots"][i - 1]
            if delta is not None and p.get("kind") != "photo":
                pdur, _ = _dur(pr, p["clip"])
                if p["out"] + delta * float(p.get("speed", 1.0)) > pdur:
                    delta = None  # previous clip has no footage left to extend
            if delta is not None:
                # move the previous shot's out-point so the cut lands on the beat
                if p.get("kind") == "photo":
                    p["dur"] = round(float(p.get("dur", 3.0)) + delta, 3)
                else:
                    p["out"] = round(p["out"] + delta * float(p.get("speed", 1.0)), 3)
                t += delta
                start = ns
                s["snapped"] = delta
        s["t_start"] = round(start, 3)
        t = start + length
        s["t_end"] = round(t, 3)
        trans_total += td
    if problems:
        die("storyboard problems:\n  " + "\n  ".join(problems))
    sb["duration"] = round(t, 3)
    sb["validated"] = now()
    dest = pr.p("storyboards", f"{fmt}.json")
    if dest.exists():  # keep every storyboard revision
        hist = pr.p("storyboards", "history")
        hist.mkdir(exist_ok=True)
        dest.rename(hist / f"{fmt}-{now()[:19].replace(':', '')}.json")
    wj(dest, sb)
    print(f"{fmt} storyboard: {len(sb['shots'])} shots, {sb['duration']:.2f}s"
          + (f", {sum(1 for s in sb['shots'] if 'snapped' in s)} cuts snapped to {a.snap}" if grid else ""))
    for s in sb["shots"]:
        print(f"  {s['id']} {fmt_t(s['t_start'])}-{fmt_t(s['t_end'])} {s['clip']} "
              f"{'' if s['kind'] == 'photo' else str(s['in']) + '-' + str(s['out'])} {s.get('transition', 'cut')} {s.get('purpose', '')[:40]}")
