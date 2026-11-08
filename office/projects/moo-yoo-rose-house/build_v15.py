import json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
U='/root/.claude/uploads/4fb0ae1d-39b3-5573-9ed2-8168ea5e1189/'
VO=U+'dd49cf75-Soi_Muban_Rewat_Niwet_2_2.m4a'
R='/home/user/marketing-dashboard/office/editor/'; FONT=R+'../assets/fonts/Itim-Regular.ttf'
MP4=U+'54ff146a-v14044g50000db512pvog65phgdopbjg.MP4'
def run(*a): subprocess.run(list(a),check=True)
allp=[(0.75,3.15),(3.85,6.35),(7.10,9.45),(10.05,12.45),(12.90,15.25),(15.65,17.75),(18.05,19.90)]
use=[0,1,2,3,4,5,6]
PAD,GAP,LEAD,CARD=0.08,0.25,0.10,2.6
clips=[(allp[i][0]-PAD,allp[i][1]+PAD) for i in use]
shots=[round((e-s)+GAP+(LEAD if k==0 else 0),3) for k,(s,e) in enumerate(clips)]
# audio
fc=[];parts=[]
for k,(s,e) in enumerate(clips):
    fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={e-s-0.04:.3f}:d=0.04,aformat=sample_rates=48000:channel_layouts=stereo[p{k}]")
    fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{LEAD if k==0 else GAP}[z{k}]"); parts+=[f"[z{k}]",f"[p{k}]"]
fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{GAP+CARD}[zt]"); parts.append("[zt]")
fc.append("".join(parts)+f"concat=n={len(parts)}:v=0:a=1,highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11[out]")
run('ffmpeg','-nostdin','-v','error','-y','-i',VO,'-filter_complex',';'.join(fc),'-map','[out]','-ar','48000','vo15.wav')
# shots: 1 lake+fountain, 2 sign, 3 building, 4 sunset lake (hands), 5 photo, 6 friends
src=[('p8430',0),(U+'0ffb9241-IMG_5948.MOV',1.2),(U+'8b5f1a8e-IMG_5943.MOV',0.4),(MP4,0.2),('p8260',0),('photo',0),(MP4,6.95)]
vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1"
names=[]
PH={'p8430':dict(xc=0.47,z0=1.0,z1=1.12,cy0=0.5,cy1=0.58,flash=False),
    'p8260':dict(xc=0.47,z0=1.15,z1=1.15,cy0=0.62,cy1=0.42,flash=False),
    'photo':dict(xc=None,flash=True)}
def photo_shot(name,d,out):
    n=round(d*30)
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    im=Image.open(name+'.jpg'); W,H=im.size; c=PH[name]
    for k in range(n):
        u=k/(n-1)
        if c['xc'] is None:  # original drink-photo move
            cw,ch,x0=3213,H,880; fx,fy=0.55*W,0.42*H
            z=1+0.10*u**0.9; w,h=cw/z,ch/z
            cx=x0+cw/2+(fx-(x0+cw/2))*(1-1/z); cy=ch/2+(fy-ch/2)*(1-1/z)
        else:
            z=c['z0']+(c['z1']-c['z0'])*u; h=H/z; w=h*9/16
            cx=min(max(c['xc']*W,w/2),W-w/2)
            cy=(c['cy0']+(c['cy1']-c['cy0'])*u)*H; cy=min(max(cy,h/2),H-h/2)
        fr=im.resize((1080,1920),Image.LANCZOS,box=(cx-w/2,cy-h/2,cx+w/2,cy+h/2))
        if c['flash'] and k<5: fr=Image.blend(fr,Image.new('RGB',fr.size,'white'),0.85*(1-k/5))
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
for i,((f,ss),d) in enumerate(zip(src,shots)):
    out=f'v15s{i}.mp4'; names.append(out)
    if f in PH: photo_shot(f,d,out)
    else:
        run('ffmpeg','-nostdin','-v','error','-y','-ss',str(ss),'-t',str(d),'-i',f,'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','18',out)
