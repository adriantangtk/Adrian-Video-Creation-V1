// v3 lead assembly: RISE 2.0 cinematic recap, landscape 1920x1080, 51.84 s on the music3 grid.
// node build/assemble3.cjs   (run from the project folder) -> index.html
const fs = require('fs');
const F = JSON.parse(fs.readFileSync('build/footage3/shots.json', 'utf8'));
const B = 0.48, DUR = 51.84;
const r = x => +x.toFixed(3);

const seq = [];
let t = 0;
const add = (src, beats, o = {}) => { const dur = o.sec ?? beats * B; seq.push({ src, start: r(t), dur: r(dur), ...o }); t += dur; };
const at = x => { t = x; };

// COLD OPEN 0-5.76: title over a dimmed puzzle-board push and the ballroom
add('s54', 0, { sec: 3.0, kb: [1.0, 1.06] });
add('s01', 0, { sec: 2.76, kb: [1.03, 1.08] });
// HOOK 5.76-11.52 (bite-1 at 5.70)
add('s02', 4); add('s19', 4); add('s56', 4);
// ENERGISE 11.52-23.04
add('s20', 6);
[['s42',2],['s44',2],['s45',2],['s03',2],['s32',1],['s33',1],['s15',1],['s36',1],['s10',2],['s04',2],['s37',2]]
  .forEach(([s, n]) => add(s, n, { kb: n >= 2 ? [1.0, 1.04] : null }));
if (Math.abs(t - 23.04) > 0.01) throw new Error('energise ends ' + t);
// EXCITE 23.04-34.56
add('s16', 4);                 // MEET YOUR SPEAKERS + chapter word
add('s23', 6);                 // Rein's bio slide, host line "He started in Prada..."
add('s24', 6);                 // push to the WORKED FOR slide, houses list on the left
add('s26', 4);                 // Rein (black) on stage, watch question -> lower third
add('s27', 4);
if (Math.abs(t - 34.56) > 0.01) throw new Error('excite ends ' + t);
// EXCEL 34.56-46.08
add('s06', 6); add('s55', 4);
['s48','s50','s49','s51','s09','s53'].forEach(s => add(s, 2));
add('s08', 2);
if (Math.abs(t - 46.08) > 0.01) throw new Error('excel ends ' + t);
// OUTRO 46.08-51.84
add('ph08', 12, { kb: [1.02, 1.12] });

const srcOf = s => s.startsWith('ph') ? `media/v3/photos/${s}.jpg` : `media/v3/${s}.mp4`;
let dom = '', js = '';
seq.forEach((s, i) => {
  const id = `m${i}`, timing = `data-start="${s.start}" data-duration="${s.dur}"`;
  dom += s.src.startsWith('ph')
    ? `  <div class="shot"><img id="${id}" class="media clip" src="${srcOf(s.src)}" ${timing} alt=""></div>\n`
    : `  <div class="shot"><video id="${id}" class="media clip" src="${srcOf(s.src)}" ${timing} muted playsinline preload="auto"></video></div>\n`;
  if (s.kb) js += `GFX3.kenBurns("#${id}", ${s.start}, ${s.dur}, { from: ${s.kb[0]}, to: ${s.kb[1]} });\n`;
});

// voice + captions
const bite = n => F.bites.find(b => b.name === n);
const V = { hook: 5.70, prada: 25.0, watch: 30.95 };
const KW = { hook: ['loudest'], prada: ['Prada'], watch: ['offer'] };
let audio = '';
for (const [n, off] of Object.entries(V)) {
  const b = bite(n);
  audio += `  <audio id="v-${n}" data-role="voice" src="${b.wav}" data-start="${off}" data-volume="1"></audio>\n`;
  const words = b.words.map(w => ({ w: w.w, start: +w.start.toFixed(2), end: +w.end.toFixed(2) }));
  js += `GFX3.captions3(${JSON.stringify(words)}, { offset: ${off}, keywords: ${JSON.stringify(KW[n])}${n === 'hook' ? ', y: 800' : ''} });\n`;
}

