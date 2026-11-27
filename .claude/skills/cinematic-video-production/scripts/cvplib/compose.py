"""Original instrumental music composed to an edit's structure (numpy synthesis, no samples, project-owned).

Arrangement is a list of sections in bars; each switches instruments on/off. The exact beat grid and section
times are known, so the beat map is written from the plan (plus the usual analysis for checking).
"""
import json, subprocess, wave
from pathlib import Path
from .common import active_project, rj, wj, now, slug, sha256, die

SR = 48000
PROG = [  # vi - IV - I - V in D major (uplifting corporate/anthemic)
    {"bass": 35, "pad": [59, 62, 66, 71]},   # Bm(add11)
    {"bass": 31, "pad": [55, 59, 62, 69]},   # Gadd9
    {"bass": 38, "pad": [57, 62, 66, 69]},   # D
    {"bass": 33, "pad": [57, 61, 64, 71]},   # Aadd9
]
MOTIF = [  # (bar in 4-bar loop, beat, midi, beats)
    (0, 0, 74, 1), (0, 1, 76, 1), (0, 2, 78, 2),
    (1, 0, 79, 1), (1, 1, 78, 1), (1, 2, 74, 2),
    (2, 0, 74, 1), (2, 1, 76, 1), (2, 2, 78, 1), (2, 3, 81, 1),
    (3, 0, 76, 3), (3, 3, 73, 1),
]
PRESETS = {
    # name: bars, and which parts play. energy 0..1 drives filter brightness.
    "intro": dict(piano=1, pad=0.5, energy=0.25),
    "build": dict(piano=1, pad=0.8, arp=1, hats="closed", kick="half", bass="root", energy=0.55, riser=1),
    "drop": dict(pad=1, arp=1, lead=1, hats="open", kick="four", clap=1, bass="octave", energy=1.0, impact=1),
    "break": dict(piano=1, pad=0.7, arp=0.6, energy=0.4),
    "lift": dict(pad=0.9, arp=1, hats="closed", kick="four", bass="root", energy=0.7, riser=1),
    "outro": dict(pad=0.8, piano=1, energy=0.3, impact=1, tail=1),
    "sting": dict(pad=1, impact=1, energy=0.8, tail=1),
}


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _rng(seed):
    import numpy as np
    return np.random.default_rng(seed)


def polyblep_saw(f, n, phase0=0.0):
    import numpy as np
    dt = f / SR
    t = (phase0 + dt * np.arange(n)) % 1.0
    y = 2 * t - 1
    m = t < dt
    x = t[m] / dt
    y[m] -= x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt
    y[m] -= x * x + x + x + 1
    return y


def env(n, a, d, s, r, total=None):
    """ADSR in seconds -> array of length n (note held for n - r samples)."""
    import numpy as np
    e = np.full(n, s, dtype=np.float64)
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = min(A, n); e[:A] = np.linspace(0, 1, A, endpoint=False) if A else e[:A]
    D2 = min(D, max(0, n - A)); e[A:A + D2] = np.linspace(1, s, D2, endpoint=False) if D2 else e[A:A + D2]
    R = min(R, n)
    if R:
        e[n - R:] *= np.linspace(1, 0, R)
    return e


def stft_filter(x, cut_lo, cut_hi, nfft=2048, hop=512):
    """Time-varying band filter. cut_lo/cut_hi: callables frame_time->Hz (or numbers)."""
    import numpy as np
    win = np.sqrt(np.hanning(nfft + 1)[:-1])
    pad = np.concatenate([np.zeros(nfft), x, np.zeros(nfft)])
    nfr = 1 + (len(pad) - nfft) // hop
    idx = np.arange(nfft)[None, :] + hop * np.arange(nfr)[:, None]
    X = np.fft.rfft(pad[idx] * win, axis=1)
    f = np.fft.rfftfreq(nfft, 1 / SR)[None, :]
    tt = (np.arange(nfr) * hop - nfft) / SR
    lo = np.asarray([cut_lo(t) if callable(cut_lo) else cut_lo for t in tt])[:, None]
    hi = np.asarray([cut_hi(t) if callable(cut_hi) else cut_hi for t in tt])[:, None]
    mask = (1 / (1 + (f / np.maximum(hi, 1)) ** 4)) * (1 - 1 / (1 + (f / np.maximum(lo, 1)) ** 4) if True else 1)
    mask = np.where(lo <= 1, 1 / (1 + (f / np.maximum(hi, 1)) ** 4), mask)
    Y = np.fft.irfft(X * mask, n=nfft, axis=1) * win
    out = np.zeros(len(pad))
    np.add.at(out, idx, Y)  # overlap-add
    norm = np.zeros(len(pad))
    np.add.at(norm, idx, np.broadcast_to(win ** 2, Y.shape))
    out /= np.maximum(norm, 1e-6)
    return out[nfft:nfft + len(x)]


