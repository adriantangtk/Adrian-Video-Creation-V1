#!/usr/bin/env python3
"""Original 125 BPM corporate-house track for ray-seminar-recap. Fully synthesized (copyright-free).
Usage: python3 compose.py <out.wav>
"""
import sys, json, numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt, fftconvolve, resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d
import pyloudnorm as pyln

SR = 48000
BPM = 125.0
BEAT = 60.0 / BPM          # 0.48
BAR = 4 * BEAT             # 1.92
NBARS = 24
DUR = NBARS * BAR          # 46.08
N = int(round(DUR * SR))
rng = np.random.default_rng(7)

def S(t): return int(round(t * SR))
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, f1, f2, o=2): return sosfilt(butter(o, [f1, f2], 'band', fs=SR, output='sos'), x, axis=0)

def stereo(): return np.zeros((N, 2))
def add(bus, sig, t0, gain=1.0, pan=0.0):
    i = S(t0)
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
    j = min(N, i + len(sig))
    if j > i: bus[i:j] += sig[:j - i] * gain

def saw(f, n, ph=0.0):
    p = (ph + f * np.arange(n) / SR) % 1.0
    return 2 * p - 1

# ---------------- arrangement ----------------
CH = {'Am': [57, 60, 64, 67, 71], 'F': [53, 57, 60, 64, 67], 'C': [55, 60, 64, 67, 69], 'G': [55, 59, 62, 67, 69]}
ROOT = {'Am': 33, 'F': 29, 'C': 36, 'G': 31}
PROG = ['Am', 'F', 'Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G',          # 1-10
        'Am', 'F', 'C', 'G', 'Am', 'G',                               # 11-16
        'Am', 'F', 'C', 'G', 'Am', 'G',                               # 17-22
        'Am', 'Am']                                                   # 23-24
def bar_t(b): return (b - 1) * BAR   # 1-indexed bar start
SEC = [('hook', 1, 2), ('drop1', 3, 10), ('breakdown', 11, 16), ('drop2', 17, 22), ('outro', 23, 24)]
def section(b):
    for n, a, z in SEC:
        if a <= b <= z: return n

# ---------------- instruments ----------------
def kick(soft=False):
    n = S(0.42); t = np.arange(n) / SR
    f = 47 + 118 * np.exp(-t / 0.032) + 40 * np.exp(-t / 0.004)
    ph = 2 * np.pi * np.cumsum(f) / SR
    amp = np.where(t < 0.02, 1.0, np.exp(-(t - 0.02) / 0.22)) * np.minimum(1, t / 0.0008 + 0.0)
    body = np.sin(ph) * amp
    click = hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.003) * 0.35
    k = np.tanh(1.8 * (body + click)) / np.tanh(1.8)
    k[-S(0.03):] *= np.linspace(1, 0, S(0.03))
    if soft: k = lp(k, 900) * 0.55
    return k

def clap():
    n = S(0.45); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    env = np.zeros(n)
    for d in (0, 0.009, 0.018, 0.026):
        tt = t - d; env += np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / 0.006), 0)
    env += np.where(t > 0.026, 0.55 * np.exp(-(t - 0.026) / 0.11), 0)
    c = bp(nz, 900, 5000) * env
    body = np.sin(2 * np.pi * 195 * t) * np.exp(-t / 0.05) * 0.5
    return (c + body) * 0.8

def ohat():
    n = S(0.22); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000, 4) * np.exp(-t / 0.07) * np.minimum(1, t / 0.002)

def chat():
    n = S(0.06); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 8500, 4) * np.exp(-t / 0.018)

def pluck(m, dur=0.32, bright=1.0):
    f = mtof(m); n = S(dur + 0.25); t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 28):
        if k * f > 14000: break
        out += np.sin(2 * np.pi * k * f * t + rng.uniform(0, 6.28) * 0) / k * np.exp(-t * (4 + k * 2.2 / bright))
        out += 0.5 * np.sin(2 * np.pi * k * f * 1.004 * t) / k * np.exp(-t * (4 + k * 2.2 / bright))
    out *= np.minimum(1, t / 0.002)
    rel = np.clip((t - dur) / 0.2, 0, 1); out *= (1 - rel) ** 2
    return out * 0.35

