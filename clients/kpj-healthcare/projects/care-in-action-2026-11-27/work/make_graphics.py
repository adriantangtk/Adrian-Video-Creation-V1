"""Beat-synced infographic compositions (HyperFrames HTML + GSAP) for KPJ C.A.R.E in Action.
Facts used: C.A.R.E words (confirmed by owner); session titles/questions as shown on the event screens."""
import json, os, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/user/Adrian-Video-Creation-V1")
B = 60 / 124  # beat
GOLD, CREAM, INK = "#D4B07A", "#F4EBDD", "#14100C"

PROGRAMME = [("01", "Reflection Mirror", "What happened? What will we do differently?"),
             ("02", "Team Identity", "Your team needs an identity"),
             ("03", "Tribe of C.A.R.E. &amp; Service Anthem", "Represent your value. Perform the anthem.")]
MIRROR = ["What happened?", "What did others experience?", "What will we do differently?"]
CARE = [("C", "Committed"), ("A", "Accountable"), ("R", "Respectful"), ("E", "Excellent")]

BASE_CSS = """
@font-face { font-family: Inter; font-weight: 400; src: url(fonts/inter-latin-400-normal.woff2) format("woff2"); }
@font-face { font-family: Inter; font-weight: 600; src: url(fonts/inter-latin-600-normal.woff2) format("woff2"); }
@font-face { font-family: Inter; font-weight: 700; src: url(fonts/inter-latin-700-normal.woff2) format("woff2"); }
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:%(W)spx; height:%(H)spx; overflow:hidden; background:%(INK)s; }
#root { position:relative; width:100%%; height:100%%; font-family: Inter, sans-serif; color:#fff; }
#bg { position:absolute; inset:-40px; background:url(bg.jpg) center/cover; }
#shade { position:absolute; inset:0; background: radial-gradient(ellipse at 50%% 45%%, rgba(20,16,12,.45), rgba(20,16,12,.88)); }
.kicker { position:absolute; color:%(GOLD)s; font-weight:600; letter-spacing:.32em; text-transform:uppercase; }
.title { position:absolute; font-weight:700; letter-spacing:-.01em; line-height:1.05; }
.gold { color:%(GOLD)s; }
.rule { position:absolute; background:%(GOLD)s; transform-origin:left center; }
"""


def page(W, H, dur, css, body, js):
    head = (f'<!doctype html>\n<html lang="en" data-resolution="{"portrait" if H > W else "landscape"}">\n<head>\n<meta charset="UTF-8" />\n'
            f'<meta name="viewport" content="width={W}, height={H}" />\n<script src="vendor/gsap.min.js"></script>\n<style>\n'
            + BASE_CSS % {"W": W, "H": H, "INK": INK, "GOLD": GOLD} + css + "\n</style>\n</head>\n<body>\n")
    root = (f'<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-fps="30" data-width="{W}" data-height="{H}">\n'
            + body + "\n</div>\n")
    script = ("<script>\n  const tl = gsap.timeline({ paused: true });\n  const B = %.6f;\n" % B
              + "  tl.fromTo('#bg', {scale:1.0}, {scale:1.06, duration:%.3f, ease:'none'}, 0);\n" % dur
              + js + "\n  window.__timelines = window.__timelines || {};\n  window.__timelines['main'] = tl;\n  tl.seek(0);\n</script>\n</body>\n</html>\n")
    return head + root + script


def clip(i, dur, inner):
    attrs = f'data-start="0" data-duration="{dur:.3f}" data-track-index="{i}"'
    if ' class="' in inner.split("CLIPATTR")[0]:
        head, tail = inner.split("CLIPATTR", 1)
        head = head.replace(' class="', ' class="clip ', 1)
        return head + attrs + tail
    return inner.replace("CLIPATTR", 'class="clip" ' + attrs, 1)