def reverb(x, seconds=2.2, seed=7, wet=0.25):
    import numpy as np
    r = _rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    outs = []
    for ch in range(2):
        ir = r.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt((ir ** 2).sum())
        L = len(x) + n
        N = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[: len(x)]
        outs.append(y)
    return np.stack([x * (1 - wet) + wet * outs[0] * 3, x * (1 - wet) + wet * outs[1] * 3])


def render_track(plan, bpm, seed=1, tail_s=2.5):
    import numpy as np
    rng = _rng(seed)
    beat = 60.0 / bpm
    bar = 4 * beat
    total_bars = sum(s["bars"] for s in plan)
    length = int((total_bars * bar + tail_s) * SR)
    stems = {k: np.zeros(length) for k in ("kick", "clap", "hats", "bass", "pad", "arp", "lead", "piano", "fx")}
    padS = np.zeros((2, length))
    pump = np.ones(length)
    sections, t0 = [], 0.0
    kick_times = []

    def put(stem, start_s, sig):
        i = int(start_s * SR)
        if i >= length:
            return
        j = min(length, i + len(sig))
        stems[stem][i:j] += sig[: j - i]

    for si, sec in enumerate(plan):
        p = {**PRESETS.get(sec.get("type", "drop"), {}), **sec}
        sections.append({"name": sec.get("name", p.get("type")), "type": p.get("type"), "t": round(t0, 3), "bars": sec["bars"]})
        for b in range(sec["bars"]):
            bt = t0 + b * bar
            ch = PROG[(sec.get("chord_offset", 0) + b) % 4]
            # kick
            kmode = p.get("kick")
            beats = [0, 1, 2, 3] if kmode == "four" else [0, 2] if kmode == "half" else []
            if p.get("riser") and b == sec["bars"] - 1 and kmode:
                beats = [0, 1, 2, 3, 3.5] if kmode == "four" else [0, 1, 2, 2.5, 3, 3.25, 3.5, 3.75]
            for k in beats:
                n = int(0.42 * SR); tt = np.arange(n) / SR
                f = 46 + 110 * np.exp(-tt * 38)
                sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7.5)
                sig[:120] += rng.standard_normal(120) * np.linspace(0.6, 0, 120)
                put("kick", bt + k * beat, sig * (0.75 if k % 1 else 1.0))
                kick_times.append(bt + k * beat)
            # clap on 2 and 4
            if p.get("clap"):
                for k in (1, 3):
                    n = int(0.3 * SR); tt = np.arange(n) / SR
                    nz = rng.standard_normal(n)
                    e = sum(np.exp(-np.maximum(tt - d, 0) * 55) * (tt >= d) for d in (0, 0.011, 0.022)) + 0.6 * np.exp(-tt * 14)
                    put("clap", bt + k * beat, nz * e * 0.5 + np.sin(2 * np.pi * 185 * tt) * np.exp(-tt * 30) * 0.4)
            # hats
            if p.get("hats"):
                for k in range(8):
                    off = k % 2 == 1
                    if p["hats"] == "closed" or not off:
                        n = int(0.05 * SR); dec = 70
                    else:
                        n = int(0.25 * SR); dec = 13
                    tt = np.arange(n) / SR
                    put("hats", bt + k * beat / 2, rng.standard_normal(n) * np.exp(-tt * dec) * (0.55 if off else 0.3))
            # bass (8ths)
            if p.get("bass"):
                for k in range(8):
                    m = ch["bass"] + (12 if p["bass"] == "octave" and k % 2 else 0)
                    n = int(beat / 2 * SR * 0.92)
                    sig = polyblep_saw(hz(m), n) * 0.6 + np.sin(2 * np.pi * hz(m) * np.arange(n) / SR) * 0.6
                    put("bass", bt + k * beat / 2, sig * env(n, 0.004, 0.08, 0.7, 0.03))
            # pad (whole bar, supersaw, stereo)
            lvl = p.get("pad", 0)
            if lvl:
                n = int(bar * SR * 1.02)
                for ci, side in enumerate((-1, 1)):
                    acc = np.zeros(n)
                    for m in ch["pad"]:
                        for dv in (-14, -6, 0, 7, 13):
                            acc += polyblep_saw(hz(m) * 2 ** ((dv * side * 0.7) / 1200), n, rng.random())
                    acc *= env(n, 0.25 if p.get("type") in ("intro", "break") else 0.04, 0.3, 0.85, 0.2) * lvl * 0.06
                    i = int(bt * SR); j = min(length, i + n)
                    padS[ci, i:j] += acc[: j - i]
            # arp (16ths, ping-pong handled in mix)
            if p.get("arp"):
                notes = [x + 12 for x in ch["pad"]]
                order = [0, 1, 2, 3, 2, 1, 2, 3] * 2
                for k in range(16):
                    n = int(beat / 4 * SR * 1.6)
                    tt = np.arange(n) / SR
                    f = hz(notes[order[k]])
                    sig = (polyblep_saw(f, n) * 0.5 + np.sign(np.sin(2 * np.pi * f * tt)) * 0.3) * np.exp(-tt * 16)
                    put("arp", bt + k * beat / 4, sig * 0.22 * p.get("arp", 1))
            # piano-ish (broken chord quarters)
            if p.get("piano"):
                for k in range(4):
                    m = ch["pad"][[0, 2, 1, 3][k]] + 12
                    n = int(beat * 2.5 * SR); tt = np.arange(n) / SR
                    f = hz(m)
                    sig = sum(np.sin(2 * np.pi * f * h * tt) * a * np.exp(-tt * (2.2 + h * 1.5)) for h, a in ((1, 1), (2, .45), (3, .2), (4, .1)))
                    sig[:200] *= np.linspace(0, 1, 200)
                    put("piano", bt + k * beat, sig * 0.32)
            # lead motif
            if p.get("lead"):
                lb = (sec.get("chord_offset", 0) + b) % 4
                for (mb, mbeat, m, dur) in MOTIF:
                    if mb != lb:
                        continue
                    n = int(dur * beat * SR); tt = np.arange(n) / SR
                    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * tt) * np.clip(tt * 3, 0, 1)
                    ph = np.cumsum(hz(m) * vib) / SR
                    sig = (np.sin(2 * np.pi * ph) * 0.6 + np.sin(4 * np.pi * ph) * 0.2 + (2 * (ph % 1) - 1) * 0.18)
                    put("lead", bt + mbeat * beat, sig * env(n, 0.01, 0.15, 0.7, 0.08) * 0.3)
        # riser over the last bar(s), impact on section start
        if p.get("riser"):
            rb = min(2, sec["bars"])
            n = int(rb * bar * SR); tt = np.arange(n) / SR
            T = rb * bar
            nz = stft_filter(rng.standard_normal(n), lambda t: 300 + 5000 * max(0, t) / T, lambda t: 1200 + 9000 * max(0, t) / T)
            put("fx", t0 + (sec["bars"] - rb) * bar, nz * (tt / T) ** 2 * 0.35 + np.sin(2 * np.pi * np.cumsum(200 + 900 * (tt / T) ** 2) / SR) * (tt / T) ** 3 * 0.08)
        if p.get("impact"):
            n = int(2.2 * SR); tt = np.arange(n) / SR
            boom = np.sin(2 * np.pi * np.cumsum(30 + 40 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 2.2)
            crash = stft_filter(rng.standard_normal(n), 4000, 16000) * np.exp(-tt * 2.8) * 0.5
            put("fx", t0, boom * 0.9 + crash)
        t0 += sec["bars"] * bar
    # sidechain pump from kicks
    for kt in kick_times:
        i = int(kt * SR); n = min(int(beat * SR), length - i)
        if n > 0:
            tt = np.arange(n) / SR
            pump[i:i + n] = np.minimum(pump[i:i + n], 1 - 0.75 * np.exp(-tt / 0.07))
    # per-stem tone shaping (energy-driven brightness from section plan)
    def energy_at(t):
        acc = 0
        for s in plan:
            dur = s["bars"] * bar
            if t < acc + dur:
                return {**PRESETS.get(s.get("type", "drop"), {}), **s}.get("energy", 0.6)
            acc += dur
        return 0.3
    stems["bass"] = stft_filter(stems["bass"], 0, 420) * pump
    stems["hats"] = stft_filter(stems["hats"], 6500, 18000)
    stems["clap"] = stft_filter(stems["clap"], 250, 9000)
    stems["arp"] = stft_filter(stems["arp"], 300, lambda t: 1500 + 5000 * energy_at(t)) * (0.4 + 0.6 * pump)
    stems["lead"] = stft_filter(stems["lead"], 200, 6000)
    for c in range(2):
        padS[c] = stft_filter(padS[c], 120, lambda t: 700 + 6500 * energy_at(t) ** 1.5) * (0.35 + 0.65 * pump)
    # stereo mix
    import numpy as np
    mix = np.zeros((2, length))
    def add(sig, g, pan=0.0):
        mix[0] += sig * g * (1 - max(0, pan)); mix[1] += sig * g * (1 + min(0, pan))
    add(stems["kick"], 0.95); add(stems["bass"], 0.55); add(stems["clap"], 0.5)
    hats = stems["hats"]; mix[0] += hats * 0.22; mix[1] += np.roll(hats, int(0.004 * SR)) * 0.22
    # arp ping-pong delay (dotted 8th)
    d = int(0.75 * beat * SR); arp = stems["arp"]
    l = arp + 0.45 * np.concatenate([np.zeros(2 * d), arp[:-2 * d]])
    r = 0.55 * np.concatenate([np.zeros(d), arp[:-d]]) + 0.25 * np.concatenate([np.zeros(3 * d), arp[:-3 * d]])
    mix[0] += l * 0.5; mix[1] += (r + arp * 0.3) * 0.5
    mix += padS * 0.9
    wet = reverb(stems["piano"] * 0.8 + stems["lead"] * 0.5 + stems["fx"] * 0.4, 2.4, seed, 0.35)
    mix += wet + np.stack([stems["lead"], stems["lead"]]) * 0.25 + np.stack([stems["fx"], stems["fx"]]) * 0.5
    mix += reverb(mix.mean(axis=0) * 0.12, 1.6, seed + 1, 1.0) * 0.5
    # master: soft clip + fade tail
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    fade = int(tail_s * SR)
    mix[:, -fade:] *= np.linspace(1, 0, fade) ** 2
    mix /= np.abs(mix).max() + 1e-9
    mix *= 0.89
    beats = [round(i * beat, 4) for i in range(total_bars * 4)]
    return mix, sections, beats, total_bars * bar


def write_wav(path, stereo):
    import numpy as np
    data = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


def cmd_compose(a):
    from .beats import analyse
    pr = active_project(a.project)
    plan = json.loads(a.plan) if a.plan.lstrip().startswith("{") else json.loads(Path(a.plan).read_text())
    bpm = float(plan.get("bpm", 120))
    secs = plan["sections"]
    tid = slug(a.id)
    mix, sections, beats, music_len = render_track(secs, bpm, plan.get("seed", 1), plan.get("tail", 2.5))
    cache = pr.cache / "music"
    cache.mkdir(parents=True, exist_ok=True)
    raw = cache / f"{tid}.raw.wav"
    write_wav(raw, mix)
    dest = cache / f"{tid}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000", str(dest)], check=True)
    raw.unlink()
    d = pr.p("music", tid)
    d.mkdir(parents=True, exist_ok=True)
    wj(d / "plan.json", plan)
    meta = {"id": tid, "title": plan.get("title", tid), "artist": "Original composition (cvp compose)", "source": "generated in this project",
            "license": "Original work composed for this project; no third-party samples or loops; cleared for commercial and social use",
            "license_verified": True, "file": str(dest.relative_to(pr.dir)), "sha256": sha256(dest), "added": now(), "bpm": bpm}
    wj(d / "track.json", meta)
    an = analyse(dest)
    bar = 240.0 / bpm
    bm = {"duration": an["duration"], "bpm": bpm, "beat_period": 60.0 / bpm, "beats": beats, "downbeats": beats[::4],
          "phrases": [round(s["t"], 4) for s in sections], "bar_energy_db": an["bar_energy_db"], "accents": an["accents"],
          "sections": [{"t": s["t"], "type": {"drop": "drop", "build": "build", "break": "breakdown", "outro": "outro",
                                                "intro": "intro", "lift": "build", "sting": "climax"}.get(s["type"], s["type"]),
                        "name": s["name"], "bars": s["bars"], "until": round(s["t"] + s["bars"] * bar, 3)} for s in sections],
          "music_end": round(music_len, 3), "detected_bpm": an["bpm"], "sha256": meta["sha256"],
          "method": "exact grid from the composition plan; detected_bpm from audio analysis as a check"}
    wj(d / "beats.json", bm)
    print(f"{tid}: {bpm} BPM, {sum(s['bars'] for s in secs)} bars, music {music_len:.2f}s (+tail), detected {an['bpm']} BPM")
    for s in bm["sections"]:
        print(f"  {s['t']:7.2f}s  {s['name']:10s} {s['type']:9s} {s['bars']} bars -> {s['until']}s")