open('list15.txt','w').write(''.join(f"file '{n}'\n" for n in names))
run('ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i','list15.txt','-c','copy','base15.mp4')
run('bash',R+'glow.sh','base15.mp4','base15-glow.mp4')
# info card (not glowed, so text stays crisp)
run('ffmpeg','-nostdin','-v','error','-y','-ss','3.5','-i',U+'c23d24fe-IMG_5942.MOV','-vf',vf,'-frames:v','1','cardbg.png')
bg=Image.open('cardbg.png').convert('RGB').filter(ImageFilter.GaussianBlur(18))
bg=Image.blend(bg,Image.new('RGB',bg.size,(255,240,246)),0.25)
F=lambda s: ImageFont.truetype(FONT,s,layout_engine=ImageFont.Layout.RAQM)
panel=Image.new('RGBA',(940,760),(0,0,0,0)); d=ImageDraw.Draw(panel)
d.rounded_rectangle((0,0,939,759),radius=60,fill=(255,255,255,235),outline=(255,105,180,255),width=8)
d.text((470,70),"MOO YOO ROSE HOUSE",font=F(70),fill=(255,105,180),anchor='ma')
d.text((470,165),"คาเฟ่ + วิลล่าริมทะเลสาบ",font=F(56),fill=(110,80,95),anchor='ma')
rows=[("ที่ตั้ง","อ.บางเลน จ.นครปฐม"),("เวลา","10:00–19:00"),("","(เช็กกับร้านก่อนไปนะ)")]
y=290
for lab,val in rows:
    if lab:
        d.rounded_rectangle((60,y-6,250,y+70),radius=30,fill=(255,105,180))
        d.text((155,y+32),lab,font=F(48),fill='white',anchor='mm')
        d.text((280,y+32),val,font=F(56),fill=(70,50,60),anchor='lm'); y+=115
    else:
        d.text((280,y-30),val,font=F(42),fill=(150,120,135),anchor='lt'); y+=60
d.text((470,640),"กดเซฟไว้ แล้วชวนเพื่อนไปกัน",font=F(56),fill=(255,105,180),anchor='ma')
n=round(CARD*30)
p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','card15.mp4'],stdin=subprocess.PIPE)
for k in range(n):
    z=1+0.05*k/n; w,h=1080/z,1920/z
    fr=bg.resize((1080,1920),Image.LANCZOS,box=((1080-w)/2,(1920-h)/2,(1080+w)/2,(1920+h)/2)).convert('RGBA')
    a=min(1,k/9); off=int((1-a)*60)
    pl=panel.copy(); pl.putalpha(pl.getchannel('A').point(lambda v:int(v*a)))
    fr.alpha_composite(pl,(70,560+off))
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close(); p.wait()
run('ffmpeg','-nostdin','-v','error','-y','-i','base15-glow.mp4','-i','card15.mp4','-filter_complex','[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[v]','-map','[v]','-c:v','libx264','-preset','medium','-crf','18','base15-card.mp4')
# subs (VO lines) + top title on first shot
texts=json.load(open('subs-v11.json')); lines=[texts[i]['text'] for i in use]
t=0;subs=[];starts=[]
for dd,tx in zip(shots,lines):
    subs.append({'start':round(t,3),'end':round(t+dd,3),'text':tx}); starts.append(round(t,2)); t+=dd
subs[4]['pos']='top'  # ช็อตสะพานไม้: ซับไว้บนท้องฟ้า ไม่ทับหน้า
subs.append({'start':0.0,'end':shots[0],'text':'คาเฟ่ริมทะเลสาบ\nนครปฐม','pos':'top','size':124})
json.dump(subs,open('subs-v15.json','w'),ensure_ascii=False,indent=1)
run('python3',R+'sparkles.py','--video','base15-card.mp4','--out','base15-fx.mp4','--bursts',','.join(str(max(s,0.1)) for s in starts+[round(t,2)]))
run('python3',R+'burn_subs.py','--video','base15-fx.mp4','--subs','subs-v15.json','--out','moo-yoo-v15.mp4','--audio','vo15.wav')
print('shots',shots,'card',CARD,'total',round(t+CARD,2),'starts',starts)
