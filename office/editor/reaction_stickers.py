"""ทำชุดสติกเกอร์ reaction จากหัวคนที่ไดคัตแล้ว (PNG จาก cutout.py ที่ยังไม่ใส่ --sticker)
ใช้: python3 -I office/editor/reaction_stickers.py --plan plan.json --outdir dir/
plan.json = [{"head": "h1.png", "name": "laugh", "text": "ฮ่าาา", "color": "#FF7DB5", "emoji": ["✨","💕"]}, ...]
- ขอบล่างของหัวโค้งมน (ไม่ตัดตรง) + ขอบขาวหนา + เงา + คำ reaction (Mali Bold) + อีโมจิรอบหัว
- ใช้หน้าจริงของเจ้าของช่องเท่านั้น ห้ามใช้ AI ดัดแปลงสีหน้า (กติกาช่อง: ห้ามภาพ AI ของบุคคลจริง)
"""
import argparse, json, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
F = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

def round_bottom(im):
    w, h = im.size
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.rectangle([0, 0, w, int(h*0.55)], fill=255)
    d.ellipse([int(-w*0.02), int(-h*0.25), int(w*1.02), int(h*1.0)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    im = im.copy(); im.putalpha(ImageChops.multiply(im.split()[3], m)); return im.crop(im.getbbox())

def sticker(im, b=16):
    pad = b*3; base = Image.new('RGBA', (im.width+pad*2, im.height+pad*2), (0,0,0,0)); base.paste(im, (pad, pad), im)
    al = base.split()[3].point(lambda v: 255 if v > 40 else 0)
    ol = al.filter(ImageFilter.MaxFilter(b*2+1)).filter(ImageFilter.GaussianBlur(1.2))
    sh = ol.filter(ImageFilter.GaussianBlur(b)).point(lambda v: int(v*0.3))
    st = Image.new('RGBA', base.size, (0,0,0,0)); st.paste((60,20,40,255), (b//2, b), sh); st.paste((255,255,255,255), (0,0), ol); st.alpha_composite(base)
    return st.crop(st.getbbox())

def emoji(ch, size):
    f = ImageFont.truetype(EMO, 109)
    im = Image.new('RGBA', (160, 160), (0,0,0,0)); ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox()); return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)

ap = argparse.ArgumentParser(); ap.add_argument('--plan', required=True); ap.add_argument('--outdir', required=True)
a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True)
base_dir = os.path.dirname(os.path.abspath(a.plan))
for p in json.load(open(a.plan, encoding='utf-8')):
    head = Image.open(os.path.join(base_dir, p['head'])).convert('RGBA')
    head.thumbnail((560, 560)); st = sticker(round_bottom(head))
    W, H = st.width + 200, st.height + 190
    c = Image.new('RGBA', (W, H), (0,0,0,0)); c.alpha_composite(st, (100, 40))
    pos = [(W-150, 10), (20, 60), (W-120, H//2-40)]
    for i, e in enumerate(p.get('emoji', [])[:3]):
        im = emoji(e, 110 if i == 0 else 80).rotate([12, -15, 8][i], expand=True, resample=Image.BICUBIC)
        c.alpha_composite(im, pos[i])
    if p.get('text'):
        f = ImageFont.truetype(os.path.join(F, 'Mali-Bold.ttf'), 104)
        t = Image.new('RGBA', (W, 220), (0,0,0,0)); d = ImageDraw.Draw(t)
        d.text((W//2+5, 115), p['text'], font=f, anchor='mm', fill=(58,32,48,120), stroke_width=16, stroke_fill=(58,32,48,120))
        d.text((W//2, 108), p['text'], font=f, anchor='mm', fill=p.get('color', '#FF7DB5'), stroke_width=14, stroke_fill='white')
        t = t.rotate(-6, resample=Image.BICUBIC); c.alpha_composite(t, (0, H-230))
    c = c.crop(c.getbbox()); out = os.path.join(a.outdir, f"reaction-{p['name']}.png"); c.save(out); print('saved', out, c.size)
