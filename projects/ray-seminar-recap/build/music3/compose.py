#!/usr/bin/env python3
"""RISE 2.0 v3: cinematic trailer / corporate-anthem track, 125 BPM, A minor -> C major lift.
Fully synthesized (copyright-free). Builds on build/music/compose.py.
Usage: python3 compose.py <out.wav> <beatgrid.json>
27 bars x 1.92 s = 51.84 s.
"""
import sys, json, wave, numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt, fftconvolve, resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d
import pyloudnorm as pyln

SR = 48000; BPM = 125.0; BEAT = 60.0 / BPM; BAR = 4 * BEAT
NBARS = 27; DUR = NBARS * BAR; N = int(round(DUR * SR))
rng = np.random.default_rng(11)
def S(t): return int(round(t * SR))
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, f1, f2, o=2): return sosfilt(butter(o, [f1, f2], 'band', fs=SR, output='sos'), x, axis=0)
def stereo(n=N): return np.zeros((n, 2))
def pan2(sig, pan):
    return np.stack([sig * np.cos((pan + 1) * np.pi / 4) * 1.414, sig * np.sin((pan + 1) * np.pi / 4) * 1.414], 1)
def add(bus, sig, t0, gain=1.0, pan=0.0):
    i = S(t0)
    if sig.ndim == 1: sig = pan2(sig, pan)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if j > i: bus[i:j] += sig[:j - i] * gain
def saw(f, n, ph=0.0):
    if np.isscalar(f): p = (ph + f * np.arange(n) / SR) % 1.0
    else: p = (ph + np.cumsum(f) / SR) % 1.0
    return 2 * p - 1
def sweep_lp(x, env, lo, hi, steps=7):
    """time-varying low-pass: env 0..1 maps lo..hi (log), crossfading between fixed filters"""
    fcs = lo * (hi / lo) ** np.linspace(0, 1, steps)
    pos = np.clip(env, 0, 1) * (steps - 1)
    out = np.zeros_like(x)
    for k, fc in enumerate(fcs):
        w = np.clip(1 - np.abs(pos - k), 0, 1)
        if w.max() == 0: continue
        out += lp(x, fc, 2) * (w[:, None] if x.ndim == 2 else w)
    return out
def bar_t(b): return (b - 1) * BAR
t = np.arange(N) / SR
def curve(points):
    xs, ys = zip(*points); return np.interp(t, xs, ys)

# ---------------- arrangement ----------------
SEC = [('cold_open', 1, 3), ('hook', 4, 6), ('energise_drop1', 7, 12), ('excite_breakdown', 13, 18),
       ('excel_drop2', 19, 24), ('outro', 25, 27)]
def section(b):
    for n, a, z in SEC:
        if a <= b <= z: return n
PROG = ['Am'] * 3 + ['Am', 'F', 'G'] + ['Am', 'F', 'C', 'G', 'F', 'G'] * 3 + ['C'] * 3
CH = {'Am': [57, 60, 64, 71], 'F': [53, 57, 60, 64, 67], 'C': [55, 60, 64, 67, 74], 'G': [55, 59, 62, 67, 69]}
ROOT = {'Am': 33, 'F': 29, 'C': 36, 'G': 31}
ARP = {'Am': [69, 72, 76, 81], 'F': [69, 72, 77, 81], 'C': [67, 72, 76, 79], 'G': [67, 71, 74, 79]}

# ---------------- instruments ----------------
def kick():
    n = S(0.45); tt = np.arange(n) / SR
    f = 46 + 130 * np.exp(-tt / 0.03) + 60 * np.exp(-tt / 0.004)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.where(tt < 0.025, 1.0, np.exp(-(tt - 0.025) / 0.2))
    click = hp(rng.standard_normal(n), 3000) * np.exp(-tt / 0.0025) * 0.5
    k = np.tanh(2.2 * (body + click)) / np.tanh(2.2); k[-S(0.03):] *= np.linspace(1, 0, S(0.03))
    return k
