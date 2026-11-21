/* GFX3: RISE 2.0 cinematic title system (GSAP 3, landscape 1920x1080).
   Load after vendor/gsap.min.js:  const tl = gsap.timeline({paused:true}); GFX3.use(tl); ...calls...; window.__timelines["main"] = tl;
   All times are ABSOLUTE seconds on the main timeline. Every function only adds tweens/sets to tl (no callbacks,
   no randomness, no timers), so any frame can be seeked in any order. Elements are built once, at call time,
   inside the host divs (see README.md). */
(function () {
  let tl = null;
  const $ = s => (typeof s === "string" ? document.querySelector(s) : s);
  const T = () => { if (!tl) throw new Error("GFX3.use(tl) first"); return tl; };
  const host = (id) => { const h = $(id); if (!h) throw new Error("GFX3: missing host " + id); return h; };
  const mk = (cls, parent, html) => { const e = document.createElement("div"); e.className = cls; if (html != null) e.innerHTML = html; parent.appendChild(e); return e; };
  const FT = (el, from, to, at) => T().fromTo(el, from, { ...to, immediateRender: false }, at);
  // intentional layering (sheen over letters, masked rows over a panel): tell `hyperframes check`
  const allow = (...els) => els.forEach(e => [e, ...e.querySelectorAll("*")].forEach(x => {
    x.setAttribute("data-layout-allow-occlusion", ""); x.setAttribute("data-layout-allow-overlap", ""); x.setAttribute("data-layout-allow-overflow", ""); }));
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

  // ---------- title builder (shared by openTitle and outroTag) ----------
  // "RISE" white + " 2.0" gold, one span per char, plus a sheen duplicate (background-clip:text light sweep).
  function buildTitle(parent, o) {
    const wrap = mk("g3-big g3-title-serif", parent);
    wrap.style.top = o.top + "px"; wrap.style.fontSize = o.size + "px";
    const word = document.createElement("span"); word.className = "g3-word"; wrap.appendChild(word);
    const parts = [...o.title].map(c => [c, false]).concat(o.accent ? [[" ", false], ...[...o.accent].map(c => [c, true])] : []);
    const chars = parts.map(([c, gold]) => { const s = document.createElement("span"); s.className = "g3-ch" + (gold ? " gold" : ""); s.textContent = c === " " ? " " : c; word.appendChild(s); return s; });
    const sheen = document.createElement("span"); sheen.className = "g3-sheen";
    sheen.style.padding = "0 .06em"; sheen.style.boxSizing = "border-box";
    sheen.innerHTML = parts.map(([c]) => `<span class="g3-ch">${c === " " ? "&nbsp;" : esc(c)}</span>`).join("");
    word.appendChild(sheen); allow(wrap);
    return { wrap, word, chars, sheen };
  }
  // letters track in from the centre (x spread + fade + slight rise); returns settle time
  function trackIn(chars, t, o = {}) {
    const n = chars.length, c = (n - 1) / 2, spread = o.spread ?? 46, dur = o.dur ?? 1.4;
    chars.forEach((ch, i) => {
      const d = Math.abs(i - c);
      FT(ch, { opacity: 0, x: (i - c) * spread, y: o.rise ?? 18 }, { opacity: 1, x: 0, y: 0, duration: dur, ease: "expo.out" }, t + d * (o.stagger ?? 0.06));
    });
    return t + c * (o.stagger ?? 0.06) + dur * 0.6;
  }
  function sweep(sheen, t, dur = 1.1) {
    FT(sheen, { webkitMaskPosition: "150% 0", maskPosition: "150% 0" }, { webkitMaskPosition: "-50% 0", maskPosition: "-50% 0", duration: dur, ease: "power2.inOut" }, t);
  }

  // ---------- 1. letterbox ----------
  // Cinematic matte bars ease in at t0 and out so they are gone at t1. Bars cover y < h and y > 1080 - h
  // (2.39:1 -> h = 138): keep captions above them (captions3 {y}) while the matte is on.
  function letterbox(t0, t1, opt = {}) {
    const h = Math.round((1080 - 1920 / (opt.ratio || 2.39)) / 2), root = host(opt.host || "#g3-matte");
    const top = mk("g3-bar top", root), bot = mk("g3-bar bot", root);
    top.style.height = bot.style.height = h + "px";
    const i = opt.inDur ?? 0.9, o = opt.outDur ?? 0.7;
    T().set([top, bot], { scaleY: 0 }, 0); // hidden until t0 (several letterboxes can share the host)
    FT([top, bot], { scaleY: 0 }, { scaleY: 1, duration: i, ease: "expo.inOut" }, t0);
    if (t1 != null) FT([top, bot], { scaleY: 1 }, { scaleY: 0, duration: o, ease: "expo.inOut" }, t1 - o);
    return h;
  }

  // ---------- 2. cold-open title ----------
  // Black (or dimmed footage, opt.bg = 0..1 opacity) -> gold rule draws -> spaced kicker tracks in -> "RISE 2.0"
  // letters track in from the centre -> light sweep -> slow push; hard white flash peaks at t+dur (the impact).
  function openTitle(t, dur, opt = {}) {
    const root = host(opt.host || "#g3-open");
    const bg = mk("g3-open-bg", root), wrap = mk("g3-open-wrap", root);
    const rule = mk("g3-rule", wrap); rule.style.left = "640px"; rule.style.width = "640px"; rule.style.top = "416px";
    const kick = mk("g3-kicker", wrap); kick.textContent = opt.kicker || "HSBC IWPB WEALTH CONFERENCE 2026"; kick.style.top = "366px";
    const ti = buildTitle(wrap, { title: opt.title || "RISE", accent: opt.accent ?? "2.0", top: 450, size: opt.size || 250 });
    const tl = T(), end = t + dur;
    tl.set(bg, { opacity: opt.bg ?? 1 }, 0);
    tl.set(wrap, { opacity: 1, scale: 1 }, 0);
    FT(rule, { scaleX: 0 }, { scaleX: 1, duration: 1.1, ease: "expo.inOut" }, t + 0.15);
    FT(kick, { opacity: 0, letterSpacing: "0.9em", textIndent: "0.9em" }, { opacity: 1, letterSpacing: "0.52em", textIndent: "0.52em", duration: 1.6, ease: "expo.out" }, t + 0.55);
    const settled = trackIn(ti.chars, t + 1.15, { spread: 52, dur: 1.5 });
    tl.set(ti.sheen, { opacity: 1 }, 0);
    sweep(ti.sheen, Math.min(settled + 0.1, end - 1.2), 1.15);
    FT(wrap, { scale: 1 }, { scale: 1.035, duration: dur - 1.1, ease: "none", transformOrigin: "50% 50%" }, t + 1.1);
    if (opt.flash !== false) flash(end, { peak: 1, inDur: 0.08, outDur: 0.55 });
    tl.set([bg, wrap], { opacity: 0 }, end);
    return { settled, end };
  }

  // ---------- 3. chapter card ----------
  // Huge spaced word rises out of a mask, "01 / 03" index, red underline; holds opt.hold (1.2 s) then clears.
  // Returns the time the card is fully gone.
  function chapter(t, word, opt = {}) {
    const root = host(opt.host || "#g3-chapter");
    const scrim = mk("g3-ch-scrim", root);
    const idx = mk("g3-ch-index", root, `<b>${esc(opt.index || "01")}</b>&nbsp;&nbsp;/&nbsp;&nbsp;${esc(opt.total || "03")}`);
    const w = mk("g3-ch-word", root, `<span>${esc(word)}</span>`), span = w.firstChild;
    const line = mk("g3-ch-line", root);
    const hold = opt.hold ?? 1.2, out = t + 0.6 + hold;
    T().set([scrim, idx], { opacity: 0 }, 0);
    T().set(span, { yPercent: 105 }, 0);
    FT(scrim, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power2.out" }, t - 0.1);
    FT(span, { yPercent: 105, scale: 1.0 }, { yPercent: 0, duration: 0.75, ease: "expo.out" }, t);
    FT(span, { scale: 1 }, { scale: 1.025, duration: hold + 0.6, ease: "none" }, t);
    FT(idx, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, t + 0.15);
    FT(line, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.6, ease: "expo.inOut" }, t + 0.3);
    FT(span, { yPercent: 0 }, { yPercent: -105, duration: 0.4, ease: "power3.in" }, out);
    FT(line, { scaleX: 1, transformOrigin: "100% 50%" }, { scaleX: 0, duration: 0.35, ease: "power3.in" }, out);
    FT(idx, { opacity: 1 }, { opacity: 0, duration: 0.3, ease: "power2.in" }, out);
    FT(scrim, { opacity: 1 }, { opacity: 0, duration: 0.5, ease: "power2.inOut" }, out + 0.1);
    return out + 0.6;
  }

  // ---------- 4. luxury houses list ----------
  // Dark left panel; gold kicker + rule; one name per beat (opt.beat 0.48 s) rises from its row mask with a red
  // dash + gold index; the previous name dims. All names return to full white on the last beat; exits at t+dur.
  const HOUSES = ["LVMH", "KERING", "PRADA GROUP", "DIOR", "GUCCI", "CELINE", "TIFFANY & CO."];
  function housesList(t, dur, names, opt = {}) {
    names = names && names.length ? names : HOUSES;
    const root = host(opt.host || "#g3-houses"), beat = opt.beat ?? 0.48, step = opt.rowStep ?? 82;
    const top0 = opt.top ?? 282;
    const panel = mk("g3-h-panel", root);
    const title = mk("g3-h-title", root); title.textContent = opt.title || "15+ YEARS ACROSS";
    const rule = mk("g3-h-rule", root); allow(panel);
    const rows = names.map((n, i) => {
      const r = mk("g3-h-row", root); r.style.top = (top0 + i * step) + "px";
      const inner = mk("g3-h-in", r,
        `<div class="g3-h-num">${String(i + 1).padStart(2, "0")}</div><div class="g3-h-dash" style="width:30px;margin-right:20px"></div><div class="g3-h-name">${esc(n)}</div>`);
      allow(r); return { inner, dash: inner.children[1], name: inner.children[2] };
    });
    const tl = T(), end = t + dur, first = t + (opt.firstAt ?? beat);
    tl.set([panel, title], { opacity: 0 }, 0);
    tl.set(rows.map(r => r.inner), { yPercent: 102 }, 0);
    tl.set(rows.map(r => r.dash), { scaleX: 0, transformOrigin: "0% 50%" }, 0);
    FT(panel, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.out" }, t - 0.15);
    FT(title, { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }, t);
    FT(rule, { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "expo.inOut" }, t + 0.05);
    rows.forEach((r, i) => {
      const at = first + i * beat;
      FT(r.inner, { yPercent: 102 }, { yPercent: 0, duration: 0.5, ease: "expo.out" }, at);
      FT(r.dash, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, at + 0.05);
      if (i < rows.length - 1) {
        FT(r.dash, { scaleX: 1 }, { scaleX: 0, duration: 0.25, ease: "power2.in" }, at + beat);
        FT(r.name, { opacity: 1 }, { opacity: 0.5, duration: 0.3, ease: "power2.out" }, at + beat);
      }
    });
    const all = first + rows.length * beat;     // one beat after the last name: everything lights up
    if (all < end - 0.6) FT(rows.slice(0, -1).map(r => r.name), { opacity: 0.5 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, all);
    rows.forEach((r, i) => FT(r.inner, { yPercent: 0 }, { yPercent: -102, duration: 0.35, ease: "power3.in" }, end - 0.55 + i * 0.03));
    FT([title, panel], { opacity: 1 }, { opacity: 0, duration: 0.4, ease: "power2.in" }, end - 0.4);
    FT(rule, { scaleX: 1 }, { scaleX: 0, duration: 0.35, ease: "power3.in", transformOrigin: "100% 50%" }, end - 0.45);
    return { beats: rows.map((r, i) => first + i * beat) };   // SFX cue times (one per name)
  }

  // ---------- 5. lower third ----------
  // Red vertical rule grows, "REIN" rises, "Reinald Goh — UHNW CLIENTELING EXPERT" slides in. y 672-832 (above captions).
  function lowerThird3(t, dur, opt = {}) {
    const root = host(opt.host || "#g3-lt");
    const grad = mk("g3-lt-grad", root), bar = mk("g3-lt-bar", root);
    const nm = mk("g3-lt-name", root, `<span>${esc(opt.name || "REIN")}</span>`).firstChild;
    const sub = mk("g3-lt-sub", root, `<div><span class="g3-lt-full">${esc(opt.full || "Reinald Goh")}</span><span class="g3-lt-sep"></span><span class="g3-lt-tag">${esc(opt.tag || "UHNW Clienteling Expert")}</span></div>`).firstChild;
    const tl = T(), o = t + dur - 0.45;
    tl.set(grad, { opacity: 0 }, 0); tl.set(nm, { yPercent: 105 }, 0); tl.set(sub, { xPercent: -101 }, 0);
    FT(grad, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.out" }, t - 0.1);
    FT(bar, { scaleY: 0 }, { scaleY: 1, duration: 0.55, ease: "expo.out" }, t);
    FT(nm, { yPercent: 105 }, { yPercent: 0, duration: 0.7, ease: "expo.out" }, t + 0.12);
    FT(sub, { xPercent: -101 }, { xPercent: 0, duration: 0.8, ease: "expo.out" }, t + 0.32);
    FT(nm, { yPercent: 0 }, { yPercent: -105, duration: 0.35, ease: "power3.in" }, o);
    FT(sub, { xPercent: 0 }, { xPercent: -101, duration: 0.35, ease: "power3.in" }, o + 0.05);
    FT(bar, { scaleY: 1 }, { scaleY: 0, duration: 0.3, ease: "power3.in", transformOrigin: "50% 0%" }, o + 0.12);
    FT(grad, { opacity: 1 }, { opacity: 0, duration: 0.35, ease: "power2.in" }, o + 0.1);
  }

  // ---------- 6. captions ----------
  const norm = s => String(s).toLowerCase().replace(/[^a-z0-9'-]/g, "");
  function chunkWords(words, opt = {}) {
    const max = opt.max || 3, gap = opt.gap ?? 0.18, kw = (opt.keywords || []).map(norm);
    const groups = []; let cur = [];
    const flush = () => { if (cur.length) groups.push(cur); cur = []; };
    words.forEach(x => {
      const w = { w: String(x.w ?? x.text ?? x.word).trim(), start: +x.start, end: +x.end };
      if (!w.w) return;
      const prev = cur[cur.length - 1];
      if (prev && w.start - prev.end >= gap && cur.length >= 2) flush();
      cur.push(w);
      if (cur.length >= max || /[.!?,;:…]$/.test(w.w)) flush();
    });
    flush();
    for (let i = groups.length - 1; i > 0; i--)          // fold a lone trailing word into the previous group (max 4)
      if (groups[i].length === 1 && groups[i - 1].length < 4 && !/[.!?…]$/.test(groups[i - 1].at(-1).w)) { groups[i - 1].push(...groups[i]); groups.splice(i, 1); }
    return groups.map(g => ({ words: g.map(x => x.w), starts: g.map(x => x.start), end: g.at(-1).end,
      keys: g.map(x => kw.includes(norm(x.w))) }));
  }
  // words: whisper [{w|text, start, end}] relative to the soundbite; opt.offset = soundbite t=0 on the main timeline.
  // opt: { keywords:[], max:3, gap:0.18, hold:0.35, y:858, scrim:true }. One group on screen at a time.
  function captions3(words, opt = {}) {
    const root = host(opt.host || "#g3-captions"), off = opt.offset || 0, groups = chunkWords(words, opt);
    const tl = T();
    if (opt.scrim !== false && groups.length) {
      const sc = mk("g3-cap-scrim", root); tl.set(sc, { opacity: 0 }, 0);
      const a = groups[0].starts[0] + off, b = groups.at(-1).end + off + (opt.hold ?? 0.35);
      FT(sc, { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.out" }, a - 0.25);
      FT(sc, { opacity: 1 }, { opacity: 0, duration: 0.4, ease: "power2.in" }, b);
    }
    return groups.map((g, i) => {
      const el = mk("g3-cap", root); if (opt.y != null) el.style.top = opt.y + "px";
      const ws = g.words.map((w, k) => { const s = document.createElement("span"); s.className = "g3-cap-w" + (g.keys[k] ? " key" : ""); s.textContent = w; el.appendChild(s); return s; });
      const next = groups[i + 1];
      let end = Math.max(g.end + (opt.hold ?? 0.35), g.starts.at(-1) + 0.45);
      if (next) end = Math.min(end, next.starts[0] - 0.03);
      const a = g.starts[0] + off - 0.05, e = end + off;
      tl.set(el, { opacity: 0 }, 0); tl.set(el, { opacity: 1 }, a);
      ws.forEach((s, k) => FT(s, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }, Math.max(a, g.starts[k] + off - 0.04)));
      FT(el, { opacity: 1 }, { opacity: 0, duration: 0.12, ease: "power2.in" }, e - 0.12);
      return el;
    });
  }

  // ---------- 7. outro ----------
  // Scrim -> "RISE 2.0" tracks in + light sweep -> rule -> "Energise. Excite. Excel." phrase by phrase (one per
  // opt.beat 0.48) -> fade to black, fully black at t+dur. Needs >= 4 s.
  function outroTag(t, dur, opt = {}) {
    const root = host(opt.host || "#g3-outro");
    const scrim = mk("g3-o-scrim", root);
    const ti = buildTitle(root, { title: opt.title || "RISE", accent: opt.accent ?? "2.0", top: 360, size: opt.size || 200 });
    const rule = mk("g3-rule", root); rule.style.left = "760px"; rule.style.width = "400px"; rule.style.top = "596px";
    const words = opt.line || ["Energise", "Excite", "Excel"];
    const line = mk("g3-o-line", root, words.map(w => `<span>${esc(w)}<i>.</i></span>`).join(""));
    const tl = T(), beat = opt.beat ?? 0.48, end = t + dur;
    tl.set([scrim], { opacity: 0 }, 0); tl.set(ti.wrap, { opacity: 1 }, 0);
    FT(scrim, { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.inOut" }, t - 0.2);
    const settled = trackIn(ti.chars, t + 0.1, { spread: 40, dur: 1.4 });
    sweep(ti.sheen, settled, 1.2);
    FT(rule, { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "expo.inOut" }, t + 0.6);
    [...line.children].forEach((s, i) => FT(s, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }, t + 1.0 + i * beat));
    FT(ti.wrap, { scale: 1 }, { scale: 1.03, duration: dur, ease: "none", transformOrigin: "50% 50%" }, t);
    const fb = host(opt.black || "#g3-black"), fd = opt.fadeDur ?? 1.1;
    FT(fb, { opacity: 0 }, { opacity: 1, duration: fd, ease: "power1.inOut" }, end - fd);
    return { phrases: words.map((w, i) => t + 1.0 + i * beat), black: end };
  }

  // ---------- 8. texture + transitions ----------
  // Film grain: one pre-generated noise tile; background-position jumps every 1/opt.fps s (stepped tween, seek-safe).
  function grain(t0, t1, opt = {}) {
    const el = host(opt.host || "#g3-grain"), fps = opt.fps || 24, n = Math.max(1, Math.round((t1 - t0) * fps));
    if (opt.opacity != null) T().set(el, { opacity: opt.opacity }, 0);
    FT(el, { backgroundPosition: "0px 0px" }, { backgroundPosition: `${n * 211}px ${n * 337}px`, duration: t1 - t0, ease: `steps(${n})` }, t0);
  }
  // White flash peaking at t.
  function flash(t, opt = {}) {
    const el = host(opt.host || "#g3-flash"), i = opt.inDur ?? 0.06;
    FT(el, { opacity: 0 }, { opacity: opt.peak ?? 1, duration: i, ease: "power1.in" }, t - i);
    FT(el, { opacity: opt.peak ?? 1 }, { opacity: 0, duration: opt.outDur ?? 0.35, ease: "power2.out" }, t + 0.034);
  }
  // Anamorphic red/gold light leak: a warm glow and a thin horizontal streak sweep across, brightest at t (cut there).
  function leak(t, opt = {}) {
    const root = host(opt.host || "#g3-leak"), dur = opt.dur ?? 0.8, rtl = opt.dir === "left";
    const glow = mk("g3-leak", root), streak = mk("g3-leak streak", root);
    const xa = rtl ? 2000 : -1900, xb = rtl ? -1900 : 2000;
    [glow, streak].forEach(e => {
      FT(e, { x: xa }, { x: xb, duration: dur, ease: "power1.inOut" }, t - dur / 2);
      FT(e, { opacity: 0 }, { opacity: opt.peak ?? 0.9, duration: dur / 2, ease: "power2.in" }, t - dur / 2);
      FT(e, { opacity: opt.peak ?? 0.9 }, { opacity: 0, duration: dur / 2, ease: "power2.out" }, t);
    });
    FT(streak, { scaleY: 0.4 }, { scaleY: 1.6, duration: dur, ease: "sine.inOut" }, t - dur / 2);
  }
  // Slow push + drift for photos/footage (put it on the <img>/<video>, not on a wrapper you also transform).
  function kenBurns(el, t, dur, opt = {}) {
    const z0 = opt.from ?? 1.02, z1 = opt.to ?? 1.09, dx = opt.x ?? 24, dy = opt.y ?? -10;
    FT($(el), { scale: z0, x: -dx / 2, y: -dy / 2, transformOrigin: opt.origin || "50% 50%" }, { scale: z1, x: dx / 2, y: dy / 2, duration: dur, ease: opt.ease || "none" }, t);
  }

  window.GFX3 = { use: x => (tl = x), letterbox, openTitle, chapter, housesList, HOUSES, lowerThird3,
    chunkWords, captions3, outroTag, grain, flash, leak, kenBurns };
})();
