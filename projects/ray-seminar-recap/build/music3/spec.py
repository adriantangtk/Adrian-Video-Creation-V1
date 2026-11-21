import sys, wave, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, json
w = wave.open(sys.argv[1]); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2).mean(1) / 32768
g = json.load(open(sys.argv[3]))
fig, ax = plt.subplots(2, 1, figsize=(16, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
ax[0].specgram(x, NFFT=4096, Fs=48000, noverlap=3072, cmap='magma', vmin=-130); ax[0].set_yscale('symlog', linthresh=200); ax[0].set_ylim(20, 20000)
tt = np.arange(len(x)) / 48000; r = np.sqrt(np.convolve(x**2, np.ones(4800)/4800, 'same'))
ax[1].plot(tt, 20*np.log10(r+1e-6)); ax[1].set_ylim(-60, 0)
for a in ax:
    for h in g['hits']: a.axvline(h, color='cyan', lw=1)
for s in g['sections']: ax[0].text(s['start']+0.2, 15000, s['name'], color='w')
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=80)