def soft_kick(): return lp(kick(), 700) * 0.6
def snare():
    n = S(0.5); tt = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 1200, 9000) * np.exp(-tt / 0.07)
    body = np.sin(2 * np.pi * (185 + 60 * np.exp(-tt / 0.01)) * tt) * np.exp(-tt / 0.06)
    env = np.zeros(n)
    for d in (0, 0.008, 0.017):
        x = tt - d; env += np.where(x >= 0, np.exp(-np.maximum(x, 0) / 0.006), 0)
    clp = bp(rng.standard_normal(n), 900, 5000) * (env + np.where(tt > .017, .5 * np.exp(-(tt - .017) / .1), 0))
    return np.tanh(1.5 * (nz * 0.7 + body * 0.8 + clp * 0.6))
def ohat():
    n = S(0.24); tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7500, 4) * np.exp(-tt / 0.075) * np.minimum(1, tt / 0.002)
def chat():
    n = S(0.06); tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 9000, 4) * np.exp(-tt / 0.016)
def shaker():
    n = S(0.09); tt = np.arange(n) / SR
    return bp(rng.standard_normal(n), 5000, 12000) * np.sin(np.pi * np.clip(tt / 0.07, 0, 1)) ** 2
def taiko(f0=62, dec=0.55):
    n = S(1.4); tt = np.arange(n) / SR
    f = f0 + f0 * 0.6 * np.exp(-tt / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / dec)
    skin = bp(rng.standard_normal(n), 150, 1800) * np.exp(-tt / 0.05) * 0.6
    return np.tanh(1.8 * (body + skin))
def tick(hi=True):
    n = S(0.03); tt = np.arange(n) / SR
    f = 3200 if hi else 2400
    return (np.sin(2 * np.pi * f * tt) * 0.6 + hp(rng.standard_normal(n), 4000) * 0.5) * np.exp(-tt / 0.004)
def pluck(m, dur=0.18, bright=1.0):
    f = mtof(m); n = S(dur + 0.3); tt = np.arange(n) / SR; out = np.zeros(n)
    for k in range(1, 30):
        if k * f > 15000: break
        d = np.exp(-tt * (5 + k * 2.4 / bright)) / k
        out += (np.sin(2 * np.pi * k * f * tt) + 0.5 * np.sin(2 * np.pi * k * f * 1.005 * tt)) * d
    out *= np.minimum(1, tt / 0.0015) * (1 - np.clip((tt - dur) / 0.25, 0, 1)) ** 2
    return out * 0.3
def piano(m, dur=1.2):
    f = mtof(m); n = S(dur + 0.6); tt = np.arange(n) / SR; out = np.zeros(n); B = 0.0004
    for k in range(1, 16):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 12000: break
        amp = 1 / k ** 1.1; d = np.exp(-tt * (0.9 + 0.55 * k)) * 0.7 + np.exp(-tt * (3 + 1.2 * k)) * 0.3
        out += amp * np.sin(2 * np.pi * fk * tt + k) * d
    out += bp(rng.standard_normal(n), 1500, 6000) * np.exp(-tt / 0.004) * 0.08
    out *= np.minimum(1, tt / 0.001) * (1 - np.clip((tt - dur) / 0.5, 0, 1))
    return out * 0.3
def ens(m, dur, att, rel, voices=7, detune=16, spread=0.9, vib=0.0):
    """detuned saw ensemble (strings / pads / supersaw), stereo"""
    f = mtof(m); n = S(dur + rel); tt = np.arange(n) / SR; o = np.zeros((n, 2))
    for i in range(voices):
        c = (i - (voices - 1) / 2) / ((voices - 1) / 2) * detune
        fv = f * 2 ** (c / 1200) * (1 + vib * np.sin(2 * np.pi * (5.2 + 0.3 * i) * tt + i))
        s = saw(fv, n, rng.uniform()); pn = (i - (voices - 1) / 2) / ((voices - 1) / 2) * spread
        o += pan2(s, pn) / 1.414
    env = np.minimum(1, tt / att) * np.where(tt > dur, np.clip(1 - (tt - dur) / rel, 0, 1), 1) ** 2
    return o * env[:, None] / voices * 0.9
