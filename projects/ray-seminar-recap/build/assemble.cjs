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
add('bite1', 2.0, { kb: [1.0, 1.06] });
add('b04', 1.92, { whip: 'right', punch: 0.96 });
add('b03', 1.92, { whip: 'left', kb: [1.02, 1.12] });
// DROP 1 (5.84-21.2): 32 beats
const d1 = [['b01',1],['b02',1],['b06',1],['b09',1,1.0],['b07',1],['b08',1],['b09',1],['b11',1],
  ['b12',2],['b14',2],['p02',2],['b17',2],['b18',2],['b20',2],
  ['b24',1],['b25',1],['b26',1],['b27',1],['b10',1],['b39',1],['b40',1],['b13',1],
  ['b19',2],['b22',2]];
d1.forEach(([s, n, ms], i) => add(s, n * B, { ms, whip: i % 2 ? 'left' : 'right', punch: n === 1 && i % 3 === 0 ? 0 : null,
  kb: s[0] === 'p' ? [1.04, 1.16] : null, flash: i === 0 }));
// BREAKDOWN (21.2-32.72): bites 2 and 3
add('bite2', 3.6, { kb: [1.0, 1.1], flash: true });
add('p08', 1.04, { whip: 'right', kb: [1.05, 1.15] });
add('p10', 1.04, { whip: 'left', kb: [1.1, 1.0] });
add('bite3', 3.6, { kb: [1.0, 1.08], wipe: true });
add('p11', 1.2, { whip: 'up', kb: [1.0, 1.12] });
add('b38', T(30.72) - t, { whip: 'right', punch: 0.5 });
// DROP 2 (32.72-44.24): party, 24 beats
const d2 = [['b28',1],['b29',1],['b30',1],['b31',1],['b32',1],['b33',1],['b34',1],['b35',1],
  ['b36',2],['b37',2],['p06',2],['b16',2],['b34',1,1.0],['b30',1,1.0],['b35',1,1.0],['b28',1,1.0],['b38',4,0.4]];
d2.forEach(([s, n, ms], i) => add(s, n * B, { ms, whip: i % 2 ? 'right' : 'left', punch: n === 1 && i % 2 === 0 ? 0 : null,
  kb: s[0] === 'p' ? [1.05, 1.18] : (n === 4 ? [1.0, 1.12] : null), flash: i === 0 }));
if (Math.abs(t - T(42.24)) > 0.01) throw new Error('drop 2 ends at ' + t);
const OUT = +t.toFixed(2); // 44.24

// ---------- DOM ----------
const srcOf = s => s.startsWith('bite') ? `media/bite-${s.slice(4)}.mp4` : s[0] === 'b' ? `media/broll/${s}.mp4` : `media/photos/${s}.jpg`;
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
js += `GFX.lowerThird(${b3 + 0.2}, 3.2, { name: "RAY", tag: "Ex-Prada · 12 yrs training luxury sales" });\n`;
js += `const cues = GFX.outro(${OUT}, { counter: "20.11.2026", handle: "@adriantang" });\n`;

// SFX
const fx = [];
const sfx = (f, at, vol, d) => fx.push(`  <audio id="fx${fx.length}" src="sfx/sx-${f}.wav" data-start="${(+at).toFixed(3)}" data-volume="${vol}"${d ? ` data-duration="${d}"` : ''}></audio>`);
sfx('whoosh-soft', 1.92, 0.35); sfx('whoosh-soft', 3.84, 0.35);
for (const hit of [T(3.84), T(30.72), OUT]) sfx('impact-bass-2', hit - 0.36, 0.5);
sfx('whoosh', T(3.84) - 0.12, 0.45);
sfx('whoosh', T(19.2) - 0.12, 0.4);
sfx('whoosh', T(30.72) - 0.12, 0.45);
sfx('pop', b3 + 0.25, 0.5);
sfx('whoosh-soft', b3 - 0.1, 0.4);
for (let k = 0; k < 4; k++) sfx('click-hi', OUT + 1.45 + k * 0.17, 0.35);
sfx('sparkle', OUT + 2.3, 0.5);

const html = `<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>Ray seminar recap</title>
<script src="vendor/gsap.min.js"></script>
<link rel="stylesheet" href="gfx.css" />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1080px; height: 1920px; overflow: hidden; background: #111; }
  #root { width: 1080px; height: 1920px; position: relative; overflow: hidden; background: #111; }
  .shot { position: absolute; inset: 0; overflow: hidden; z-index: 1; }
  .media { position: absolute; inset: -40px; width: calc(100% + 80px); height: calc(100% + 80px); object-fit: cover; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${DUR}" data-fps="30" data-width="1080" data-height="1920">
${dom}
  <div id="gfx-vignette" class="clip" data-start="0" data-duration="${OUT}" data-track-index="5"></div>
  <div id="gfx-hook" class="clip" data-start="0" data-duration="5.84" data-track-index="6">
    <div class="hook-kicker">SALES SEMINAR · 20.11.2026</div>
    <div class="hook-rule"></div>
    <div class="hook-sub">with <b>Ray</b>, ex-Prada</div>
  </div>
  <div id="gfx-lt" class="clip" data-start="${b3}" data-duration="3.6" data-track-index="7">
    <div class="lt-bar"></div>
    <div class="lt-mask name"><div class="lt-name">RAY</div></div>
    <div class="lt-mask tag"><div class="lt-tag">Ex-Prada · 12 yrs training luxury sales</div></div>
  </div>
  <div id="gfx-captions" class="clip" data-start="0" data-duration="${OUT}" data-track-index="8" data-track-kind="captions"></div>
  <div id="gfx-leak" class="clip" data-start="0" data-duration="${OUT}" data-track-index="9"><div class="leak-glow"></div><div class="leak-bar"></div></div>
  <div id="gfx-flash" class="clip" data-start="0" data-duration="${DUR}" data-track-index="10"></div>
  <div id="gfx-outro" class="clip" data-start="${OUT}" data-duration="${+(DUR - OUT).toFixed(2)}" data-track-index="11">
    <div class="out-kicker">SALES SEMINAR · WITH RAY</div>
    <div class="out-title">
      <div class="out-line serif"><span>The art of</span></div>
      <div class="out-line serif"><span>serving the</span></div>
      <div class="out-line bold"><span>ULTRA-RICH</span></div>
    </div>
    <div class="out-rule"></div>
    <div class="out-counter">20.11.2026</div>
    <div class="out-handle">@adriantang</div>
  </div>
  <audio id="music" src="sfx/music.wav" data-start="${M0}" data-volume="0.8"></audio>
${audio}${fx.join('\n')}
</div>
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
