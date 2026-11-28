# ภาพลองธีมสติกเกอร์สแครปบุ๊ก: python3 -I scrapbook_mock.py <รูป> <out.jpg> [หัวข้อ1] [หัวข้อ2] [ป้ายไทย] [บับเบิล]
import sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='/home/user/marketing-dashboard/office/assets/fonts/'
W,H=1080,1920
bg=Image.new('RGB',(W,H),'#FFF4F8'); d=ImageDraw.Draw(bg)
for x in range(0,W,90): d.rectangle([x,0,x+44,H],fill='#F9D3E2')
def star(dr,cx,cy,r,fill):
    pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5; rr=r if i%2==0 else r*0.45
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    dr.polygon(pts,fill=fill)
random.seed(3)
for _ in range(26): star(d,random.randint(0,W),random.randint(0,H),random.randint(14,28),random.choice(['#E58BB0','#7CCBE0','#F7B7CF']))
# photo sticker
ph=Image.open(sys.argv[1]).convert('RGB'); pw=820; ph=ph.resize((pw,int(ph.height*pw/ph.width)))
st=Image.new('RGBA',(pw+36,ph.height+36),'white'); st.paste(ph,(18,18))
st=st.rotate(-3,expand=True,resample=Image.BICUBIC)
sh=Image.new('RGBA',st.size,(0,0,0,0)); sh.paste((0,0,0,70),mask=st.split()[3]); sh=sh.filter(ImageFilter.GaussianBlur(14))
bg.paste(sh,(110+12,760+16),sh); bg.paste(st,(110,760),st)
can=bg.convert('RGBA'); d=ImageDraw.Draw(can)
def outlined(text,font,xy,fill,stroke=14,scol='white',shadow=True,angle=0):
    tmp=Image.new('RGBA',(W,500),(0,0,0,0)); t=ImageDraw.Draw(tmp)
    if shadow: t.text((40+8,60+10),text,font=font,fill=(122,14,59,90),stroke_width=stroke,stroke_fill=(122,14,59,90))
    t.text((40,60),text,font=font,fill=fill,stroke_width=stroke,stroke_fill=scol)
    tmp=tmp.crop(tmp.getbbox()).rotate(angle,expand=True,resample=Image.BICUBIC)
    can.alpha_composite(tmp,xy); return tmp.size
en=ImageFont.truetype(F+'DancingScript-Bold.ttf',200)
T1=sys.argv[3] if len(sys.argv)>3 else 'Sample'
T2=sys.argv[4] if len(sys.argv)>4 else 'Title!'
outlined(T1,en,(90,170),'#F7E36B',angle=6)
outlined(T2,en,(380,340),'#8FD3EA',angle=6)
th=ImageFont.truetype(F+'Kanit-Bold.ttf',92)
# tilted label box
lab=Image.new('RGBA',(560,160),(0,0,0,0)); l=ImageDraw.Draw(lab)
l.rectangle([10,10,550,150],fill='#C9F0EA',outline='white',width=8)
l.text((275,78),(sys.argv[5] if len(sys.argv)>5 else 'พามารีวิว'),font=th,fill='#E0569A',anchor='mm',stroke_width=6,stroke_fill='white')
lab=lab.rotate(5,expand=True,resample=Image.BICUBIC); can.alpha_composite(lab,(70,560))
# speech bubble
b=Image.new('RGBA',(360,240),(0,0,0,0)); bd=ImageDraw.Draw(b)
bd.ellipse([10,10,350,190],fill='#FFE1EE',outline='#3A2030',width=6); bd.polygon([(70,170),(40,235),(130,180)],fill='#FFE1EE',outline='#3A2030')
bd.text((180,100),(sys.argv[6] if len(sys.argv)>6 else 'แบบนี้'),font=ImageFont.truetype(F+'Kanit-SemiBold.ttf',56),fill='#3A2030',anchor='mm')
can.alpha_composite(b.rotate(-8,expand=True,resample=Image.BICUBIC),(640,600))
d=ImageDraw.Draw(can)
for cx,cy,r,c in [(980,560,46,'#F7E36B'),(70,1500,40,'#8FD3EA'),(1000,1450,34,'#F7B7CF')]:
    for k in range(4):
        a=k*math.pi/4; d.line([(cx-r*math.cos(a),cy-r*math.sin(a)),(cx+r*math.cos(a),cy+r*math.sin(a))],fill=c,width=22)
# bilingual sub
sub=ImageFont.truetype(F+'Kanit-Bold.ttf',70); sub2=ImageFont.truetype(F+'Kanit-Medium.ttf',48)
y=1640
d.text((W//2-230,y),'ซับภาษาไทย',font=sub,fill='white',anchor='lm',stroke_width=7,stroke_fill='#3A2030')
d.text((W//2+125,y),'คำเด่น',font=sub,fill='#FF7DB5',anchor='lm',stroke_width=7,stroke_fill='#3A2030')
d.text((W//2,y+80),'english subtitle',font=sub2,fill='white',anchor='mm',stroke_width=5,stroke_fill='#3A2030')
# note bubble
nf=ImageFont.truetype(F+'Mali-Bold.ttf',40)
d.rounded_rectangle([640,1430,1000,1510],radius=40,fill='white',outline='#3A2030',width=3)
d.text((820,1470),'* โน้ตสั้น ๆ',font=nf,fill='#3A2030',anchor='mm')
can.convert('RGB').save(sys.argv[2],quality=92)