def bass_note(m, dur, cutoff=500):
    f = mtof(m); n = S(dur + 0.02); tt = np.arange(n) / SR
    s = lp(saw(f, n) + 0.6 * saw(f * 1.004, n), cutoff, 2)
    env = np.minimum(1, tt / 0.003) * np.where(tt > dur, np.clip(1 - (tt - dur) / 0.02, 0, 1), 1)
    return (np.sin(2 * np.pi * f * tt) * 0.8 + s * 0.5) * env
def braam(notes, dur=3.2):
    """trailer brass hit: big detuned saw stack, fast filter bloom, growl, saturation"""
    n = S(dur); tt = np.arange(n) / SR; o = np.zeros((n, 2))
    for m in notes:
        o += ens(m, dur - 0.6, 0.012, 0.6, voices=9, detune=22, spread=1.0)[:n] * (1.3 if m < 45 else 1.0)
    env_f = np.clip(np.minimum(tt / 0.06, 1) * np.exp(-tt / 0.9) + 0.12, 0, 1)
    o = sweep_lp(o, env_f, 120, 4200, 8)
    growl = 1 + 0.25 * np.sin(2 * np.pi * 28 * tt) * np.exp(-tt / 0.7)
    amp = np.minimum(1, tt / 0.01) * (0.55 + 0.45 * np.exp(-tt / 0.5)) * np.clip((dur - tt) / 1.2, 0, 1)
    o = np.tanh(2.5 * o * (growl * amp)[:, None]) / 1.5
    return o
def subdrop(dur=2.2, f0=95, f1=27):
    n = S(dur); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt / 0.35)
    return np.tanh(1.4 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-tt / 0.9) * np.minimum(1, tt / 0.003)
def impact(dur=2.5, depth=1.0):
    n = S(dur); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(32 + 55 * np.exp(-tt / 0.07)) / SR) * np.exp(-tt / 0.6)
    crack = bp(rng.standard_normal(n), 400, 6000) * np.exp(-tt / 0.03) * 0.8
    tail = hp(rng.standard_normal(n), 3500) * np.exp(-tt / 0.8) * 0.25
    return np.tanh(1.6 * (boom * depth + crack + tail)) * 0.9
def crash(dur=2.4):
    n = S(dur); tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 4500, 3) * np.exp(-tt / 0.75) * np.minimum(1, tt / 0.001) * 0.3
def sweep_noise(dur, f0, f1, width=1.0):
    n = S(dur); W = 2048; H = W // 2; win = np.hanning(W)
    out = np.zeros(n + W); nz = rng.standard_normal(n + W); fr = np.fft.rfftfreq(W, 1 / SR)
    for i in range(0, n, H):
        fc = f0 * (f1 / f0) ** (i / n)
        mask = np.exp(-0.5 * (np.log2(np.maximum(fr, 1) / fc) / (0.6 * width)) ** 2)
        out[i:i + W] += np.fft.irfft(np.fft.rfft(nz[i:i + W] * win) * mask) * win
    out = out[:n]; return out / (np.abs(out).max() + 1e-9)
def riser(dur, base=57):
    n = S(dur); tt = np.arange(n) / SR; x = tt / dur
    nz = sweep_noise(dur, 300, 10000)
    f = mtof(base) * 2 ** (2 * x ** 1.6)
    ton = sum(np.sin(2 * np.pi * np.cumsum(f * r) / SR) * a for r, a in ((1, .5), (1.5, .3), (2.01, .25)))
    out = (nz * 0.8 + ton * 0.25) * x ** 2.4
    return np.stack([out, np.roll(out, 240)], 1)
