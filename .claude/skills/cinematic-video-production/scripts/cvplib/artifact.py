"""The project's navigable visual artifact: local HTML built only from cached data (no model tokens)."""
import html, json
from pathlib import Path
from .common import active_project, rj, fmt_t, now

CSS = """
:root{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--card:#fff;--line:#e2e0da;--acc:#b8860b}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#ecebe8;--mut:#9a988f;--card:#1e1e1e;--line:#2e2e2e;--acc:#ffd60a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,-apple-system,Segoe UI,Inter,sans-serif}
main{max-width:1200px;margin:0 auto;padding:16px}h1{font-size:24px;margin:8px 0}h2{margin:28px 0 8px;font-size:19px;border-bottom:1px solid var(--line);padding-bottom:4px}
nav{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);display:flex;gap:12px;flex-wrap:wrap;z-index:2}
nav a{color:var(--fg);text-decoration:none;font-weight:600;font-size:14px}a{color:var(--acc)}
.mut{color:var(--mut);font-size:13px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px;overflow:hidden}
.strip{display:flex;gap:4px;overflow-x:auto}.strip img{height:90px;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:13.5px;display:block;overflow-x:auto}td,th{border-bottom:1px solid var(--line);padding:6px;text-align:left;vertical-align:top}
th{font-size:12px;text-transform:uppercase;color:var(--mut)}td img{height:70px;border-radius:4px}.score{font-weight:700;font-size:16px}
.tag{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:0 7px;font-size:12px;margin:1px}
.thumbs{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}.thumbs figure{margin:0}.thumbs img{width:100%;border-radius:4px}
figcaption{font-size:12px;color:var(--mut)}
"""


def _e(x):
    return html.escape(str(x if x is not None else ""))