js += `
GFX3.grain(0, ${DUR}, { opacity: 0.08 });
GFX3.openTitle(0.3, 5.46, { bg: 0.62 });
GFX3.letterbox(5.76, 23.04);
GFX3.letterbox(34.56, null);
GFX3.flash(11.52, { peak: 0.85 });
GFX3.chapter(11.6, "ENERGISE", { index: "01" });
GFX3.leak(23.04, { dir: "right" });
GFX3.chapter(23.1, "EXCITE", { index: "02" });
const houses = GFX3.housesList(27.9, 3.0, null, { title: "15+ YEARS ACROSS", beat: 0.27 });
GFX3.lowerThird3(31.05, 3.3, { name: "REIN", full: "Reinald Goh", tag: "UHNW Clienteling Expert" });
GFX3.flash(34.56, { peak: 0.9 });
GFX3.chapter(34.64, "EXCEL", { index: "03" });
GFX3.leak(46.08, { dir: "left", peak: 0.7 });
GFX3.outroTag(46.3, 5.54);
`;

// SFX (music3 already carries the braams/impacts, so keep this light)
const fx = [];
const sfx = (f, a, vol, d) => fx.push(`  <audio id="fx${fx.length}" src="sfx/sx-${f}.wav" data-start="${(+a).toFixed(3)}" data-volume="${vol}"${d ? ` data-duration="${d}"` : ''}></audio>`);
sfx('whoosh-soft', 11.3, 0.35); sfx('whoosh-soft', 22.8, 0.35); sfx('whoosh-soft', 34.3, 0.35); sfx('whoosh-soft', 45.8, 0.3);
for (let k = 0; k < 7; k++) sfx('click-hi', 27.9 + 0.27 * (k + 1), 0.22, 0.2);
sfx('pop', 31.1, 0.35);

const html = `<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>RISE 2.0 recap</title>
<script src="vendor/gsap.min.js"></script>
<link rel="stylesheet" href="gfx3.css" />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1920px; height: 1080px; overflow: hidden; background: #000; }
  #root { width: 1920px; height: 1080px; position: relative; overflow: hidden; background: #000; }
  .shot { position: absolute; inset: 0; overflow: hidden; z-index: 1; }
  .media { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${DUR}" data-fps="30" data-width="1920" data-height="1080">
${dom}
  <div id="g3-vignette" class="g3-host clip" data-start="0" data-duration="${DUR}" data-track-index="4"></div>
  <div id="g3-grain" class="g3-host clip" data-start="0" data-duration="${DUR}" data-track-index="5"></div>
  <div id="g3-chapter" class="g3-host clip" data-start="11.5" data-duration="26" data-track-index="6"></div>
  <div id="g3-houses" class="g3-host clip" data-start="27.8" data-duration="3.3" data-track-index="7"></div>
  <div id="g3-lt" class="g3-host clip" data-start="31" data-duration="3.5" data-track-index="8"></div>
  <div id="g3-captions" class="g3-host clip" data-start="5.6" data-duration="29" data-track-index="9" data-track-kind="captions"></div>
  <div id="g3-outro" class="g3-host clip" data-start="46.2" data-duration="5.64" data-track-index="10"></div>
  <div id="g3-open" class="g3-host clip" data-start="0" data-duration="5.9" data-track-index="11"></div>
  <div id="g3-matte" class="g3-host clip" data-start="0" data-duration="${DUR}" data-track-index="12"></div>
  <div id="g3-leak" class="g3-host clip" data-start="0" data-duration="${DUR}" data-track-index="13"></div>
  <div id="g3-flash" class="g3-host clip" data-start="0" data-duration="${DUR}" data-track-index="14"></div>
  <div id="g3-black" class="g3-host clip" data-start="0" data-duration="${DUR}" data-track-index="15"></div>
  <audio id="music" src="sfx/music3.wav" data-start="0" data-volume="0.85"></audio>
${audio}${fx.join('\n')}
</div>
<script src="gfx3.js"></script>
<script>
const tl = gsap.timeline({ paused: true });
GFX3.use(tl);
${js}
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
</script>
</body>
</html>
`;
fs.writeFileSync('index.html', html);
console.log('shots', seq.length, 'duration', DUR);