def programme(W, H):
    beats = 12; dur = beats * B + 0.5; vert = H > W
    css = f"""
#k {{ left:{80 if not vert else 70}px; top:{110 if not vert else 280}px; font-size:{26 if not vert else 30}px; width:{1700 if not vert else 900}px; line-height:1.5; }}
#t {{ left:{80 if not vert else 70}px; top:{160 if not vert else 400}px; font-size:{92 if not vert else 104}px; }}
#line {{ left:{180 if not vert else 132}px; top:{560 if not vert else 640}px; width:{1560 if not vert else 6}px; height:{6 if not vert else 900}px; transform-origin:{'left center' if not vert else 'center top'}; }}
.node {{ position:absolute; width:{110 if not vert else 120}px; height:{110 if not vert else 120}px; border-radius:50%; background:{INK}; border:5px solid {GOLD};
  color:{GOLD}; font-weight:700; font-size:{40 if not vert else 44}px; display:flex; align-items:center; justify-content:center; }}
.card {{ position:absolute; width:{480 if not vert else 740}px; }}
.card h3 {{ font-size:{44 if not vert else 52}px; font-weight:700; line-height:1.1; }}
.card p {{ margin-top:14px; font-size:{28 if not vert else 34}px; color:{CREAM}; opacity:.85; line-height:1.3; }}
"""
    body = [clip(0, dur, '<div id="bg" CLIPATTR></div>'), clip(1, dur, '<div id="shade" CLIPATTR></div>'),
            clip(2, dur, '<div id="k" class="kicker" CLIPATTR>KPJ Healthcare Teambuilding · 27.11.2026</div>'),
            clip(3, dur, '<div id="t" class="title" CLIPATTR>The <span class="gold">Programme</span></div>'),
            clip(4, dur, '<div id="line" class="rule" CLIPATTR></div>')]
    js = ["  tl.from('#k', {opacity:0, y:20, duration:.35, ease:'power2.out'}, 0.05);",
          "  tl.from('#t', {opacity:0, y:40, duration:.45, ease:'expo.out'}, B*1);",
          f"  tl.from('#line', {{{'scaleX' if not vert else 'scaleY'}:0, duration:B*2, ease:'power2.inOut'}}, B*2);"]
    for i, (n, h, p) in enumerate(PROGRAMME):
        if not vert:
            nx, ny = 180 + i * 560 - 52, 560 - 52 + 3
            cx, cy = 180 + i * 560 - 52, 700
        else:
            nx, ny = 132 - 57, 640 + i * 330
            cx, cy = 230, 640 + i * 330 - 4
        body.append(clip(5 + 2 * i, dur, f'<div id="n{i}" class="node" style="left:{nx}px;top:{ny}px" CLIPATTR>{n}</div>'))
        body.append(clip(6 + 2 * i, dur, f'<div id="c{i}" class="card" style="left:{cx}px;top:{cy}px" CLIPATTR><h3>{h}</h3><p>{p}</p></div>'))
        t = 3 + 2 * i
        js.append(f"  tl.from('#n{i}', {{scale:0, duration:.32, ease:'back.out(2.2)'}}, B*{t});")
        js.append(f"  tl.from('#c{i}', {{opacity:0, {'y' if not vert else 'x'}:30, duration:.4, ease:'power3.out'}}, B*{t} + .08);")
    return dur, page(W, H, dur, css, "\n".join(body), "\n".join(js))


def mirror(W, H):
    beats = 12; dur = beats * B + 0.5; vert = H > W
    css = f"""
#k {{ left:{120 if not vert else 70}px; top:{190 if not vert else 420}px; font-size:{26 if not vert else 30}px; }}
#t {{ left:{120 if not vert else 70}px; top:{240 if not vert else 480}px; font-size:{88 if not vert else 96}px; }}
.q {{ position:absolute; left:{120 if not vert else 70}px; display:flex; align-items:center; gap:{36 if not vert else 30}px; }}
.q b {{ color:{GOLD}; font-size:{64 if not vert else 68}px; font-weight:700; width:{110 if not vert else 110}px; }}
.q span {{ font-size:{58 if not vert else 56}px; font-weight:600; line-height:1.15; max-width:{1500 if not vert else 800}px; }}
.qbar {{ position:absolute; left:{120 if not vert else 70}px; height:3px; width:{1680 if not vert else 940}px; background:rgba(212,176,122,.35); transform-origin:left center; }}
"""
    body = [clip(0, dur, '<div id="bg" CLIPATTR></div>'), clip(1, dur, '<div id="shade" CLIPATTR></div>'),
            clip(2, dur, '<div id="k" class="kicker" CLIPATTR>Accountable</div>'),
            clip(3, dur, '<div id="t" class="title" CLIPATTR>The Reflection <span class="gold">Mirror</span></div>')]
    js = ["  tl.from('#k', {opacity:0, y:20, duration:.35, ease:'power2.out'}, 0.05);",
          "  tl.from('#t', {opacity:0, y:40, duration:.45, ease:'expo.out'}, B*1);"]
    for i, q in enumerate(MIRROR):
        y = (450 + i * 170) if not vert else (760 + i * 250)
        body.append(clip(4 + 2 * i, dur, f'<div id="qb{i}" class="qbar" style="top:{y - 30}px" CLIPATTR></div>'))
        body.append(clip(5 + 2 * i, dur, f'<div id="q{i}" class="q" style="top:{y}px" CLIPATTR><b>0{i + 1}</b><span>{q}</span></div>'))
        t = 3 + 2 * i
        js.append(f"  tl.from('#qb{i}', {{scaleX:0, duration:B, ease:'power2.out'}}, B*{t} - .1);")
        js.append(f"  tl.from('#q{i}', {{opacity:0, x:-40, duration:.4, ease:'power3.out'}}, B*{t});")
    return dur, page(W, H, dur, css, "\n".join(body), "\n".join(js))


