import json
P='/home/user/Adrian-Video-Creation-V1/projects/ray-seminar-recap/'
S='/tmp/claude-0/-home-user-Adrian-Video-Creation-V1/786f2193-8616-5085-91d0-d7c3c01bfff6/scratchpad/'
log=json.load(open(P+'build/footage3/cut-log.json')); meas=json.load(open(P+'build/footage3/measure.json'))
old=json.load(open(P+'build/footage/shots.json'))
fix={
 's01':dict(description='grand ballroom wide: chandelier ceiling, LED wall showing the Reinald Goh slide, full tables'),
 's15':dict(category='audience',description='attendees at tables (laptops out) under the sculpture wall, slide on side screen',motion='static',hasBackdrop=False),
 's22':dict(category='rein',description='Rein (black, standing) and host (seated) on the RISE 2.0 stage, 1 Question slide'),
 's23':dict(description="host at the HSBC lectern beside Rein's bio slide (Tiffany, Gucci, Dior, Celine; LVMH, Kering & Prada groups) - native 1:1 crop, pairs with the Prada bite"),
 's24':dict(description="push-in from the wide hall to Rein's speaker slide; ends on the WORKED FOR logos row (Dior, Celine, Gucci, Saint Laurent, Prada) - brand logos visible at the end"),
 's25':dict(description='LED wall wide with the Reinald Goh slide and RISE 2.0 logo, host at lectern, full house'),
 's26':dict(description='Rein (black) standing, host seated, under the RISE 2.0 logo with the watch question slide - native 1:1 crop'),
 's27':dict(description='push-in on the watch question slide, Rein and host on stage'),
 's28':dict(description='wide: tables watching Rein and host, 1 Question That Unravelled More Than Asked slides'),
 's29':dict(description='Rein draws the value-over-time chart on screen while the host sits beside the RISE 2.0 logo'),
 's30':dict(description='Rein at the whiteboard sketching the chart - native 1:1 crop'),
 's31':dict(description='push-in on the host and the RISE 2.0 logo while Rein draws'),
 's38':dict(description='packed tables toward the RISE 2.0 screen (light stand in frame)'),
 's41':dict(description='tables under the chandelier ceiling, red pillars'),
 's47':dict(description='crowd up and mingling/dancing, stage beams on red pillars (darker, softer)'),
 's48':dict(description='crowd on their feet, guest in white shirt dancing toward camera, chandeliers'),
}
grade=lambda m,mode:('A' if m>=800 else 'B' if m>=450 else 'C') if not (mode.startswith('crop') or mode.startswith('push:0.18')) else 'B'
shots=[]
for r in log:
    n=r['file'].split('/')[-1][:-4]; m=meas[n]
    d=dict(file=r['file'],dur=r['dur'],source=r['source'],offset=r['offset'],framing=r['mode'],category=r['category'],description=r['description'],
        sharpness=dict(score=int(m['med']),min=int(m['min']),relToClipBest=r['relSharp'],shakeJitter=r['jitter'],grade=grade(m['med'],r['mode'])),
        motion=r['motion'],hasBackdrop=r['hasBackdrop'],bestFor=r['bestFor'])
    d.update(fix.get(n,{})); shots.append(d)
kb=[('s54','ph25','puzzle','slow push on the lit RISE 2.0 / Energise, Excite, Excel puzzle board','open'),
    ('s55','ph21','puzzle','slow push on the giant RISE 2.0 puzzle piece held up on stage (ONE TEAM, ONE HSBC LED behind)','excel'),
    ('s56','ph07','stage','slow push on the giant HSBC RISE 2.0 logo, host on stage (IWPB Wealth Conference 2026)','outro'),
    ('s57','ph16','rein',"slow push on Rein's WORKED FOR slide (brand logos visible) with Rein on stage",'excite')]
for n,ph,cat,desc,bf in kb:
    m=meas[n]; shots.append(dict(file=f'media/v3/{n}.mp4',dur=3.0,source=f'media/v3/photos/{ph}.jpg (photo, Ken Burns)',offset=0,framing='photo-push',category=cat,description=desc,
        sharpness=dict(score=int(m['med']),min=int(m['min']),grade='A' if n in('s55','s54') else 'B'),motion='push',hasBackdrop=True,bestFor=bf))
def oldbite(i):
    b=old['bites'][i]; return b
tx=json.load(open('/tmp/bp/transcript.json'))
pw=[dict(w=x['text'].replace('training.','trainee.'),start=x['start'],end=x['end']) for x in tx]
bites=[
 dict(name='hook',wav='media/v3/bite-1.wav',mp4=None,dur=5.834,text=oldbite(0)['text'],words=oldbite(0)['words'],source=oldbite(0)['source'],note='portrait source shows no speaker: cover with stage shots'),
 dict(name='prada',wav='media/v3/bite-prada.wav',mp4='media/v3/bite-prada.mp4',dur=2.767,text='He started in Prada as a management trainee.',words=pw,
      source='20261120_145350_132.mp4 2.52-5.29 (host intro; one continuous phrase, no internal pause >0.22 s)',note='mp4 is the wide ballroom (host tiny on stage, LED shows the Reinald Goh slide); whisper hears "training", word timings from whisper on the final cut'),
 dict(name='watch',wav='media/v3/bite-3.wav',mp4='media/v3/bite-3.mp4',dur=3.6,text=oldbite(2)['text'],words=oldbite(2)['words'],source=oldbite(2)['source'],note='mp4 copied from media/land/bite-3.mp4 (3.567 s, landscape 1080p)'),
]
photos=json.load(open(S+'photos.json'))
hero=['s54','s02','s45','s19','s55','s56','s07','s53']
rejected=[
 '20261120_150930_281.mp4: Insta360 compilation with AI Director watermark, already edited, 1080p',
 'portrait videos 133610, 135721, 141401, 144001, 144352, IMG_5526.MOV, IMG_5531.MOV: centre 16:9 crop < 1080 px tall',
 '133644 0-14 s: speaker over heads, out of focus',
 '134523 2-7 s: standing crowd, motion smear; 145516 43-46/60+ and 145533 44/62+: whip pans / floor',
 '145350_132 76-84 s and 145427 60+ s: camera pointed at floor/phone screen',
 '141325 8-21 s, 145455 6-9 s: soft during fast pan',
 'photos 133116, 133120, 133123, 135755: soft/motion blur; 141625, 143956, 143959, 144346 portrait',
]
json.dump(dict(format='1920x1080 30fps, grade eq contrast 1.06 sat 1.12 gamma 1.03 + unsharp 0.45, crf14 g6, no audio',
  sharpnessNote='score = mean Laplacian variance of the 6 sharpest 320x270 tiles on 1080p output frames (10 fps), median over the shot; native 1:1 crops score lower than downscaled wides but were checked by eye',
  bites=bites,shots=shots,photos=photos,heroes=hero,rejected=rejected,contactSheets=[f'build/footage3/sheet-{i}.jpg' for i in range(1,6)]),
  open(P+'build/footage3/shots.json','w'),indent=1)
from collections import Counter; print(Counter(s['category'] for s in shots), len(shots), Counter(s['sharpness']['grade'] for s in shots))
