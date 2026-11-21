// Lead assembly: builds ../index.html from the footage index, beat grid and gfx kit.
// node build/assemble.cjs   (run from the project folder)
const fs = require('fs');
const shots = JSON.parse(fs.readFileSync('build/footage/shots.json', 'utf8'));
const B = 0.48, M0 = 2.0;               // beat length; music starts at t=2.0 so its hook section sits under the hook bite
const MUSIC_DUR = 46.08, DUR = +(M0 + MUSIC_DUR).toFixed(2); // 48.08
const T = m => +(M0 + m).toFixed(3);    // music time -> timeline time
const bite = n => shots.bites[n - 1];

// [src, beats, opts]  src: bNN (b-roll), pNN (photo), biteN (soundbite video). ms = media start offset
const seq = [];
let t = 0;
const add = (src, dur, o = {}) => { seq.push({ src, start: +t.toFixed(3), dur: +dur.toFixed(3), ...o }); t += dur; };

// HOOK 0-5.84: cold open on bite-1 (voice), music enters at 2.0
add('b04', 2.0, { kb: [1.0, 1.06] });
add('b38', 1.92, { whip: 'right', punch: 0.96 });
add('p05', 1.92, { whip: 'left', kb: [1.02, 1.12] });
// DROP 1 (5.84-21.2): 32 beats
const d1 = [['b01',1],['b02',1],['b06',1],['b05',1],['b07',1],['b03',1],['b25',1],['b11',1],
  ['b12',2],['b18',2],['p03',2],['b20',2],['b21',2],['p04',2],
  ['b23',1],['b24',1],['b26',1],['b27',1],['b19',1],['b10',1],['b40',1],['b13',1],
  ['b22',2],['p09',2]];
d1.forEach(([s, n, ms], i) => add(s, n * B, { ms, whip: i % 2 ? 'left' : 'right', punch: n === 1 && i % 3 === 0 ? 0 : null,
  kb: s[0] === 'p' ? [1.04, 1.16] : null, flash: i === 0 }));
// BREAKDOWN (21.2-32.72): bites 2 and 3
add('bite2', 3.6, { kb: [1.0, 1.1], flash: true });
add('p08', 1.04, { whip: 'right', kb: [1.05, 1.15] });
add('b31', 1.04, { whip: 'left', punch: 0.5 });
add('bite3', 3.6, { kb: [1.0, 1.08], wipe: true });
add('b32', 1.2, { whip: 'up', kb: [1.0, 1.1] });
add('b37', T(30.72) - t, { whip: 'right', punch: 0.5 });
// DROP 2 (32.72-44.24): party, 24 beats
const d2 = [['b28',1],['b29',1],['b30',1],['b31',1],['b32',1],['b33',1],['b34',1],['b35',1],
  ['b36',2],['b37',2],['p01',2],['p07',2],['b34',1,1.0],['b30',1,1.0],['b35',1,1.0],['b28',1,1.0],['b38',4,0.4]];
d2.forEach(([s, n, ms], i) => add(s, n * B, { ms, whip: i % 2 ? 'right' : 'left', punch: n === 1 && i % 2 === 0 ? 0 : null,
  kb: s[0] === 'p' ? [1.05, 1.18] : (n === 4 ? [1.0, 1.12] : null), flash: i === 0 }));
if (Math.abs(t - T(42.24)) > 0.01) throw new Error('drop 2 ends at ' + t);
const OUT = +t.toFixed(2);
add('p06', DUR - OUT, { whip: 'left', kb: [1.0, 1.1] }); // closing frame: full house + backdrop, fades to black // 44.24

// ---------- DOM ----------
const srcOf = s => s.startsWith('bite') ? `media/land/bite-${s.slice(4)}.mp4` : s[0] === 'b' ? `media/land/${s}.mp4` : `media/photos/${s}.jpg`;
let dom = '', js = '';
seq.forEach((s, i) => {
  const id = `s${i}`, m = `m${i}`, timing = `data-start="${s.start}" data-duration="${s.dur}"`;
  const media = s.src[0] === 'p'
    ? `<img id="${m}" class="media clip" src="${srcOf(s.src)}" ${timing} alt="">`
    : `<video id="${m}" class="media clip" src="${srcOf(s.src)}" ${timing}${s.ms ? ` data-media-start="${s.ms}"` : ''} muted playsinline preload="auto"></video>`;
  dom += `  <div id="${id}" class="shot">${media}</div>\n`;
  if (s.whip && i > 0) js += `GFX.whipIn("#${id}", ${s.start}, "${s.whip}");\n`;
  if (s.kb) js += `GFX.kenBurns("#${m}", ${s.start}, ${s.dur}, { from: ${s.kb[0]}, to: ${s.kb[1]} });\n`;
  else if (s.punch != null) js += `GFX.punchIn("#${m}", ${+(s.start + s.punch).toFixed(3)});\n`;
  if (s.flash) js += `GFX.flash(${s.start});\n`;
  if (s.wipe) js += `GFX.redWipe(${s.start});\n`;
});

