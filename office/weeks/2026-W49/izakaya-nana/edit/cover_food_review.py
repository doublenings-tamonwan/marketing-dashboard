import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
F='/home/user/marketing-dashboard/office/assets/fonts/'
U='/root/.claude/uploads/4c923d2c-8f5d-5971-8899-b8d14570e947/'
W,H=1080,1920
def make(photo, out, yc=0.5, xc=0.5, py=915):
    im=ImageOps.exif_transpose(Image.open(U+photo)).convert('RGB')
    s=max(W/im.width,H/im.height); im=im.resize((int(im.width*s)+1,int(im.height*s)+1),Image.LANCZOS)
    x=int((im.width-W)*xc); y=int((im.height-H)*yc); im=im.crop((x,y,x+W,y+H))
    # soft dark gradient top for legibility (no color filter on food)
    g=Image.new('L',(1,H)); 
    for i in range(H): g.putpixel((0,i), int(150*max(0,1-i/900)))
    g=g.resize((W,H)); dark=Image.new('RGB',(W,H),(20,12,10)); im=Image.composite(dark,im,g)
    c=im.convert('RGBA'); d=ImageDraw.Draw(c)
    def txt(xy,t,f,fill,sw=0,sf=None,anchor='mm',shadow=True):
        if shadow:
            l=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(l).text((xy[0]+4,xy[1]+6),t,font=f,fill=(0,0,0,150),anchor=anchor,stroke_width=sw,stroke_fill=(0,0,0,150))
            c.alpha_composite(l.filter(ImageFilter.GaussianBlur(8)))
        ImageDraw.Draw(c).text(xy,t,font=f,fill=fill,anchor=anchor,stroke_width=sw,stroke_fill=sf)
    th=ImageFont.truetype(F+'Chonburi-Regular.ttf',46)
    txt((W//2,430),'พามารีวิว · ร้านญี่ปุ่นสไตล์อิซากายะ',th,'#FFF4E0')
    fr=ImageFont.truetype(F+'Fraunces-Bold.ttf',175)
    txt((W//2,600),'Izakaya',fr,'#F6E3A8')
    fr2=ImageFont.truetype(F+'Fraunces-Bold.ttf',200)
    txt((W//2,790),'NANA',fr2,'#F6E3A8')
    # asterisks
    def ast(cx,cy,r,col):
        for k in range(3):
            a=k*math.pi/3; ImageDraw.Draw(c).line([(cx-r*math.cos(a),cy-r*math.sin(a)),(cx+r*math.cos(a),cy+r*math.sin(a))],fill=col,width=14)
    ast(905,545,34,'#FF8FB8'); ast(170,830,26,'#8FD3EA')
    # pill
    pf=ImageFont.truetype(F+'Chonburi-Regular.ttf',48); t='ปากน้ำ · สมุทรปราการ'
    bw=ImageDraw.Draw(c).textlength(t,font=pf)+90
    ImageDraw.Draw(c).rounded_rectangle([W//2-bw/2,py,W//2+bw/2,py+90],radius=45,fill='white')
    ImageDraw.Draw(c).text((W//2,py+45),t,font=pf,fill='#2A1A14',anchor='mm')
    # small tag
    sf=ImageFont.truetype(F+'Chonburi-Regular.ttf',44); t2='วันนี้ขอสายปลาดิบ!'
    bw=ImageDraw.Draw(c).textlength(t2,font=sf)+70
    ImageDraw.Draw(c).rounded_rectangle([W//2-bw/2,py+115,W//2+bw/2,py+190],radius=38,fill='#FF8FB8')
    ImageDraw.Draw(c).text((W//2,py+152),t2,font=sf,fill='white',anchor='mm')
    c.convert('RGB').save(out,quality=92)
    # 3:4 center check
    h=int(W*4/3); y0=(H-h)//2
    c.convert('RGB').crop((0,y0,W,y0+h)).save(out.replace('.jpg','-3x4.jpg'),quality=85)
make('7e14678d-image.jpg', sys.argv[1]+'/coverA-yukhoe.jpg', yc=0.15, py=1440)
make('7fa7d651-image.jpg', sys.argv[1]+'/coverA-table.jpg', yc=0.35)