def pad_note(m, dur, att, rel, spread=1.0):
    f = mtof(m); n = S(dur + rel); t = np.arange(n) / SR
    o = np.zeros((n, 2))
    for i, c in enumerate([-14, -7, 0, 7, 14]):
        s = saw(f * 2 ** (c / 1200), n, rng.uniform())
        pan = (i - 2) / 2 * 0.8 * spread
        o[:, 0] += s * np.cos((pan + 1) * np.pi / 4); o[:, 1] += s * np.sin((pan + 1) * np.pi / 4)
    env = np.minimum(1, t / att) * np.where(t > dur, np.clip(1 - (t - dur) / rel, 0, 1), 1)
    return o * env[:, None] * 0.12

def bass_note(m, dur):
    f = mtof(m); n = S(dur + 0.02); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * f * t)
    s = lp(saw(f * 2, n) + 0.6 * saw(f * 2.003, n), 420, 2)
    env = np.minimum(1, t / 0.004) * np.where(t > dur, np.clip(1 - (t - dur) / 0.02, 0, 1), 1)
    return (sub * 0.75 + s * 0.45) * env

def frame_sweep_noise(dur, f0, f1, width=1.0):
    """noise with a band-pass whose centre sweeps f0->f1 (exponential), via FFT overlap-add"""
    n = S(dur); W = 2048; H = W // 2; win = np.hanning(W)
    out = np.zeros(n + W); nz = rng.standard_normal(n + W)
    fr = np.fft.rfftfreq(W, 1 / SR)
    for i in range(0, n, H):
        x = i / n; fc = f0 * (f1 / f0) ** x
        mask = np.exp(-0.5 * (np.log2(np.maximum(fr, 1) / fc) / (0.6 * width)) ** 2)
        seg = np.fft.irfft(np.fft.rfft(nz[i:i + W] * win) * mask)
        out[i:i + W] += seg * win
    return out[:n]

def riser(dur):
    n = S(dur); t = np.arange(n) / SR; x = t / dur
    nz = frame_sweep_noise(dur, 400, 9000)
    nz = nz / (np.abs(nz).max() + 1e-9)
    f = mtof(57) * 2 ** (2 * x ** 1.5)
    ton = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    env = x ** 2.2
    return (nz * 0.8 + ton * 0.18) * env

def impact():
    n = S(2.0); t = np.arange(n) / SR
    f = 34 + 40 * np.exp(-t / 0.08)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.55)
    crash = hp(rng.standard_normal(n), 3500) * np.exp(-t / 0.7) * 0.35
    return np.tanh(1.5 * (boom + crash)) * 0.9

def crash():
    n = S(2.0); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 5000, 3) * np.exp(-t / 0.6) * 0.3

def reverb_ir(length=2.2, decay=0.55, pre=0.02):
    n = S(length); t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        nz = rng.standard_normal(n) * np.exp(-t / decay)
        ir[:, c] = lp(nz, 5500)
    ir[:S(pre)] = 0
    return ir / np.sqrt((ir ** 2).sum(0)).max()

# ---------------- render buses ----------------
drums, kicks, bass, pads, plk, fx, verb_send = (stereo() for _ in range(7))
kick_times = []
KD, KS, CL, OH = kick(), kick(True), clap(), ohat()

