import subprocess,numpy as np,cv2,json,glob,os
from PIL import Image,ImageDraw,ImageFont
P='/home/user/Adrian-Video-Creation-V1/projects/ray-seminar-recap/'
fs=sorted(glob.glob(P+'media/v3/s*.mp4'))
font=ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-MediumItalic.otf',24)
res={}; thumbs={}
for f in fs:
    n=os.path.basename(f)[:-4]
    p=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf','fps=10,format=gray','-f','rawvideo','-'],capture_output=True).stdout
    fr=np.frombuffer(p,np.uint8).reshape(-1,1080,1920)
    vals=[]
    for g in fr:
        lap=cv2.Laplacian(g,cv2.CV_32F); t=sorted(lap[y:y+270,x:x+320].var() for y in range(0,1080,270) for x in range(0,1920,320)); vals.append(np.mean(t[-6:]))
    dur=len(fr)/10
    res[n]=dict(min=float(np.min(vals)),med=float(np.median(vals)),bri=float(fr.mean()))
    th=[]
    for t in (0.15,dur/2,dur-0.2):
        o=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',f,'-frames:v','1','-vf','scale=400:225','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
        th.append(Image.frombytes('RGB',(400,225),o))
    thumbs[n]=th
json.dump(res,open(P+'build/footage3/measure.json','w'),indent=1)
names=sorted(thumbs); per=12
for k in range(0,len(names),per):
    grp=names[k:k+per]; rows=(len(grp)+1)//2
    s=Image.new('RGB',(2*1220,rows*235),'black'); d=ImageDraw.Draw(s)
    for i,n in enumerate(grp):
        x0=(i%2)*1220; y0=(i//2)*235
        for j,im in enumerate(thumbs[n]): s.paste(im,(x0+j*402,y0))
        d.rectangle([x0,y0,x0+250,y0+32],fill='black'); d.text((x0+5,y0+3),f"{n} sh{int(res[n]['med'])}",fill='yellow',font=font)
    s.save(P+f'build/footage3/sheet-{k//per+1}.jpg',quality=82)
for n in names: print(n,{a:int(b) for a,b in res[n].items()})