def make_ir(length, decay, lpf, pre, seed):
    r = np.random.default_rng(seed); n = S(length); tt = np.arange(n) / SR; ir = np.zeros((n, 2))
    for c in range(2): ir[:, c] = lp(r.standard_normal(n) * np.exp(-tt / decay), lpf)
    ir[:S(pre)] = 0; return ir / np.sqrt((ir ** 2).sum(0)).max()
def conv(x, ir, n=None):
    n = n or len(x)
    return np.stack([fftconvolve(x[:, c], ir[:, c])[:n] for c in range(2)], 1)

# ---------------- buses ----------------
kicks, drums, perc, bass, pads, strings, keys, lead, fx, sub = (stereo() for _ in range(10))
plate_send, hall_send = stereo(), stereo()
kick_times = []
KD, KS, SN = kick(), soft_kick(), snare()
DROPS = ('energise_drop1', 'excel_drop2')

for b in range(1, NBARS + 1):
    sec = section(b); t0 = bar_t(b); ch = PROG[b - 1]; r = ROOT[ch]
    last_bar_of_sec = b in (3, 6, 12, 18, 24, 27)
    # ---- cold open: drone + ticking clock + heartbeat
    if sec == 'cold_open':
        x0 = (b - 1) / 3
        for e in range(8):
            te = t0 + e * BEAT / 2; x = x0 + e / 24
            add(perc, tick(e % 2 == 0), te, 0.10 + 0.5 * x ** 1.3, 0.35 if e % 2 else -0.35)
            if b == 3: add(perc, tick(False), te + BEAT / 4, 0.25 + 0.3 * e / 8, 0.5)
            add(hall_send, pan2(tick(e % 2 == 0), 0), te, 0.08 * x)
        if b >= 2:
            for q in range(4):
                add(sub, KS, t0 + q * BEAT, 0.25 + 0.25 * (b - 2) + 0.05 * q)
                if q in (0, 2): add(sub, KS * 0.6, t0 + q * BEAT + 0.16, 0.2 + 0.15 * (b - 2))
    # ---- hook: low strings + soft pulse
    if sec == 'hook':
        for q in range(8):
            add(bass, lp(bass_note(r + 12, 0.16, 300), 250), t0 + q * BEAT / 2, 0.30 + 0.05 * (b - 4))
        add(sub, KS, t0, 0.45); add(sub, KS, t0 + 2 * BEAT, 0.35)
        for e in range(8): add(perc, tick(e % 2 == 0), t0 + e * BEAT / 2, 0.12, 0.35 if e % 2 else -0.35)
    # ---- drums in drops
    if sec in DROPS:
        d2 = sec == 'excel_drop2'
        for q in range(4):
            tb = t0 + q * BEAT
            gap = last_bar_of_sec and q == 3 and not d2   # silent beat before breakdown
            if not gap: add(kicks, KD, tb, 1.0); kick_times.append(tb)
            if q in (1, 3) and not gap:
                add(drums, SN, tb, 0.6); add(plate_send, pan2(SN, 0), tb, 0.45)
            add(drums, ohat(), tb + BEAT / 2, 0.28, 0.2)
            for s16 in (1, 3): add(drums, chat(), tb + s16 * BEAT / 4, 0.14 if s16 == 1 else 0.1, -0.3)
            if d2:
                for s16 in range(4): add(perc, shaker(), tb + s16 * BEAT / 4, 0.10 + 0.05 * (s16 % 2), 0.55)
            # octave bass on 8ths (root / octave), sidechained
            for e in (0, 1):
                if gap: continue
                m = r + 12 * e + (12 if d2 and e == 1 and q % 2 else 0)
                add(bass, bass_note(m, 0.2 if e == 0 else 0.18, 650 if d2 else 520), tb + e * BEAT / 2, 0.6)
        # taiko on bar starts (+ beat 3 'and' pickup)
        add(perc, taiko(60), t0, 0.75, -0.1); add(hall_send, pan2(taiko(60), 0), t0, 0.25)
        add(perc, taiko(78, 0.35), t0 + 2.5 * BEAT, 0.45 if not d2 else 0.6, 0.3)
        if d2: add(perc, taiko(95, 0.3), t0 + 3 * BEAT, 0.4, -0.4); add(perc, taiko(95, 0.3), t0 + 3.5 * BEAT, 0.45, 0.4)
        # pluck arp 16ths
        pat = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 3, 1, 2]
        for s16, ix in enumerate(pat):
            m = ARP[ch][ix]
            add(keys, pluck(m, 0.12, 1.0), t0 + s16 * BEAT / 4, 0.55 if s16 % 4 == 0 else 0.42, 0.25 if s16 % 2 else -0.25)
            if d2: add(keys, pluck(m + 12, 0.09, 1.2), t0 + s16 * BEAT / 4, 0.2, -0.5 if s16 % 2 else 0.5)
        # wide chords
        for m in CH[ch]:
            p = ens(m, BAR, 0.02, 0.35, voices=7, detune=20, spread=1.0); add(pads, p, t0, 0.9); add(hall_send, p, t0, 0.15)
        # strings octave doubling in drop 2
        if d2:
            for m in CH[ch][:3]:
                add(strings, ens(m - 12, BAR, 0.08, 0.4, 7, 10, 0.9, vib=0.003), t0, 0.5)
    # ---- low strings / pads in hook, cold, breakdown
    if sec in ('hook', 'excite_breakdown'):
        for m in CH[ch][:3]:
            s = ens(m - 12, BAR, 0.5, 0.6, 7, 9, 0.9, vib=0.0025); add(strings, s, t0, 0.8); add(hall_send, s, t0, 0.3)
    if sec == 'cold_open' and b == 1:
        for m in (33, 45):
            s = ens(m, 3 * BAR - 0.1, 2.5, 0.3, 7, 8, 0.7); add(strings, s, t0, 1.0); add(hall_send, s, t0, 0.2)
    # ---- breakdown: piano, pad, soft pulse, kicks enter bar 17-18
    if sec == 'excite_breakdown':
        notes = ARP[ch]
        for e, ix in enumerate([0, 2, 1, 3, 2, 1, 3, 2]):
            if e in (5, 7) and b < 17: continue
            pn = piano(notes[ix] - 12 if ix < 2 else notes[ix], 0.5)
            add(keys, pn, t0 + e * BEAT / 2, 0.55, 0.3 if ix % 2 else -0.3)
        add(keys, piano(r + 24, 1.6), t0, 0.5)
        for q in range(4):
            add(bass, lp(bass_note(r + 12, 0.18, 280), 240), t0 + q * BEAT, 0.3)
            add(bass, lp(bass_note(r + 12, 0.12, 280), 240), t0 + q * BEAT + BEAT / 2, 0.2)
        if b >= 17:
            for q in range(4):
                if b == 18 and q == 3: continue
                add(kicks, KS, t0 + q * BEAT, 0.5 + 0.2 * (b - 17)); kick_times.append(t0 + q * BEAT)
        for e in range(8): add(perc, shaker(), t0 + e * BEAT / 2 + BEAT / 4, 0.06, 0.5)