def _page(title, body):
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{_e(title)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>")


def _sb_table(sb, thumbs):
    if not sb:
        return "<p class='mut'>Not storyboarded yet.</p>"
    rows = "".join(
        f"<tr><td>{_e(s['id'])}</td><td>{fmt_t(s.get('t_start', 0))}<br>{fmt_t(s.get('t_end', 0))}</td>"
        f"<td><img loading='lazy' src='{thumbs(s['clip'], s.get('in', 0))}'></td><td>{_e(s['clip'])}<br>"
        f"<span class='mut'>{'' if s.get('kind') == 'photo' else str(s.get('in')) + '–' + str(s.get('out'))}</span></td>"
        f"<td>{_e(s.get('dialogue', ''))}</td><td>{_e('; '.join(o['text'] for o in s.get('overlay', [])))}</td>"
        f"<td>{_e(s.get('music_cue', ''))}</td><td>{_e(', '.join(Path(x['file']).stem for x in s.get('sfx', [])))}</td>"
        f"<td>{_e(s.get('transition', 'cut'))}</td><td>{_e(s.get('framing', ''))} z{s.get('zoom', 1)}→{s.get('zoom_to', s.get('zoom', 1))}</td>"
        f"<td>{_e(s.get('purpose', ''))}</td></tr>" for s in sb["shots"])
    return (f"<p class='mut'>{len(sb['shots'])} shots · {sb.get('duration', 0):.1f}s · music: {_e((sb.get('music') or {}).get('track', 'none'))}</p>"
            "<table><tr><th>#</th><th>time</th><th>frame</th><th>source</th><th>dialogue</th><th>overlay</th><th>music</th><th>sfx</th>"
            f"<th>transition</th><th>framing</th><th>purpose</th></tr>{rows}</table>")


def cmd_artifact(a):
    pr = active_project(a.project)
    meta, man = pr.meta(), pr.manifest()
    ann = rj(pr.p("annotations.json"), {})
    out = pr.p("artifact")
    (out / "clips").mkdir(parents=True, exist_ok=True)
    idx = {mid: rj(pr.idx(mid) / "index.json", {}) for mid in man["media"]}

    def thumb(mid, t=0, rel="../"):
        th = idx.get(mid, {}).get("thumbs", [])
        if not th:
            return ""
        best = min(th, key=lambda x: abs(x["t"] - (t or 0)))
        return f"{rel}index/{mid}/{best['file']}"

    live = [e for e in man["media"].values() if e.get("status") != "removed"]
    body = [f"<h1>{_e(meta.get('title'))}</h1><p class='mut'>{_e(pr.ref)} · built {now()} · {len(live)} media items · "
            f"source {_e((meta.get('source') or {}).get('type'))} · current version {_e(meta.get('current_version'))}</p>",
            "<nav><a href='#inv'>Inventory</a><a href='#lines'>Best lines</a><a href='#hooks'>Hooks</a><a href='#sbl'>Landscape</a>"
            "<a href='#sbv'>Vertical</a><a href='#music'>Music</a><a href='#ver'>Versions</a><a href='#log'>Scans</a></nav>"]
    # inventory
    cards = []
    for e in sorted(live, key=lambda x: x.get("path", "")):
        ix = idx.get(e["id"], {})
        p = ix.get("probe", {})
        v = p.get("video", p)
        an = ann.get(e["id"], {})
        strip = "".join(f"<img loading='lazy' src='../index/{e['id']}/{t['file']}' title='{fmt_t(t['t'])}'>" for t in ix.get("thumbs", [])[:8])
        cards.append(f"<div class='card'><b><a href='clips/{e['id']}.html'>{_e(e['id'])}</a></b> <span class='mut'>{_e(e.get('path'))}</span>"
                     f"<div class='strip'>{strip}</div><div class='mut'>{_e(e['kind'])} · {p.get('duration', 0):.1f}s · {v.get('w', '?')}x{v.get('h', '?')}"
                     f" · {v.get('fps', '')}fps · scenes {len(ix.get('scenes', []))}</div>"
                     f"<div>{_e(an.get('summary', ''))}</div>"
                     + "".join(f"<span class='tag'>{_e(x)}</span>" for x in an.get("use", [])) + "</div>")
        # per-clip page
        tr = rj(pr.idx(e["id"]) / "transcript.json")
        figs = "".join(f"<figure><img loading='lazy' src='../../index/{e['id']}/{t['file']}'><figcaption>{fmt_t(t['t'])} · {t['why']}</figcaption></figure>"
                       for t in ix.get("thumbs", []))
        shots = "".join(f"<tr><td>{_e(s.get('t'))}</td><td>{_e(s.get('shot'))}</td><td>{_e(s.get('action'))}</td><td>{_e(s.get('speaker', 'unknown'))}</td>"
                        f"<td>{_e(s.get('dialogue'))}</td><td>{_e(s.get('emotion'))}</td><td>{_e(s.get('quality'))}</td><td>{_e(s.get('use'))}</td></tr>"
                        for s in an.get("shots", []))
        trh = "".join(f"<tr><td>{s['s']:.2f}–{s['e']:.2f}</td><td>{_e(s['text'])}</td></tr>" for s in (tr or {}).get("segments", []))
        cp = (f"<p><a href='../index.html'>← project</a></p><h1>{_e(e['id'])} · {_e(e['name'])}</h1>"
              f"<p class='mut'>path {_e(e.get('path'))} · sha256 {_e((e.get('sha256') or '')[:16])}… · source id {_e(e['source_id'])}"
              f" · modified {_e(e.get('modified'))}</p><p class='mut'>probe {_e(json.dumps(p))}</p>"
              f"<p class='mut'>quality {_e(json.dumps({k: v2 for k, v2 in ix.get('quality', {}).items() if k != 'audio'}))}</p>"
              f"<p>Frame index (every decoded frame: n, pts, scene score, luma, saturation): <a href='../../index/{e['id']}/frames.jsonl.gz'>frames.jsonl.gz</a>"
              f" · <a href='../../index/{e['id']}/contact.jpg'>contact sheet</a></p>"
              f"<p class='mut'>Semantic notes cover {_e(an.get('coverage', 'not annotated yet'))}; frame metadata is exhaustive.</p>"
              f"<h2>Annotated moments</h2><table><tr><th>t</th><th>shot</th><th>action</th><th>speaker</th><th>dialogue</th><th>emotion</th><th>quality</th><th>use</th></tr>{shots}</table>"
              f"<h2>Thumbnails</h2><div class='thumbs'>{figs}</div><h2>Transcript</h2><p class='mut'>machine transcript, verify names</p><table>{trh}</table>")
        (out / "clips" / f"{e['id']}.html").write_text(_page(e["name"], cp))
    body.append(f"<h2 id='inv'>Inventory</h2><div class='grid'>{''.join(cards)}</div>")
    # best lines / trainer moments / reactions / b-roll from annotations
    rows = []
    for mid, an in ann.items():
        for bl in an.get("best_lines", []):
            rows.append(f"<tr><td><img loading='lazy' src='{thumb(mid, bl.get('t', 0))}'></td><td>{_e(mid)} {bl.get('t', '')}</td>"
                        f"<td>{_e(bl.get('speaker', 'unknown'))}</td><td>“{_e(bl.get('quote'))}”</td><td>{_e(bl.get('type', ''))}</td><td>{_e(bl.get('note', ''))}</td></tr>")
    body.append("<h2 id='lines'>Best lines, trainer moments, reactions, B-roll</h2>"
                + (f"<table><tr><th></th><th>source</th><th>speaker</th><th>quote / moment</th><th>type</th><th>note</th></tr>{''.join(rows)}</table>" if rows else "<p class='mut'>No annotations yet.</p>"))
    # hooks
    hk = rj(pr.p("hooks.json"), {}).get("hooks", [])
    hrows = "".join(f"<tr><td class='score'>{h['score']:.1f}</td><td><img loading='lazy' src='../{h.get('thumb', '')}'></td><td>{_e(h['clip'])}<br>{h['in']:.2f}–{h['out']:.2f}</td>"
                    f"<td>{_e(h.get('speaker', 'unknown'))}</td><td>{_e(h.get('quote') or h.get('action'))}</td><td>{_e(h.get('overlay', ''))}</td>"
                    f"<td class='mut'>{' '.join(f'{k[:4]} {v}' for k, v in h['scores'].items())}</td><td>{_e(h.get('why', ''))}</td><td>{_e(', '.join(h.get('selected_for', [])))}</td></tr>" for h in hk)
    body.append("<h2 id='hooks'>Hook rankings</h2><p class='mut'>Equal weights: attention, curiosity, emotion, clarity, shareability, audiovisual impact. Editorial estimates, not predictions.</p>"
                + (f"<table><tr><th>/10</th><th></th><th>source</th><th>speaker</th><th>quote / action</th><th>overlay</th><th>scores</th><th>why</th><th>used in</th></tr>{hrows}</table>" if hk else "<p class='mut'>No hooks scored yet.</p>"))
    body.append(f"<h2 id='sbl'>Landscape storyboard (16:9)</h2>{_sb_table(rj(pr.p('storyboards', 'landscape.json')), lambda m, t: thumb(m, t))}")
    body.append(f"<h2 id='sbv'>Vertical storyboard (9:16)</h2>{_sb_table(rj(pr.p('storyboards', 'vertical.json')), lambda m, t: thumb(m, t))}")
    # music
    mrows = []
    for tj in sorted(pr.p("music").glob("*/track.json")):
        t = rj(tj)
        bm = rj(tj.parent / "beats.json", {})
        eb = bm.get("bar_energy_db", [])
        secs = ", ".join("%s %ss" % (x["type"], x["t"]) for x in bm.get("sections", []))
        svg = ""
        if eb:
            lo, hi = min(eb), max(eb)
            pts = " ".join(f"{i * 600 / max(1, len(eb) - 1):.1f},{50 - 45 * (x - lo) / max(1e-6, hi - lo):.1f}" for i, x in enumerate(eb))
            svg = f"<svg viewBox='0 0 600 55' width='100%' height='55'><polyline fill='none' stroke='currentColor' stroke-width='1.5' points='{pts}'/></svg>"
        mrows.append(f"<div class='card'><b>{_e(t.get('title'))}</b> <span class='mut'>{_e(t.get('artist'))} · {_e(t.get('source'))}</span><br>"
                     f"license: <b>{_e(t.get('license'))}</b> {'✓ verified' if t.get('license_verified') else '⚠ not verified'}<br>"
                     f"{bm.get('bpm', '?')} BPM · {len(bm.get('beats', []))} beats · {bm.get('duration', '?')}s<br>{svg}"
                     f"<div class='mut'>{_e(secs)}</div></div>")
    mrec = rj(pr.p("music", "recommendations.json"))
    rec = ""
    if mrec:
        rec = "<ol>" + "".join(f"<li><b>{_e(r.get('title'))}</b> — {_e(r.get('why'))} <span class='mut'>{_e(r.get('license'))}</span></li>" for r in mrec.get("ranked", [])) + "</ol>"
    body.append(f"<h2 id='music'>Music and beat maps</h2>{rec}<div class='grid'>{''.join(mrows) or '<p class=mut>No tracks yet.</p>'}</div>")
    # versions
    vrows = []
    for vd in sorted(pr.p("versions").glob("v*"), reverse=True):
        rep, qc = rj(vd / "render.json", {}), rj(vd / "qc.json", {})
        for fmt, r in rep.items():
            q = qc.get(fmt, {})
            vrows.append(f"<tr><td>{vd.name}</td><td>{fmt}</td><td><a href='../versions/{vd.name}/{r['file']}'>{_e(r['file'])}</a></td>"
                         f"<td>{r['duration']}s</td><td>{q.get('lufs', '')} LUFS</td><td>{_e('; '.join(q.get('issues', [])) or ('OK' if q else 'not QCed'))}</td></tr>")
    body.append("<h2 id='ver'>Versions</h2>" + (f"<table><tr><th>version</th><th>format</th><th>file</th><th>length</th><th>loudness</th><th>QC</th></tr>{''.join(vrows)}</table>" if vrows else "<p class='mut'>No renders yet.</p>"))
    srows = "".join(f"<tr><td>{_e(s['time'])}</td><td>{_e(s['source'])}</td><td>{_e(json.dumps(s['summary']))}</td></tr>" for s in reversed(man.get("scans", [])))
    body.append(f"<h2 id='log'>Scans and Dig log</h2><table>{srows}</table><p class='mut'>Manifest: <a href='../manifest.json'>manifest.json</a></p>")
    (out / "index.html").write_text(_page(meta.get("title", "Project"), "".join(body)))
    print(out / "index.html")