def care(W, H):
    beats = 8; dur = beats * B + 0.5; vert = H > W
    css = f"""
.L {{ position:absolute; font-weight:700; color:{GOLD}; font-size:{260 if not vert else 230}px; line-height:1; text-align:center; }}
.Wd {{ position:absolute; font-weight:600; color:#fff; font-size:{44 if not vert else 64}px; letter-spacing:.04em; }}
#k {{ left:0; width:100%; text-align:center; top:{170 if not vert else 300}px; font-size:{28 if not vert else 32}px; }}
#u {{ left:{240 if not vert else 120}px; top:{760 if not vert else 1520}px; width:{1440 if not vert else 840}px; height:6px; }}
"""
    body = [clip(0, dur, '<div id="bg" CLIPATTR></div>'), clip(1, dur, '<div id="shade" CLIPATTR></div>'),
            clip(2, dur, '<div id="k" class="kicker" CLIPATTR>Our values in action</div>')]
    js = ["  tl.from('#k', {opacity:0, y:20, duration:.3, ease:'power2.out'}, 0.02);"]
    for i, (l, w) in enumerate(CARE):
        if not vert:
            x = 240 + i * 360; lx, ly, wx, wy, ww = x, 330, x, 640, 360
            lstyle = f"left:{lx}px;top:{ly}px;width:360px"
            wstyle = f"left:{wx}px;top:{wy}px;width:{ww}px;text-align:center"
        else:
            y = 420 + i * 270
            lstyle = f"left:120px;top:{y}px;width:220px"
            wstyle = f"left:380px;top:{y + 80}px;width:600px"
        body.append(clip(3 + 2 * i, dur, f'<div id="l{i}" class="L" style="{lstyle}" CLIPATTR>{l}</div>'))
        body.append(clip(4 + 2 * i, dur, f'<div id="w{i}" class="Wd" style="{wstyle}" CLIPATTR>{w}</div>'))
        js.append(f"  tl.from('#l{i}', {{scale:1.8, opacity:0, duration:.28, ease:'expo.out'}}, B*{i});")
        js.append(f"  tl.from('#w{i}', {{opacity:0, y:24, duration:.35, ease:'power3.out'}}, B*{4 + i * 0.5});")
    body.append(clip(11, dur, '<div id="u" class="rule" CLIPATTR></div>'))
    js.append("  tl.from('#u', {scaleX:0, duration:B*1.5, ease:'power2.inOut'}, B*6);")
    return dur, page(W, H, dur, css, "\n".join(body), "\n".join(js))


if __name__ == "__main__":
    out = []
    for name, fn in (("programme", programme), ("mirror", mirror), ("care", care)):
        for fmt, (W, H) in (("landscape", (1920, 1080)), ("vertical", (1080, 1920))):
            d = ROOT / "graphics" / f"{name}-{fmt}"
            (d / "vendor").mkdir(parents=True, exist_ok=True)
            (d / "fonts").mkdir(exist_ok=True)
            shutil.copy(REPO / "kit/vendor/gsap.min.js", d / "vendor/gsap.min.js")
            for wgt in (400, 600, 700):
                shutil.copy(REPO / f"kit/fonts/inter-latin-{wgt}-normal.woff2", d / "fonts")
            shutil.copy(ROOT / "graphics" / f"bg-{name}-{fmt}.jpg", d / "bg.jpg")
            for f in ("hyperframes.json",):
                shutil.copy(REPO / "projects/example-reel" / f, d / f)
            (d / "meta.json").write_text(json.dumps({"id": f"kpj-{name}-{fmt}", "name": f"kpj-{name}-{fmt}"}))
            dur, html = fn(W, H)
            (d / "index.html").write_text(html)
            out.append((str(d), round(dur, 3)))
    for d, dur in out:
        print(dur, d)