# ---- soaring lead in drop 2 (strings + supersaw)
LEAD = [(0, 76, 1.5), (1.5, 74, .5), (2, 72, 2), (4, 72, 1), (5, 74, 1), (6, 76, 2), (8, 79, 3), (11, 76, 1),
        (12, 74, 2), (14, 71, 1), (15, 74, 1), (16, 72, 1.5), (17.5, 76, .5), (18, 77, 2), (20, 79, 2), (22, 83, 2)]
for rep, base in enumerate((19, 19)):
    if rep: break
    for bt, m, dl in LEAD:
        st = bar_t(base) + bt * BEAT
        nt = ens(m, dl * BEAT - 0.02, 0.03, 0.25, 7, 14, 0.7, vib=0.004); add(lead, nt, st, 0.65); add(hall_send, nt, st, 0.35)
        nt2 = ens(m - 12, dl * BEAT - 0.02, 0.06, 0.3, 5, 8, 0.5, vib=0.003); add(lead, nt2, st, 0.45)
    # repeat second half of phrase as answer (bars 22-24 get full phrase again, an octave-stacked)
for bt, m, dl in LEAD:
    st = bar_t(22) + bt * BEAT
    if st >= bar_t(25): break
    nt = ens(m + 12, dl * BEAT - 0.02, 0.03, 0.25, 7, 12, 0.7, vib=0.004); add(lead, nt, st, 0.35); add(hall_send, nt, st, 0.25)