for b in range(1, NBARS + 1):
    sec = section(b); t0 = bar_t(b); chord = PROG[b - 1]
    for q in range(4):
        tb = t0 + q * BEAT
        # kick
        if sec in ('drop1', 'drop2'):
            if not (b == 10 and q == 3):            # gap before breakdown
                add(kicks, KD, tb, 1.0); kick_times.append(tb)
        elif sec == 'hook':
            add(kicks, KS, tb, 0.7); kick_times.append(tb)
        elif sec == 'breakdown' and b >= 15 and not (b == 16 and q == 3):
            add(kicks, KS, tb, 0.45 + 0.1 * (b - 15)); kick_times.append(tb)
        elif sec == 'outro' and b == 23 and q == 0:
            add(kicks, KD, tb, 1.0); kick_times.append(tb)
        # claps on 2 & 4
        if sec in ('drop1', 'drop2') and q in (1, 3) and not (b == 10 and q == 3):
            add(drums, CL, tb, 0.55); add(verb_send, CL, tb, 0.25)
        # offbeat open hats
        if sec in ('drop1', 'drop2'):
            add(drums, OH, tb + BEAT / 2, 0.32, 0.15)
        elif sec == 'breakdown' and b >= 13:
            add(drums, OH, tb + BEAT / 2, 0.14, 0.15)
        # 16th closed hats
        if sec == 'drop2' or (sec == 'drop1' and b >= 7):
            for s16 in (1, 3):
                add(drums, chat(), tb + s16 * BEAT / 4, 0.16 if s16 == 1 else 0.12, -0.25)
        # offbeat bass
        if sec in ('drop1', 'drop2'):
            for s16 in (2, 3) if sec == 'drop2' else (2,):
                add(bass, bass_note(ROOT[chord] + 12 * (s16 == 3), 0.2 if s16 == 2 else 0.1), tb + s16 * BEAT / 4, 0.55)
    # sustained sub in breakdown / hook
    if sec in ('breakdown',):
        nb = bass_note(ROOT[chord], BAR - 0.05); nb = lp(nb, 200)
        n_ = len(nb); nb *= np.minimum(1, np.arange(n_) / S(0.15)); add(bass, nb, t0, 0.35)
    # pads (one chord per bar)
    att = 0.05 if sec in ('drop1', 'drop2') else 0.35
    durp = BAR if sec != 'outro' else (2 * BAR if b == 23 else 0)
    if durp:
        for m in CH[chord]:
            p = pad_note(m, durp, att, 0.5 if sec != 'outro' else 1.2, 1.3 if sec == 'drop2' else 1.0)
            add(pads, p, t0, 1.0); add(verb_send, p, t0, 0.35)
    # pluck hook (16th grid 3-3-4-3-3)
    MOT = {'Am': [76, 72, 69, 72, 76], 'F': [77, 72, 69, 72, 77], 'C': [76, 72, 67, 72, 79], 'G': [74, 71, 67, 74, 79]}
    slots = [0, 3, 6, 10, 13]
    if sec in ('drop1', 'drop2', 'breakdown'):
        if sec == 'drop1' and b < 5: pass                # pluck enters at bar 5
        else:
            g = 0.5 if sec == 'breakdown' else 0.8
            bright = 0.5 if sec == 'breakdown' else 1.0
            for s, m in zip(slots, MOT[chord]):
                if sec == 'breakdown' and s in (3, 13): continue
                nte = pluck(m, 0.2, bright); add(plk, nte, t0 + s * BEAT / 4, g, 0.1)
                if sec == 'drop2':
                    add(plk, pluck(m + 12, 0.15, 1.0), t0 + s * BEAT / 4, 0.32, -0.3)

# FX: risers, impacts, crashes
add(fx, riser(BAR), bar_t(2), 0.45)                     # into drop1 (3.84)
add(fx, impact(), bar_t(3), 0.9); add(verb_send, impact(), bar_t(3), 0.3)
add(fx, crash(), bar_t(3), 0.8); add(fx, crash(), bar_t(7), 0.6)
# downlifter / impact into breakdown 19.2
rev_c = crash()[::-1][-S(BEAT):]; add(fx, rev_c, bar_t(11) - BEAT, 0.7)
add(fx, impact(), bar_t(11), 0.55)
add(fx, riser(2 * BAR), bar_t(15), 0.6)                 # into drop2 (30.72)
add(fx, impact(), bar_t(17), 1.0); add(fx, crash(), bar_t(17), 0.9); add(fx, crash(), bar_t(21), 0.7)
add(verb_send, impact(), bar_t(17), 0.3)
add(fx, rev_c, bar_t(23) - BEAT, 0.6); add(fx, impact(), bar_t(23), 0.6); add(fx, crash(), bar_t(23), 0.7)
# snare roll in last bar of hook & last 2 beats of bar 16
for (t_start, t_end, base) in ((bar_t(2) + 2 * BEAT, bar_t(3), 0.15), (bar_t(16) + 2 * BEAT, bar_t(17), 0.25)):
    k = 0; tt = t_start
    while tt < t_end - 1e-6:
        x = (tt - t_start) / (t_end - t_start)
        add(drums, CL, tt, base * (0.3 + 0.7 * x), 0); tt += BEAT / 4 if x < 0.5 else BEAT / 8

