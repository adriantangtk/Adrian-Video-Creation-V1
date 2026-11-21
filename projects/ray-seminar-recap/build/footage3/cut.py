import json,sys,os,subprocess,numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,os.path.dirname(__file__))
from shotlist import SHOTS
P='/home/user/Adrian-Video-Creation-V1/projects/ray-seminar-recap/'
SC=sys.argv[1]  # score dir
GRADE="eq=contrast=1.06:saturation=1.12:gamma=1.03,unsharp=5:5:0.45:5:5:0.0"
def pick(src,a,b,dur):
    r=json.load(open(f'{SC}/{src}.mp4.json'))
    sh=np.array([x['sh'] for x in r]);dx=np.array([x['dx'] for x in r]);dy=np.array([x['dy'] for x in r])
    k=np.ones(5)/5; jit=np.hypot(dx-np.convolve(dx,k,'same'),dy-np.convolve(dy,k,'same'))
    spd=np.hypot(np.convolve(dx,k,'same'),np.convolve(dy,k,'same'))
    p90=np.percentile(sh,90); best=None
    n=int(round(dur*10))
    for s in np.arange(a,b-dur+0.001,0.1):
        i=int(round(s*10)); w=slice(i,min(i+n,len(sh)))
        if w.stop-w.start<n-1: continue
        sc=sh[w].min()/p90 + 0.3*np.median(sh[w])/p90 - 0.25*jit[w].mean() - 0.5*(jit[w].max()>6)
        if best is None or sc>best[0]: best=(sc,round(float(s),2),float(sh[w].min()/p90),float(np.median(sh[w])),float(jit[w].mean()),float(spd[w].mean()))
    return best
def vf(mode,dur):
    if mode=='full': core="scale=1920:1080:flags=lanczos"
    elif mode.startswith('crop:'):
        x,y=mode[5:].split(','); core=f"crop=1920:1080:{x}:{y}"
    else:
        kind,rest=mode.split(':'); cx,cy,z=map(float,rest.split(','))
        f=f"(1+({z}-1)*t/{dur})" if kind=='push' else f"({z}-({z}-1)*t/{dur})"
        core=f"scale=w='2*trunc(1920*{f}/2)':h=-2:eval=frame:flags=lanczos,crop=1920:1080:'(iw-1920)*{cx}':'(ih-1080)*{cy}'"
    return f"setpts=PTS-STARTPTS,fps=30,{core},{GRADE},format=yuv420p"
def job(i):
    src,a,b,dur,mode,cat,desc,motion,bd,bf=SHOTS[i]
    sc,s,rel,med,jit,spd=pick(src,a,b,dur)
    out=P+f'media/v3/s{i+1:02d}.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(s),'-i',P+f'media/raw/{src}.mp4','-t',str(dur),'-an','-vf',vf(mode,dur),
        '-c:v','libx264','-preset','slow','-crf','14','-g','6','-movflags','+faststart',out],check=True)
    return dict(file=f'media/v3/s{i+1:02d}.mp4',dur=dur,source=src+'.mp4',offset=s,mode=mode,category=cat,description=desc,motion=motion,hasBackdrop=bd,bestFor=bf,
        relSharp=round(rel,3),jitter=round(jit,2),panSpeed=round(spd,1))
with ThreadPoolExecutor(3) as ex: res=list(ex.map(job,range(len(SHOTS))))
json.dump(res,open(P+'build/footage3/cut-log.json','w'),indent=1)
for r in res: print(r['file'],r['offset'],r['relSharp'],r['jitter'],r['mode'])