# ---- FX & hits
HITS = [5.76, 11.52, 23.04, 34.56, 46.08]
# cold open reverse swell into 5.76 (reversed hall of a braam + noise riser)
bra = braam([33, 45, 52, 57, 60])
rev = conv(np.pad(bra[:S(0.5)], ((0, S(3)), (0, 0))), make_ir(3.0, 0.9, 6000, 0.0, 3))[::-1]
rev = rev[-S(2.6):] / np.abs(rev).max()
rev *= np.linspace(0, 1, len(rev))[:, None] ** 2.5
add(fx, rev, HITS[0] - len(rev) / SR, 0.7)
add(fx, riser(2 * BAR, 45), HITS[0] - 2 * BAR, 0.4)
# 5.76: BRAAM + sub drop + impact
add(fx, bra, HITS[0], 1.0); add(hall_send, bra, HITS[0], 0.35)
add(sub, pan2(subdrop(), 0), HITS[0], 0.9); add(fx, pan2(impact(), 0), HITS[0], 0.6); add(fx, pan2(crash(), 0), HITS[0], 0.5)
# riser into 11.52 + snare roll
add(fx, riser(BAR * 1.5), HITS[1] - BAR * 1.5, 0.5)
def roll(ts, te, g0, g1):
    tt_ = ts
    while tt_ < te - 1e-6:
        x = (tt_ - ts) / (te - ts); add(drums, SN, tt_, g0 + (g1 - g0) * x); add(plate_send, pan2(SN, 0), tt_, 0.2 * x)
        tt_ += BEAT / 4 if x < 0.5 else BEAT / 8
roll(HITS[1] - BAR / 2, HITS[1], 0.1, 0.45)
add(fx, pan2(impact(), 0), HITS[1], 0.85); add(fx, pan2(crash(), 0), HITS[1], 0.8); add(sub, pan2(subdrop(1.6, 80, 32), 0), HITS[1], 0.6)
add(fx, pan2(crash(), 0), bar_t(10), 0.5)
# 23.04 breakdown: reverse cymbal + soft impact
rc = crash()[::-1][-S(BEAT * 2):]
add(fx, pan2(rc, 0), HITS[2] - BEAT * 2, 0.7); add(fx, pan2(impact(2.2, 0.8), 0), HITS[2], 0.55)
add(hall_send, pan2(impact(2.2, 0.8), 0), HITS[2], 0.3)
# riser over last 2 bars into 34.56 + roll
add(fx, riser(2 * BAR, 57), HITS[3] - 2 * BAR, 0.6); roll(HITS[3] - BAR, HITS[3], 0.1, 0.55)
add(fx, rc, HITS[3] - 2 * BEAT, 0.5)
# 34.56 big drop 2 hit: braam + impact + sub drop + crash
bra2 = braam([33, 45, 52, 57, 64], 2.6)
add(fx, bra2, HITS[3], 0.75); add(fx, pan2(impact(), 0), HITS[3], 1.0); add(fx, pan2(crash(), 0), HITS[3], 0.9)
add(sub, pan2(subdrop(1.8), 0), HITS[3], 0.75); add(fx, pan2(crash(), 0), bar_t(22), 0.6)
# riser + roll into 46.08
add(fx, riser(BAR, 60), HITS[4] - BAR, 0.45); roll(HITS[4] - BAR / 2, HITS[4], 0.15, 0.5)
add(fx, rc, HITS[4] - 2 * BEAT, 0.5)
# 46.08 final BRAAM on C, then sustained C major lift chord with long tail
bra3 = braam([36, 48, 55, 60, 64], 3.8)
add(fx, bra3, HITS[4], 1.0); add(hall_send, bra3, HITS[4], 0.5)
add(fx, pan2(impact(3.0), 0), HITS[4], 0.8); add(sub, pan2(subdrop(2.6, 90, 30), 0), HITS[4], 0.8)
add(fx, pan2(crash(3.0), 0), HITS[4], 0.7)
tail_d = DUR - HITS[4]
for m, g in ((48, .8), (55, .7), (60, .7), (64, .65), (67, .55), (72, .5), (74, .35), (76, .4)):
    s = ens(m, tail_d - 1.5, 0.35, 1.5, 7, 10, 1.0, vib=0.002); add(strings, s, HITS[4], g * 0.9); add(hall_send, s, HITS[4], 0.5 * g)