# ---------------- sidechain ----------------
t = np.arange(N) / SR
sc = np.ones(N)
for kt in kick_times:
    i = S(kt); j = min(N, i + S(0.3)); dt = np.arange(j - i) / SR
    depth = 0.75 if section(int(kt // BAR) + 1) in ('drop1', 'drop2') else 0.35
    sc[i:j] = np.minimum(sc[i:j], 1 - depth * (1 - np.clip(dt / 0.26, 0, 1)) ** 2)
sc = uniform_filter1d(sc, S(0.003))
bass *= sc[:, None]; pads *= sc[:, None]; plk *= (0.5 + 0.5 * sc)[:, None]

# pad brightness automation: dark in hook/breakdown/outro, bright in drops, opening on risers
def curve(points):
    xs, ys = zip(*points); return np.interp(t, xs, ys)
bright = curve([(0, 0), (bar_t(2), 0.05), (bar_t(3) - 0.01, 0.45), (bar_t(3), 1), (bar_t(11) - 0.01, 1), (bar_t(11), 0.0),
                (bar_t(15), 0.05), (bar_t(17) - 0.01, 0.7), (bar_t(17), 1), (bar_t(23) - 0.01, 1), (bar_t(23), 0.25), (DUR, 0)])
pads = lp(pads, 650) * (1 - bright[:, None]) + lp(pads, 3800) * bright[:, None]
plk = hp(plk, 250)

# ping-pong delay on pluck (dotted 8th)
d = S(0.75 * BEAT); dl = np.zeros_like(plk)
src = lp(plk, 4000) * 0.35
for k in range(1, 5):
    off = d * k; ch = k % 2
    dl[off:, ch] += src[:-off, 0 if ch else 1] * (0.55 ** (k - 1))
plk += dl

# reverb
ir = reverb_ir()
wet = np.stack([fftconvolve(verb_send[:, c] + plk[:, c] * 0.25, ir[:, c])[:N] for c in range(2)], 1)
wet = hp(wet, 300) * 0.5

mix = kicks * 0.9 + drums * 0.8 + bass * 0.9 + pads * 0.75 + plk * 0.6 + fx * 0.7 + wet

# voice pocket: zero-phase cut of 1-4 kHz under speech sections (hook + breakdown)
pocket = curve([(0, 0.55), (bar_t(3) - 0.15, 0.55), (bar_t(3), 0), (bar_t(11) - 0.1, 0), (bar_t(11) + 0.2, 0.6),
                (bar_t(16), 0.6), (bar_t(17), 0.0), (DUR, 0)])
band = sosfiltfilt(butter(2, [1000, 4000], 'band', fs=SR, output='sos'), mix, axis=0)
mix = mix - band * pocket[:, None]

# master: low-cut, gentle tilt, fade-out, loudness, true-peak limiter
mix = hp(mix, 28)
fade = curve([(0, 1), (bar_t(23) + 1.2, 1), (DUR - 0.05, 0), (DUR, 0)]) ** 1.6
mix *= fade[:, None]
mix[:S(0.004)] *= np.linspace(0, 1, S(0.004))[:, None]

meter = pyln.Meter(SR)
CEIL = 10 ** (-1.3 / 20)
def limit(x):
    up = resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(x)]
    g = np.minimum(1, CEIL / np.maximum(pk, 1e-9))
    g = minimum_filter1d(g, S(0.008))
    g = uniform_filter1d(g, S(0.004))
    g = np.minimum(g, minimum_filter1d(np.minimum(1, CEIL / np.maximum(pk, 1e-9)), 3))
    return x * g[:, None]
mix /= np.abs(mix).max()
for it in range(4):
    L = meter.integrated_loudness(mix)
    mix *= 10 ** ((-14.0 - L) / 20)
    mix = limit(mix)
mix = np.clip(mix, -CEIL, CEIL)
print('LUFS (pyloudnorm):', round(meter.integrated_loudness(mix), 2), 'sample peak dB', round(20 * np.log10(np.abs(mix).max()), 2))

import wave
out = sys.argv[1]
pcm = (mix * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

grid = {
    'bpm': BPM, 'beat': BEAT, 'bar': BAR, 'offset': 0.0, 'duration': DUR,
    'beats': [round(i * BEAT, 4) for i in range(NBARS * 4)],
    'bars': [round(i * BAR, 4) for i in range(NBARS)],
    'sections': [{'name': n, 'start': round(bar_t(a), 4), 'end': round(bar_t(z + 1), 4), 'bars': [a, z]} for n, a, z in SEC],
    'hits': [3.84, 19.2, 30.72, 42.24],
    'hitsDetail': [
        {'t': 3.84, 'what': 'riser peak + impact + crash: drop 1 starts'},
        {'t': 19.2, 'what': 'reverse-cymbal swell + soft impact: breakdown starts (beat at 18.72 is silent gap)'},
        {'t': 30.72, 'what': 'riser peak + snare roll + big impact + crash: drop 2 starts'},
        {'t': 42.24, 'what': 'reverse-cymbal + impact + crash: outro chord, fades to silence by 46.08'}],
    'kickTimes': [round(k, 4) for k in kick_times],
    'notes': 'Speech-friendly sections (1-4 kHz pocket cut): hook 0-3.84, breakdown 19.2-30.72. Chords per bar: ' + ' '.join(PROG),
}
json.dump(grid, open(sys.argv[2], 'w'), indent=1)
