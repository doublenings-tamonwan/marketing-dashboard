import sys
sys.argv=[sys.argv[0],'cover']
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import build as B
W,H=1080,1920
src=B.photo('7e14678d')
h=1500; w=h*9/16; x0=718-w/2; y0c=135
im=src.resize((W,H),Image.LANCZOS,box=(x0,y0c,x0+w,y0c+h))
# warm/vivid like clip grade
im=ImageEnhance.Color(im).enhance(1.15); im=ImageEnhance.Contrast(im).enhance(1.04)
a=np.asarray(im).astype(np.float32); a=255*((a/255)**0.93); a[...,0]*=1.02; a[...,2]*=0.97
im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
# soften top (glass) + scrim behind title
top=im.filter(ImageFilter.GaussianBlur(6)); m=Image.new('L',(W,H),0)
md=ImageDraw.Draw(m); [md.line((0,y,W,y),fill=int(255*max(0,1-y/340))) for y in range(340)]
im=Image.composite(top,im,m)
dk=Image.new('L',(1,H))
for y in range(H): dk.putpixel((0,y),int(255*0.5*max(0,1-y/300)**1.2))
dl=Image.new('RGBA',(W,H),(30,16,10,0)); dl.putalpha(dk.resize((W,H))); im.alpha_composite(dl)
sc=Image.new('L',(1,H))
for y in range(H):
    t=y/H; v=0.0
    if t<0.56: v=0.62*min(1,max(0,(t-0.0)/0.15))*min(1,max(0,(0.56-t)/0.12))
    sc.putpixel((0,y),int(v*255))
lay=Image.new('RGBA',(W,H),(25,12,10,0)); lay.putalpha(sc.resize((W,H))); im.alpha_composite(lay)
cx=W//2
B.shadow_text(im,(cx,385),'พามารีวิว',B.font('Kanit-Medium.ttf',56),(255,255,255,255),alpha=200)
f1=B.font('Fraunces-Bold.ttf',200)
B.shadow_text(im,(cx,545),'Izakaya',f1,B.CREAM,blur=18,alpha=190)
B.shadow_text(im,(cx+40,735),'NANA',f1,B.CREAM,blur=18,alpha=190)
d=ImageDraw.Draw(im)
bb1=d.textbbox((cx,545),'Izakaya',font=f1,anchor='mm'); bb2=d.textbbox((cx+40,735),'NANA',font=f1,anchor='mm')
im.alpha_composite(B.asterisk(96,B.PINK),(int(bb1[2])+6,int(bb1[1])-32))
im.alpha_composite(B.asterisk(80,(140,215,255,255)),(int(bb2[0])-104,int((bb2[1]+bb2[3])/2)-40))
B.shadow_text(im,(cx,875),'อิซากะยะนานะ',B.font('Kanit-Medium.ttf',58),(255,255,255,255),alpha=210)
pf=B.font('Kanit-Medium.ttf',54); txt='ปากน้ำ · สมุทรปราการ'; tw=d.textlength(txt,font=pf); y0,ph=932,90
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((cx-tw/2-44,y0+6,cx+tw/2+44,y0+ph+6),radius=ph//2,fill=(0,0,0,120))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
d=ImageDraw.Draw(im); d.rounded_rectangle((cx-tw/2-44,y0,cx+tw/2+44,y0+ph),radius=ph//2,fill=(255,255,255,255))
d.text((cx,y0+ph/2+2),txt,font=pf,fill=(20,20,20,255),anchor='mm')
im.convert('RGB').save('izakaya-cover.png')
c=im.convert('RGB').crop((0,240,1080,1680)); c.save('chk/cover-3x4.jpg')
