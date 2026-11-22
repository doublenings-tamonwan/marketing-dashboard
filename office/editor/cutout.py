"""ไดคัตคน/ลบพื้นหลัง (rembg) → PNG พื้นโปร่งใส + ทำเป็นสติกเกอร์ขอบขาวได้
ใช้:
  python3 -I office/editor/cutout.py <รูป> --out cut.png                 # ไดคัตทั้งภาพ (คนทุกคน)
  python3 -I office/editor/cutout.py <รูป> --out head.png --box 0.33,0.30,0.30,0.45 --sticker
      --box x,y,w,h = ครอปก่อนไดคัต (สัดส่วน 0–1 ของภาพ) ใช้เลือกคนเดียว/เฉพาะหัว
      --main        = เก็บเฉพาะคนที่อยู่กลางกรอบ (ตัดมือ/ตัวเพื่อนที่ติดมาทิ้ง)
      --sticker     = ขอบขาวหนา + เงานุ่ม แบบสติกเกอร์สแครปบุ๊ก
  --model birefnet-portrait (ค่าเริ่มต้น สวยสุด ช้า ~1 นาที/ภาพ) | u2net_human_seg (เร็ว) | isnet-general-use (ของ/สินค้า)
- โมเดลโหลดจาก GitHub ครั้งแรกเก็บที่ ~/.rembg/models (birefnet ~970MB)
- ไดคัตเฉพาะเจ้าของช่อง/คนที่อนุญาตเท่านั้น · ห้ามไดคัตดารา/คนดัง/คนแปลกหน้ามาลงคลิป
"""
import argparse
from PIL import Image, ImageFilter
from rembg import remove, new_session

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('--out', required=True)
ap.add_argument('--model', default='birefnet-portrait')
ap.add_argument('--box', help='x,y,w,h สัดส่วน 0-1')
ap.add_argument('--main', action='store_true', help='เก็บเฉพาะก้อนคนที่อยู่กลางกรอบ (ตัดมือ/ตัวคนข้าง ๆ ทิ้ง)')
ap.add_argument('--sticker', action='store_true'); ap.add_argument('--border', type=int, default=18)
a = ap.parse_args()
im = Image.open(a.src).convert('RGB')
if a.box:
    x, y, w, h = map(float, a.box.split(','))
    W, H = im.size; im = im.crop((int(x*W), int(y*H), int((x+w)*W), int((y+h)*H)))
cut = remove(im, session=new_session(a.model), post_process_mask=True).convert('RGBA')
if a.main:
    import numpy as np
    from scipy import ndimage
    al = np.array(cut.split()[3]); lab, n = ndimage.label(al > 40)
    if n > 1:
        cy, cx = al.shape[0]//2, al.shape[1]//2
        k = lab[cy, cx] or (np.bincount(lab.ravel())[1:].argmax() + 1)
        al[lab != k] = 0; cut.putalpha(Image.fromarray(al))
cut = cut.crop(cut.getbbox())
if a.sticker:
    b = a.border; pad = b * 3
    base = Image.new('RGBA', (cut.width + pad*2, cut.height + pad*2), (0, 0, 0, 0)); base.paste(cut, (pad, pad), cut)
    alpha = base.split()[3].point(lambda v: 255 if v > 40 else 0)
    outline = alpha.filter(ImageFilter.MaxFilter(b*2+1)).filter(ImageFilter.GaussianBlur(1.2))
    shadow = outline.filter(ImageFilter.GaussianBlur(b)).point(lambda v: int(v*0.35))
    st = Image.new('RGBA', base.size, (0, 0, 0, 0))
    st.paste((60, 20, 40, 255), (b//2, b), shadow)
    st.paste((255, 255, 255, 255), (0, 0), outline)
    st.alpha_composite(base)
    cut = st.crop(st.getbbox())
cut.save(a.out)
print('saved', a.out, cut.size)
