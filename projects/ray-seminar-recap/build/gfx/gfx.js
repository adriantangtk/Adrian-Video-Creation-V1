/* ray-seminar-recap graphics kit (GSAP 3). Load after vendor/gsap.min.js, before your timeline script.
   Usage:  const tl = gsap.timeline({ paused: true }); GFX.use(tl); ...calls...; window.__timelines["main"] = tl;
   Every function is deterministic (a pure function of timeline time). See README.md. */
(function () {
  let tl = null, uid = 0;
  const $ = s => (typeof s === "string" ? document.querySelector(s) : s);
  const T = () => { if (!tl) throw new Error("GFX.use(tl) first"); return tl; };

  // ---------- 1. captions ----------
  // Split whisper words [{w|text, start, end}] into 2-3 word groups: break at max words, sentence end,
  // or a pause >= gap s. keywords: array of words (case-insensitive, punctuation ignored) to highlight red.
  function chunkWords(words, opt = {}) {
    const max = opt.max || 3, gap = opt.gap ?? 0.15, kw = (opt.keywords || []).map(norm);
    const groups = []; let cur = [];
    const flush = () => { if (cur.length) groups.push(cur); cur = []; };
    words.forEach((x, i) => {
      const w = { w: (x.w ?? x.text ?? x.word).trim(), start: +x.start, end: +x.end };
      if (!w.w) return;
      const prev = cur[cur.length - 1];
      if (prev && (w.start - prev.end >= gap)) flush();
      cur.push(w);
      if (cur.length >= max || /[.!?,;:]$/.test(w.w)) flush();
    });
    flush();
    return groups.map(g => ({
      words: g.map(x => x.w), starts: g.map(x => x.start), end: g[g.length - 1].end,
      keywordIndex: g.findIndex(x => kw.includes(norm(x.w))),
    }));
  }
  const norm = s => String(s).toLowerCase().replace(/[^a-z0-9'-]/g, "");

  // One caption chunk. words[] + startTimes[] (absolute s). keywordIndex -1 = none.
  // opt: { host:"#gfx-captions", end:<abs s, default last start+0.6>, size:<px auto>, style:"shadow"|"pill", y:1190 }
  function captionPill(words, startTimes, keywordIndex, t0, opt = {}) {
    const tl = T(), host = $(opt.host || "#gfx-captions");
    const g = document.createElement("div");
    g.className = "cap-group" + (opt.style === "pill" ? " pill" : "");
    g.id = "cap-" + (++uid);
    if (opt.y != null) g.style.top = opt.y + "px";
    const chars = words.join(" ").length + (keywordIndex >= 0 ? 3 : 0);
    const size = opt.size || Math.max(54, Math.min(88, Math.floor(880 / (chars * 0.56))));
    g.style.fontSize = size + "px";
    const els = words.map((w, i) => {
      const s = document.createElement("span");
      s.className = "cap-w" + (i === keywordIndex ? " key" : "");
      s.textContent = w; g.appendChild(s); return s;
    });
    host.appendChild(g);
    const start = Math.min(t0, startTimes[0]) - 0.04;
    const end = opt.end ?? (startTimes[startTimes.length - 1] + 0.6);
    tl.set(g, { opacity: 1, visibility: "visible" }, start);
    els.forEach((s, i) => {
      const at = Math.max(start, startTimes[i] - 0.03), key = i === keywordIndex;
      tl.fromTo(s, { opacity: 0, y: 26, scale: key ? 0.7 : 0.86 },
        { opacity: 1, y: 0, scale: 1, duration: key ? 0.26 : 0.2, ease: key ? "back.out(2.4)" : "back.out(1.7)", immediateRender: false }, at);
    });
    tl.to(g, { opacity: 0, y: -10, duration: 0.1, ease: "power2.in" }, end - 0.1);
    tl.set(g, { opacity: 0, visibility: "hidden" }, end);
    return g;
  }

  // Caption a whole soundbite from whisper words. offset shifts word times onto the main timeline.
  // Each group holds until the next group starts (max hold 1.2 s after its last word).
  function captionsFromWords(words, opt = {}) {
    const off = opt.offset || 0;
    const groups = chunkWords(words, opt);
    return groups.map((g, i) => {
      const next = groups[i + 1];
      const hold = Math.min(g.end + (opt.hold ?? 0.35), g.starts[g.starts.length - 1] + 1.2);
      let end = next ? Math.min(next.starts[0] - 0.05, hold + 0.6) : hold;
      end = Math.max(end, g.starts[g.starts.length - 1] + 0.3);
      if (next) end = Math.min(end, next.starts[0] - 0.02);   // never two groups on screen
      return captionPill(g.words, g.starts.map(s => s + off), g.keywordIndex, g.starts[0] + off, { ...opt, end: end + off });
    });
  }

  // ---------- 2. hook title ----------
  // DOM: #gfx-hook > .hook-kicker, .hook-rule, .hook-sub (sub optional). Text set from opt if given.
  function hookTitle(t0, dur, opt = {}) {
    const tl = T(), root = $(opt.root || "#gfx-hook");
    const k = root.querySelector(".hook-kicker"), r = root.querySelector(".hook-rule"), s = root.querySelector(".hook-sub");
    if (opt.kicker) k.textContent = opt.kicker;
    if (opt.sub != null && s) s.innerHTML = opt.sub;
    tl.set(root, { opacity: 1 }, 0);
    tl.fromTo(k, { opacity: 0, y: 18, letterSpacing: "0.5em" }, { opacity: 1, y: 0, letterSpacing: "0.28em", duration: 0.7, ease: "expo.out", immediateRender: true }, t0);
    tl.fromTo(r, { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "expo.inOut", immediateRender: true }, t0 + 0.18);
    if (s) tl.fromTo(s, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", immediateRender: true }, t0 + 0.45);
    tl.to([k, r, s].filter(Boolean), { opacity: 0, y: -14, duration: 0.25, ease: "power2.in", stagger: 0.04 }, t0 + dur - 0.3);
  }

  // ---------- 3. transitions (operate on any element: <video>, <img>, wrapper div) ----------
  function blurFilter(el) {           // per-element horizontal SVG motion blur
    let svg = document.getElementById("gfx-defs");
    if (!svg) {
      svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.id = "gfx-defs"; svg.setAttribute("width", "0"); svg.setAttribute("height", "0");
      svg.style.position = "absolute"; document.body.appendChild(svg);
    }
    const f = document.createElementNS("http://www.w3.org/2000/svg", "filter"), id = "gfx-mb-" + (++uid);
    f.id = id; f.setAttribute("x", "-20%"); f.setAttribute("width", "140%");
    f.setAttribute("color-interpolation-filters", "sRGB");
    const b = document.createElementNS("http://www.w3.org/2000/svg", "feGaussianBlur");
    b.setAttribute("stdDeviation", "0 0"); f.appendChild(b); svg.appendChild(f);
    return { id, blur: b };
  }
  const DIRS = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] };

  // Element whips IN: from offset + motion blur + slight rotation to rest. dir = side it comes FROM.
  function whipIn(el, t, dir = "right", opt = {}) {
    const tl = T(); el = $(el);
    const dur = opt.dur || 0.16, dist = opt.dist || 380, [dx, dy] = DIRS[dir];
    const { id, blur } = blurFilter(el), amt = opt.blur || 44;
    const sd = dx ? `${amt} 0` : `0 ${amt}`;
    tl.set(el, { filter: `url(#${id})` }, t);
    tl.fromTo(blur, { attr: { stdDeviation: sd } }, { attr: { stdDeviation: "0 0" }, duration: dur, ease: "power3.out", immediateRender: false }, t);
    tl.fromTo(el, { x: dx * dist, y: dy * dist, rotation: (opt.rot ?? 3.5) * (dx || dy), scale: 1.12 },
      { x: 0, y: 0, rotation: 0, scale: 1, duration: dur, ease: "power3.out", immediateRender: false }, t);
    tl.set(el, { filter: "none" }, t + dur);
  }
  // Element whips OUT toward dir, ending at t + dur (cut point).
  function whipOut(el, t, dir = "left", opt = {}) {
    const tl = T(); el = $(el);
    const dur = opt.dur || 0.14, dist = opt.dist || 520, [dx, dy] = DIRS[dir];
    const { id, blur } = blurFilter(el), amt = opt.blur || 44;
    tl.set(el, { filter: `url(#${id})` }, t);
    tl.fromTo(blur, { attr: { stdDeviation: "0 0" } }, { attr: { stdDeviation: dx ? `${amt} 0` : `0 ${amt}` }, duration: dur, ease: "power3.in", immediateRender: false }, t);
    tl.fromTo(el, { x: 0, y: 0, rotation: 0 }, { x: dx * dist, y: dy * dist, rotation: -(opt.rot ?? 3.5) * (dx || dy), scale: 1.1, duration: dur, ease: "power3.in", immediateRender: false }, t);
  }
  // Cut-on-beat whip between two shots: a whips out, b whips in; the cut lands at t.
  function whip(a, b, t, dir = "left", opt = {}) {
    const opp = { left: "right", right: "left", up: "down", down: "up" }[dir];
    if (a) whipOut(a, t - (opt.outDur || 0.08), dir, { ...opt, dur: opt.outDur || 0.08 });
    whipIn(b, t, opp, opt);
  }
  // Quick punch-in zoom on a beat (snaps in, eases back a little).
  function punchIn(el, t, opt = {}) {
    const tl = T(); el = $(el);
    const to = opt.to || 1.12, dur = opt.dur || 0.22;
    tl.fromTo(el, { scale: opt.from || 1 }, { scale: to, duration: 0.07, ease: "power4.out", immediateRender: false }, t);
    if (opt.hold !== true) tl.to(el, { scale: opt.settle || (1 + (to - 1) * 0.6), duration: dur, ease: "power2.out" }, t + 0.07);
  }
  // Flash-to-white frame centred on the cut at t.
  function flash(t, opt = {}) {
    const tl = T(), el = $(opt.el || "#gfx-flash"), peak = opt.peak ?? 1;
    tl.fromTo(el, { opacity: 0 }, { opacity: peak, duration: opt.inDur || 0.05, ease: "none", immediateRender: false }, t - (opt.inDur || 0.05));
    tl.to(el, { opacity: 0, duration: opt.outDur || 0.22, ease: "power2.out" }, t + 0.033);
  }
  // Red light-leak wipe: a skewed red bar sweeps across; screen fully red at t (cut there).
  function redWipe(t, opt = {}) {
    const tl = T(), root = $(opt.el || "#gfx-leak");
    const bar = root.querySelector(".leak-bar"), glow = root.querySelector(".leak-glow");
    const dur = opt.dur || 0.42, rtl = opt.dir === "left";
    const x0 = rtl ? 1300 : -2900, x1 = rtl ? -2900 : 1300;
    tl.set(bar, { opacity: 1, skewX: -14 }, t - dur / 2);
    tl.fromTo(bar, { x: x0 }, { x: x1, duration: dur, ease: "power2.inOut", immediateRender: false }, t - dur / 2);
    tl.set(bar, { opacity: 0 }, t + dur / 2);
    tl.fromTo(glow, { opacity: 0 }, { opacity: 1, duration: dur * 0.5, ease: "power2.out", immediateRender: false }, t - dur * 0.3);
    tl.to(glow, { opacity: 0, duration: dur * 1.2, ease: "power2.out" }, t + dur * 0.2);
  }

  // ---------- 4. Ken Burns ----------
  function kenBurns(el, t, dur, opt = {}) {
    const tl = T(); el = $(el);
    const z0 = opt.from || 1.04, z1 = opt.to || 1.16, dx = opt.x ?? 30, dy = opt.y ?? -20;
    tl.fromTo(el, { scale: z0, x: -dx / 2, y: -dy / 2, transformOrigin: opt.origin || "50% 50%" },
      { scale: z1, x: dx / 2, y: dy / 2, duration: dur, ease: opt.ease || "sine.inOut", immediateRender: false }, t);
  }

  // ---------- 5. lower third ----------
  // DOM: #gfx-lt > .lt-bar, .lt-mask.name > .lt-name, .lt-mask.tag > .lt-tag
  function lowerThird(t, dur, opt = {}) {
    const tl = T(), root = $(opt.root || "#gfx-lt");
    const bar = root.querySelector(".lt-bar"), name = root.querySelector(".lt-name"), tag = root.querySelector(".lt-tag");
    if (opt.name) name.textContent = opt.name;
    if (opt.tag) tag.textContent = opt.tag;
    tl.set([bar, name, tag], { opacity: 0 }, 0);
    tl.fromTo(bar, { scaleY: 0, opacity: 1 }, { scaleY: 1, duration: 0.4, ease: "expo.out", immediateRender: false }, t);
    tl.fromTo(name, { yPercent: 105, opacity: 1 }, { yPercent: 0, duration: 0.55, ease: "expo.out", immediateRender: false }, t + 0.1);
    tl.fromTo(tag, { xPercent: -104, opacity: 1 }, { xPercent: 0, duration: 0.55, ease: "expo.out", immediateRender: false }, t + 0.28);
    const o = t + dur - 0.35;
    tl.to(name, { yPercent: -105, duration: 0.3, ease: "power3.in" }, o);
    tl.to(tag, { xPercent: -104, duration: 0.3, ease: "power3.in" }, o + 0.04);
    tl.to(bar, { scaleY: 0, transformOrigin: "50% 100%", duration: 0.3, ease: "power3.in" }, o + 0.08);
  }

  // ---------- 6. outro card ----------
  // DOM: #gfx-outro > .out-kicker, .out-title > .out-line > span (x N), .out-rule, .out-counter, .out-handle
  function outro(t, opt = {}) {
    const tl = T(), root = $(opt.root || "#gfx-outro");
    const kick = root.querySelector(".out-kicker"), lines = [...root.querySelectorAll(".out-line > span")];
    const rule = root.querySelector(".out-rule"), ctr = root.querySelector(".out-counter"), hand = root.querySelector(".out-handle");
    const target = opt.counter || ctr.textContent.trim() || "20.11.2026";
    if (opt.handle) hand.textContent = opt.handle;
    tl.set(root, { opacity: 0 }, 0);
    tl.set(root, { opacity: 1 }, t);                        // hard cut to white
    tl.set([kick, hand], { opacity: 0 }, 0);
    tl.set(lines, { yPercent: 110 }, 0);
    tl.set(rule, { scaleX: 0 }, 0);
    lines.forEach((l, i) => tl.to(l, { yPercent: 0, duration: 0.6, ease: "expo.out" }, t + 0.12 + i * 0.2));
    tl.fromTo(kick, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out", immediateRender: false }, t + 0.1);
    const tr = t + 0.25 + lines.length * 0.2;
    tl.to(rule, { scaleX: 1, duration: 0.5, ease: "expo.inOut" }, tr);
    // counter: digits roll, then lock left-to-right
    const tc = tr + 0.15, cd = opt.counterDur || 1.1, state = { p: 0 };
    const render = p => {
      let out = "", n = 0;
      for (let i = 0; i < target.length; i++) {
        const c = target[i];
        if (!/[0-9]/.test(c)) { out += c; continue; }
        const lock = 0.35 + 0.65 * (n / 7); n++;
        out += p >= lock ? c : String((Math.floor(p * 40) * 7 + i * 3 + 1) % 10);
      }
      return out;
    };
    tl.set(ctr, { opacity: 0, textContent: render(0) }, 0);
    tl.set(ctr, { opacity: 1 }, tc);
    tl.fromTo(state, { p: 0 }, { p: 1, duration: cd, ease: "none", immediateRender: false,
      onUpdate: () => { ctr.textContent = render(state.p); } }, tc);
    tl.set(ctr, { textContent: target }, tc + cd);
    tl.fromTo(ctr, { scale: 1 }, { scale: 1.06, duration: 0.08, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, tc + cd);
    tl.fromTo(hand, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, tc + cd + 0.2);
    return { counterDone: tc + cd, handleIn: tc + cd + 0.2 };
  }

  window.GFX = { use: t => (tl = t), chunkWords, captionPill, captionsFromWords, hookTitle,
    whipIn, whipOut, whip, punchIn, flash, redWipe, kenBurns, lowerThird, outro };
})();