for m in (72, 76, 79, 84):
    add(keys, piano(m, 3.0), HITS[4] + 0.02, 0.45); add(hall_send, pan2(piano(m, 3.0), 0), HITS[4], 0.4)
add(bass, pan2(np.sin(2 * np.pi * mtof(36) * np.arange(S(tail_d)) / SR) * np.exp(-np.arange(S(tail_d)) / SR / 2.2), 0), HITS[4], 0.5)

# ---------------- processing ----------------
sc = np.ones(N)
for kt in kick_times:
    i = S(kt); j = min(N, i + S(0.3)); dt = np.arange(j - i) / SR
    depth = 0.8 if section(int(round(kt / BAR, 6) // 1) + 1) in DROPS else 0.4
    sc[i:j] = np.minimum(sc[i:j], 1 - depth * (1 - np.clip(dt / 0.25, 0, 1)) ** 2)
sc = uniform_filter1d(sc, S(0.003))[:, None]
bass *= sc; pads *= sc; strings *= (0.35 + 0.65 * sc); keys *= (0.6 + 0.4 * sc); lead *= (0.6 + 0.4 * sc)

# pad brightness automation (open on risers, bright in drops)
bright = curve([(0, 0), (bar_t(7) - 0.01, 0.3), (bar_t(7), 1), (bar_t(13) - .01, 1), (bar_t(13), .1), (bar_t(17), .1),
                (bar_t(19) - .01, .7), (bar_t(19), 1), (DUR, 1)])
pads = sweep_lp(pads, bright, 600, 6000, 6)
strings = sweep_lp(strings, curve([(0, .1), (bar_t(4), .25), (bar_t(19), .6), (bar_t(25), .7), (DUR, .25)]), 300, 5000, 6)
lead = lp(lead, 7000)
keys = hp(keys, 180)
# dotted-8th ping-pong delay on keys
d = S(0.75 * BEAT); src = lp(keys, 4500) * 0.3; dl = np.zeros_like(keys)
for k in range(1, 5):
    off = d * k; c = k % 2; dl[off:, c] += src[:-off, 1 - c] * 0.55 ** (k - 1)
keys += dl
# reverbs: bright plate for snare, long hall for everything cinematic
plate = hp(conv(plate_send, make_ir(1.8, 0.45, 9000, 0.008, 5)), 250) * 0.55
hall = hp(conv(hall_send + lead * 0.2 + keys * 0.2, make_ir(5.5, 1.5, 4200, 0.03, 9)), 180) * 0.6
# mid/side width on pads & strings
def widen(x, w):
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2 * w; return np.stack([m + s, m - s], 1)
pads = widen(pads, 1.5); strings = widen(strings, 1.3)
# mono low end
low = lp(bass + sub, 120); bass_m = (low[:, :1] + low[:, 1:]) / 2
bass = (bass + sub - low) + bass_m

drum_bus = kicks * 1.0 + drums * 0.75 + perc * 0.7
drum_bus = np.tanh(drum_bus * 1.3) / 1.3     # glue saturation
mix = drum_bus + bass * 0.85 + pads * 0.55 + strings * 0.7 + keys * 0.6 + lead * 0.6 + fx * 0.75 + plate + hall

# voice pocket: -8 dB at 1-4 kHz under speech (hook + excite breakdown)
pocket = curve([(0, 0), (HITS[0] - 0.01, 0), (HITS[0] + 0.25, 0.6), (HITS[1] - 0.25, 0.6), (HITS[1], 0),
                (HITS[2], 0), (HITS[2] + 0.3, 0.6), (HITS[3] - 0.35, 0.6), (HITS[3], 0), (DUR, 0)])
band = sosfiltfilt(butter(2, [1000, 4000], 'band', fs=SR, output='sos'), mix, axis=0)
mix = mix - band * pocket[:, None]

# master
mix = hp(mix, 25)
fade = curve([(0, 0), (0.6, 1), (HITS[4] + 1.5, 1), (DUR - 0.02, 0), (DUR, 0)])
fade = np.where(t < 1, fade ** 2, fade ** 1.8)
mix *= fade[:, None]
meter = pyln.Meter(SR); CEIL = 10 ** (-1.4 / 20)
def limit(x):
    up = resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(x)]
    g0 = np.minimum(1, CEIL / np.maximum(pk, 1e-9))
    g = uniform_filter1d(minimum_filter1d(g0, S(0.01)), S(0.005))
    g = np.minimum(g, minimum_filter1d(g0, 5))
    return x * g[:, None]
mix /= np.abs(mix).max()
for it in range(5):
    L = meter.integrated_loudness(mix); mix *= 10 ** ((-14.0 - L) / 20); mix = limit(mix)
mix = np.clip(mix, -CEIL, CEIL)
print('LUFS:', round(meter.integrated_loudness(mix), 2), 'sample peak dB', round(20 * np.log10(np.abs(mix).max()), 2))
for n_, a, z in SEC:
    seg = mix[S(bar_t(a)):S(bar_t(z + 1))]
    print(f'  {n_:18s} {bar_t(a):6.2f}-{bar_t(z+1):6.2f}  {meter.integrated_loudness(seg):6.2f} LUFS')

pcm = (mix * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
grid = {
    'bpm': BPM, 'beat': BEAT, 'bar': BAR, 'offset': 0.0, 'duration': DUR, 'key': 'A minor -> C major (outro)',
    'beats': [round(i * BEAT, 4) for i in range(NBARS * 4)],
    'bars': [round(i * BAR, 4) for i in range(NBARS)],
    'sections': [{'name': n_, 'start': round(bar_t(a), 4), 'end': round(bar_t(z + 1), 4), 'bars': [a, z]} for n_, a, z in SEC],
    'hits': HITS,
    'hitsDetail': [
        {'t': 5.76, 'what': 'reverse swell -> BRAAM + sub drop + impact (title reveal)'},
        {'t': 11.52, 'what': 'riser + snare roll -> impact + crash: drop 1 (ENERGISE)'},
        {'t': 23.04, 'what': 'reverse cymbal -> soft impact: breakdown (EXCITE); beat 22.56 is a silent gap'},
        {'t': 34.56, 'what': '2-bar riser + roll -> BRAAM + big impact + crash: drop 2 (EXCEL)'},
        {'t': 46.08, 'what': 'final BRAAM on C + impact, C major chord, reverb tail to silence at 51.84'}],
    'kickTimes': [round(k, 4) for k in kick_times],
    'chords': PROG,
    'notes': 'Voice pocket (1-4 kHz -8 dB): hook 5.76-11.52, breakdown 23.04-34.56. Ticking clock on 8ths 0-5.76.',
}
json.dump(grid, open(sys.argv[2], 'w'), indent=1)
