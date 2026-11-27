"""Music library per project and beat maps (BPM, beats, downbeats, phrases, energy sections, accents)."""
import shutil, subprocess
from pathlib import Path
from .common import active_project, rj, wj, now, slug, sha256, die, run

SR, HOP, NFFT = 22050, 512, 2048


def _load(path):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def analyse(path):
    import numpy as np
    y = _load(path)
    dur = len(y) / SR
    if dur < 2:
        raise RuntimeError("audio too short for a beat map")
    n = 1 + (len(y) - NFFT) // HOP
    win = np.hanning(NFFT).astype(np.float32)
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    frames = y[idx] * win
    mag = np.abs(np.fft.rfft(frames, axis=1))
    logm = np.log1p(100 * mag)
    flux = np.maximum(0, np.diff(logm, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode="same")
    env = np.maximum(flux, 0)
    env /= env.max() + 1e-9
    fr = SR / HOP  # envelope frames per second
    # tempo: autocorrelation weighted by a log-normal prior around 120 BPM
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm_of = 60 * fr / np.maximum(lags, 1)
    valid = (bpm_of >= 60) & (bpm_of <= 190)
    prior = np.exp(-0.5 * (np.log2(np.maximum(bpm_of, 1) / 120) / 0.9) ** 2)
    score = np.where(valid, ac * prior, 0)
    lag = int(np.argmax(score))
    # refine lag with parabolic interpolation
    if 1 < lag < len(score) - 1:
        a_, b_, c_ = score[lag - 1], score[lag], score[lag + 1]
        lagf = lag + 0.5 * (a_ - c_) / (a_ - 2 * b_ + c_ + 1e-12)
    else:
        lagf = float(lag)
    bpm = 60 * fr / lagf
    period = lagf
    # dynamic-programming beat tracking (Ellis 2007)
    N = len(env)
    D = env.copy()
    back = np.full(N, -1)
    lo, hi = int(round(period / 2)), int(round(period * 2))
    for t in range(hi, N):
        prev = np.arange(t - hi, t - lo + 1)
        tight = -100 * (np.log((t - prev) / period)) ** 2
        cand = D[prev] + tight
        k = int(np.argmax(cand))
        D[t] = env[t] + cand[k]
        back[t] = prev[k]
    tail = slice(max(0, N - int(period)), N)
    t = int(np.argmax(D[tail]) + tail.start)
    beats = []
    while t >= 0:
        beats.append(t)
        t = back[t]
    beats = np.array(beats[::-1])
    off = (NFFT / 2) / SR  # frames are not centred: shift to the window centre
    bt = beats / fr + off
    # downbeat phase: which of 4 phases carries the most low-frequency onset energy
    low = np.maximum(0, np.diff(logm[:, :12], axis=0)).sum(axis=1)
    low = np.concatenate([[0], low])
    phase = int(np.argmax([low[beats[p::4]].sum() for p in range(4)])) if len(beats) >= 8 else 0
    downbeats = bt[phase::4]
    phrases = bt[phase::16]
    # energy per bar -> sections
    rms = np.sqrt(np.convolve(y ** 2, np.ones(HOP) / HOP, mode="same")[::HOP] + 1e-12)
    bars = list(downbeats) + [dur]
    e_bar = []
    for i in range(len(bars) - 1):
        s, e = int(bars[i] * fr), max(int(bars[i] * fr) + 1, int(bars[i + 1] * fr))
        e_bar.append(float(20 * np.log10(rms[s:e].mean() + 1e-9)))
    sections = []
    if e_bar:
        eb = np.array(e_bar)
        med = float(np.median(eb))
        for i in range(1, len(eb)):
            d = eb[i] - eb[i - 1]
            if d >= 4 and eb[i] > med:
                sections.append({"t": round(float(bars[i]), 3), "type": "drop", "delta_db": round(float(d), 1)})
            elif d <= -5:
                sections.append({"t": round(float(bars[i]), 3), "type": "breakdown", "delta_db": round(float(d), 1)})
        # builds: 4+ bars of rising energy
        run_start = None
        for i in range(1, len(eb)):
            if eb[i] > eb[i - 1] + 0.4:
                run_start = i - 1 if run_start is None else run_start
            else:
                if run_start is not None and i - run_start >= 4:
                    sections.append({"t": round(float(bars[run_start]), 3), "type": "build", "until": round(float(bars[i]), 3)})
                run_start = None
        k = int(np.argmax(eb))
        sections.append({"t": round(float(bars[k]), 3), "type": "climax", "level_db": round(float(eb[k]), 1)})
        sections.sort(key=lambda x: x["t"])
    # accents: strongest onsets (impacts) at least 1 s apart
    order = np.argsort(env)[::-1]
    acc = []
    for i in order:
        if env[i] < 0.35 or len(acc) >= 40:
            break
        tt = i / fr + off
        if all(abs(tt - x) >= 1.0 for x in acc):
            acc.append(tt)
    return {"duration": round(dur, 3), "bpm": round(float(bpm), 2), "beat_period": round(60 / bpm, 4),
            "beats": [round(float(x), 3) for x in bt], "downbeats": [round(float(x), 3) for x in downbeats],
            "phrases": [round(float(x), 3) for x in phrases], "bar_energy_db": [round(x, 1) for x in e_bar],
            "sections": sections, "accents": sorted(round(float(x), 3) for x in acc),
            "method": "spectral-flux onset envelope, autocorrelation tempo, DP beat tracking; estimates, verify by ear"}


def cmd_music_add(a):
    pr = active_project(a.project)
    f = Path(a.file).resolve()
    if not f.is_file():
        die(f"no file {f}")
    tid = slug(a.id or f.stem)[:40]
    d = pr.p("music", tid)
    d.mkdir(parents=True, exist_ok=True)
    cache = pr.cache / "music"
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / f"{tid}{f.suffix.lower()}"
    if f != dest:
        shutil.copy2(f, dest)
    meta = rj(d / "track.json", {})
    meta.update(id=tid, title=a.title or f.stem, artist=a.artist, source=a.source, license=a.license or "UNVERIFIED",
                license_verified=bool(a.verified), file=str(dest.relative_to(pr.dir)), sha256=sha256(dest), added=now())
    wj(d / "track.json", meta)
    cmd_beats_one(pr, tid)
    print(f"music {tid} added (license: {meta['license']}{'' if meta['license_verified'] else ', NOT verified'})")


def cmd_beats_one(pr, tid, force=False):
    d = pr.p("music", tid)
    meta = rj(d / "track.json") or die(f"unknown track {tid}")
    bm = rj(d / "beats.json")
    if bm and bm.get("sha256") == meta["sha256"] and not force:
        return bm
    bm = analyse(pr.dir / meta["file"])
    bm["sha256"] = meta["sha256"]
    wj(d / "beats.json", bm)
    return bm


def cmd_beats(a):
    pr = active_project(a.project)
    bm = cmd_beats_one(pr, a.track, a.force)
    secs = ", ".join(f"{s['type']}@{s['t']}" for s in bm["sections"][:20])
    print(f"{a.track}: {bm['bpm']} BPM, {len(bm['beats'])} beats, {len(bm['downbeats'])} bars, dur {bm['duration']}s")
    print(f"phrases: {bm['phrases'][:16]}")
    print(f"sections: {secs}")
    print(f"accents: {bm['accents'][:20]}")
    print(f"full map: {pr.p('music', a.track, 'beats.json')}")