// soundbites: voice audio + captions
const bites = [[1, 0.0], [2, seq.find(s => s.src === 'bite2').start], [3, seq.find(s => s.src === 'bite3').start]];
const kw = { 1: ['loudest'], 2: ['headhunted'], 3: ['offer'] };
let audio = '';
bites.forEach(([n, at]) => {
  const b = bite(n);
  audio += `  <audio id="v${n}" data-role="voice" src="media/bite-${n}.wav" data-start="${at}" data-volume="1"></audio>\n`;
  js += `GFX.captionsFromWords(${JSON.stringify(b.words.map(w => ({ w: w.w, start: +w.start.toFixed(2), end: +w.end.toFixed(2) })))}, { offset: ${at}, keywords: ${JSON.stringify(kw[n])} });\n`;
});
const b3 = bites[2][1];
js += `GFX.hookTitle(0.15, 5.4);\n`;
js += `GFX.lowerThird(${b3 + 0.2}, 3.2, { name: "REIN", tag: "Ex-Prada · 12 yrs training luxury sales" });\n`;
js += `tl.set('#fade', { opacity: 0 }, 0);\ntl.to('#fade', { opacity: 1, duration: 1.3, ease: 'power1.in' }, ${+(DUR - 1.4).toFixed(2)});\n`;

// SFX
const fx = [];
const sfx = (f, at, vol, d) => fx.push(`  <audio id="fx${fx.length}" src="sfx/sx-${f}.wav" data-start="${(+at).toFixed(3)}" data-volume="${vol}"${d ? ` data-duration="${d}"` : ''}></audio>`);
sfx('whoosh-soft', 1.92, 0.35); sfx('whoosh-soft', 3.84, 0.35);
for (const hit of [T(3.84), T(30.72)]) sfx('impact-bass-2', hit - 0.36, 0.5);
sfx('whoosh', T(3.84) - 0.12, 0.45);
sfx('whoosh', T(19.2) - 0.12, 0.4);
sfx('whoosh', T(30.72) - 0.12, 0.45);
sfx('pop', b3 + 0.25, 0.5);
sfx('whoosh-soft', b3 - 0.1, 0.4);

const html = `<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>Ray seminar recap</title>
<script src="vendor/gsap.min.js"></script>
<link rel="stylesheet" href="gfx.css" />
<link rel="stylesheet" href="gfx-land.css" />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1920px; height: 1080px; overflow: hidden; background: #111; }
  #root { width: 1920px; height: 1080px; position: relative; overflow: hidden; background: #111; }
  .shot { position: absolute; inset: 0; overflow: hidden; z-index: 1; }
  #fade { position: absolute; inset: 0; background: #000; opacity: 0; z-index: 90; }
  .media { position: absolute; inset: -40px; width: calc(100% + 80px); height: calc(100% + 80px); object-fit: cover; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${DUR}" data-fps="30" data-width="1920" data-height="1080">
${dom}
  <div id="gfx-vignette" class="clip" data-start="0" data-duration="${OUT}" data-track-index="5"></div>
  <div id="gfx-hook" class="clip" data-start="0" data-duration="5.84" data-track-index="6">
    <div class="hook-kicker">SALES SEMINAR · 20.11.2026</div>
    <div class="hook-rule"></div>
    <div class="hook-sub">with <b>Rein</b>, ex-Prada</div>
  </div>
  <div id="gfx-lt" class="clip" data-start="${b3}" data-duration="3.6" data-track-index="7">
    <div class="lt-bar"></div>
    <div class="lt-mask name"><div class="lt-name">REIN</div></div>
    <div class="lt-mask tag"><div class="lt-tag">Ex-Prada · 12 yrs training luxury sales</div></div>
  </div>
  <div id="gfx-captions" class="clip" data-start="0" data-duration="${OUT}" data-track-index="8" data-track-kind="captions"></div>
  <div id="gfx-leak" class="clip" data-start="0" data-duration="${OUT}" data-track-index="9"><div class="leak-glow"></div><div class="leak-bar"></div></div>
  <div id="gfx-flash" class="clip" data-start="0" data-duration="${DUR}" data-track-index="10"></div>
  <div id="fade" class="clip" data-start="0" data-duration="${DUR}" data-track-index="11"></div>
  <audio id="music" src="sfx/music.wav" data-start="${M0}" data-volume="0.8"></audio>
${audio}${fx.join('\n')}
</div>
<script>window.GFX_CAP_W = 1500; window.GFX_CAP_MAX = 96; window.GFX_WIPE = [-3800, 2400];</script>
<script src="gfx.js"></script>
<script>
const tl = gsap.timeline({ paused: true });
GFX.use(tl);
${js}
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
</script>
</body>
</html>
`;
fs.writeFileSync('index.html', html);
console.log('shots', seq.length, 'duration', DUR, 'outro at', OUT);
