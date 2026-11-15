"""มาสคอตประจำช่อง "น้องนางาจิ" (v2 คาวาอี้ + ขอบสติกเกอร์) — วาดด้วยโค้ด หน้าตาเหมือนเดิมทุกคลิป

ใช้งาน:
    from character import draw_nagaji
    img = draw_nagaji(pose="wave", face="smile", height=900)   # RGBA พื้นโปร่งใส มีขอบสติกเกอร์ขาว

pose:  stand | wave | point | think | cheer
face:  smile | talk | surprised | wink | happy | think
ขยับปากตอนพูด: สลับ face="smile" ↔ "talk" ทุก ~0.12 วิ · กะพริบตา: ใช้ face="happy" 2–3 เฟรม
แผ่นตัวละคร: python3 office/editor/character.py sheet.png
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter

S = 4
BW, BH = 600, 820
OUT = (70, 40, 44)
SKIN = (255, 224, 204)
SKIN_SH = (248, 196, 178)
HAIR = (92, 52, 46)
HAIR_HI = (150, 96, 76)
HAIR_TIP = (160, 104, 80)
EYE = (58, 35, 40)
IRIS = (150, 92, 64)
BLUSH = (255, 140, 165, 150)
BLOUSE = (255, 255, 255)
DOT = (110, 160, 230)
PANTS = (128, 84, 58)
PINK = (255, 105, 160)
GLASS = (40, 30, 36)
LW = 7  # ความหนาเส้นขอบ


def _s(pts):
    return [(x * S, y * S) for x, y in pts]


def _chaikin(pts, it=3, closed=True):
    for _ in range(it):
        new = []
        n = len(pts)
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            p, q = pts[i], pts[(i + 1) % n]
            new += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]),
                    (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        pts = new
    return pts


def _blob(d, pts, fill, it=3, outline=True):
    sm = _s(_chaikin(pts, it))
    d.polygon(sm, fill=fill, outline=OUT if outline else None, width=LW * S if outline else 0)


def _ell(d, box, fill, outline=True, w=LW):
    d.ellipse([v * S for v in box], fill=fill, outline=OUT if outline else None, width=w * S if outline else 0)


def _arm(d, a, b, w=30):
    for col, ww in ((OUT, w + 2 * LW), (SKIN, w)):
        d.line([a[0] * S, a[1] * S, b[0] * S, b[1] * S], fill=col, width=ww * S)
        for x, y in (a, b):
            r = ww * S / 2
            d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=col)
    r = 22
    _ell(d, (b[0] - r, b[1] - r, b[0] + r, b[1] + r), SKIN)


def draw_nagaji(pose="stand", face="smile", height=820, sticker=True):
    im = Image.new("RGBA", (BW * S, BH * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # ---- ผมด้านหลัง (ลอนนุ่ม ปลายสว่าง)
    back = [(300, 86), (412, 100), (488, 172), (512, 292), (505, 420), (522, 520), (478, 588), (428, 560),
            (392, 596), (340, 548), (260, 548), (208, 596), (172, 560), (122, 588), (78, 520), (95, 420),
            (88, 292), (112, 172), (188, 100)]
    _blob(d, back, HAIR)
    tips = [(96, 470), (150, 520), (205, 545), (250, 520), (350, 520), (395, 545), (450, 520), (504, 470),
            (515, 528), (478, 590), (430, 562), (392, 598), (340, 550), (260, 550), (208, 598), (170, 562),
            (122, 590), (84, 528)]
    _blob(d, tips, HAIR_TIP, it=3, outline=False)

    # ---- ตัว (เล็ก น่ารัก)
    _blob(d, [(228, 600), (372, 600), (386, 700), (308, 700), (300, 650), (292, 700), (214, 700)], PANTS, it=1)
    _ell(d, (205, 688, 292, 722), (255, 250, 248))
    _ell(d, (308, 688, 395, 722), (255, 250, 248))
    _blob(d, [(232, 455), (368, 455), (392, 610), (208, 610)], BLOUSE, it=2)
    _ell(d, (182, 452, 262, 532), BLOUSE)
    _ell(d, (338, 452, 418, 532), BLOUSE)
    for (x, y) in [(250, 500), (300, 520), (348, 498), (268, 575), (330, 585), (225, 545), (372, 555),
                   (205, 490), (395, 490), (300, 470)]:
        for k in range(5):
            a = k * 2 * math.pi / 5
            cx, cy = x + 7 * math.cos(a), y + 7 * math.sin(a)
            d.ellipse(((cx - 4) * S, (cy - 4) * S, (cx + 4) * S, (cy + 4) * S), fill=DOT)
        d.ellipse(((x - 3) * S, (y - 3) * S, (x + 3) * S, (y + 3) * S), fill=(255, 214, 110))

    # ---- แขน
    L, R = (198, 505), (402, 505)
    arms = {"stand": [(L, (186, 600)), (R, (414, 600))],
            "wave": [(L, (186, 600)), (R, (478, 372))],
            "point": [(L, (186, 600)), (R, (520, 470))],
            "think": [(L, (186, 600)), (R, (338, 448))],
            "cheer": [(L, (116, 360)), (R, (484, 360))]}[pose]
    for a, b in arms:
        _arm(d, a, b)
    if pose == "point":
        _arm(d, (530, 462), (562, 446), w=11)

    # ---- หน้า
    _ell(d, (138, 168, 462, 462), SKIN)
    # เงาใต้หน้าม้า
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([v * S for v in (160, 200, 440, 300)], fill=SKIN_SH + (160,))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([v * S for v in (146, 176, 454, 454)], fill=255)
    im.paste(Image.alpha_composite(im.crop((0, 0) + im.size), sh), (0, 0), m)
    d = ImageDraw.Draw(im)

    # ---- ตา (โต เป็นประกาย)
    ey = 335
    eyes = (236, 364)

    def glossy(x, big=False, look=(0, 0)):
        w, h = (30, 40) if big else (27, 36)
        x += look[0]
        y = ey + look[1]
        d.ellipse(((x - w) * S, (y - h) * S, (x + w) * S, (y + h) * S), fill=EYE)
        d.ellipse(((x - w + 7) * S, (y - 2) * S, (x + w - 7) * S, (y + h - 5) * S), fill=IRIS)
        d.ellipse(((x - w + 12) * S, (y + 8) * S, (x + w - 12) * S, (y + h - 9) * S), fill=(190, 128, 90))
        d.ellipse(((x - 17) * S, (y - 26) * S, (x + 1) * S, (y - 8) * S), fill=(255, 255, 255))
        d.ellipse(((x + 8) * S, (y + 8) * S, (x + 16) * S, (y + 16) * S), fill=(255, 255, 255))
        # ขนตาบน + หางตา
        d.arc(((x - w - 2) * S, (y - h - 2) * S, (x + w + 2) * S, (y + h + 2) * S), 200, 340, fill=EYE, width=8 * S)
        side = -1 if x < 300 else 1
        d.line(((x + side * (w - 2)) * S, (y - h * 0.55) * S, (x + side * (w + 10)) * S, (y - h * 0.8) * S),
               fill=EYE, width=6 * S)

    def closed(x):
        d.arc(((x - 26) * S, (ey - 16) * S, (x + 26) * S, (ey + 20) * S), 200, 340, fill=EYE, width=9 * S)

    if face in ("smile", "talk"):
        glossy(eyes[0]); glossy(eyes[1])
    elif face == "surprised":
        glossy(eyes[0], True); glossy(eyes[1], True)
    elif face == "wink":
        glossy(eyes[0]); closed(eyes[1])
    elif face == "happy":
        closed(eyes[0]); closed(eyes[1])
    elif face == "think":
        glossy(eyes[0], look=(7, -6)); glossy(eyes[1], look=(7, -6))

    # คิ้ว
    by = ey - (68 if face == "surprised" else 60)
    for x in eyes:
        d.arc(((x - 20) * S, by * S, (x + 20) * S, (by + 18) * S), 200, 340, fill=HAIR, width=6 * S)

    # แก้ม + ขีดเขิน
    bl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bl)
    for cx in (196, 404):
        bd.ellipse(((cx - 30) * S, 378 * S, (cx + 30) * S, 404 * S), fill=BLUSH)
    im.alpha_composite(bl)
    d = ImageDraw.Draw(im)
    for cx in (196, 404):
        for k in (-12, 0, 12):
            d.line(((cx + k - 4) * S, 396 * S, (cx + k + 4) * S, 386 * S), fill=(235, 100, 130), width=3 * S)

    # ปาก
    if face == "talk":
        d.chord((282 * S, 392 * S, 318 * S, 430 * S), 0, 180, fill=(170, 60, 80), outline=OUT, width=3 * S)
        d.chord((290 * S, 410 * S, 310 * S, 426 * S), 0, 180, fill=(255, 140, 160))
    elif face == "surprised":
        d.ellipse((288 * S, 396 * S, 312 * S, 424 * S), fill=(170, 60, 80), outline=OUT, width=3 * S)
    elif face == "think":
        d.line((288 * S, 410 * S, 314 * S, 404 * S), fill=OUT, width=5 * S)
    else:  # ปากแมว ω
        d.arc((276 * S, 392 * S, 302 * S, 414 * S), 20, 160, fill=OUT, width=5 * S)
        d.arc((298 * S, 392 * S, 324 * S, 414 * S), 20, 160, fill=OUT, width=5 * S)

    # ---- หน้าม้า (ลอยเป็นปอย ๆ)
    bangs = [(112, 230), (130, 150), (205, 100), (300, 88), (402, 104), (474, 160), (490, 238), (462, 222),
             (448, 262), (412, 200), (378, 252), (346, 192), (306, 262), (270, 190), (232, 252), (200, 205),
             (160, 268), (134, 238)]
    _blob(d, bangs, HAIR, it=2)
    d.arc((170 * S, 112 * S, 430 * S, 300 * S), 205, 300, fill=HAIR_HI, width=14 * S)  # เงาผม

    # ---- แว่นกันแดดคาดหัว + กิ๊บโบว์ชมพู
    for x0 in (196, 312):
        d.rounded_rectangle((x0 * S, 118 * S, (x0 + 92) * S, 162 * S), radius=18 * S, fill=GLASS, outline=OUT, width=4 * S)
        d.line(((x0 + 14) * S, 130 * S, (x0 + 40) * S, 130 * S), fill=(130, 120, 130), width=4 * S)
    d.line((288 * S, 138 * S, 312 * S, 138 * S), fill=GLASS, width=7 * S)
    bx, byy = 452, 222
    for side in (-1, 1):
        d.polygon(_s([(bx, byy), (bx + side * 36, byy - 24), (bx + side * 36, byy + 24)]), fill=PINK, outline=OUT, width=4 * S)
    _ell(d, (bx - 11, byy - 11, bx + 11, byy + 11), (255, 160, 200), w=4)

    out = im.resize((BW, BH), Image.LANCZOS)
    if sticker:  # ขอบสติกเกอร์ขาว + เงานุ่ม
        a = out.getchannel("A").point(lambda v: 255 if v > 20 else 0)
        rim = a.filter(ImageFilter.MaxFilter(23))
        canvas = Image.new("RGBA", out.size, (0, 0, 0, 0))
        shadow = Image.new("RGBA", out.size, (120, 40, 70, 0))
        shadow.putalpha(rim.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.35)))
        canvas.alpha_composite(shadow, (0, 0))
        white = Image.new("RGBA", out.size, (255, 255, 255, 0))
        white.putalpha(rim)
        canvas.alpha_composite(white)
        canvas.alpha_composite(out)
        out = canvas
    if height != BH:
        out = out.resize((int(BW * height / BH), height), Image.LANCZOS)
    return out


def sheet(path):
    import os
    from PIL import ImageFont
    fonts = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
    f = ImageFont.truetype(os.path.join(fonts, "Prompt-Medium.ttf"), 30, layout_engine=ImageFont.Layout.RAQM)
    ft = ImageFont.truetype(os.path.join(fonts, "PlayfairDisplay-Italic.ttf"), 64, layout_engine=ImageFont.Layout.RAQM)
    ft.set_variation_by_axes([600])
    combos = [("stand", "smile", "ยืนยิ้ม"), ("wave", "happy", "ทักทาย"), ("point", "talk", "ชี้ + พูด"),
              ("think", "think", "สงสัย"), ("cheer", "surprised", "ตกใจ/ว้าว"), ("stand", "wink", "ขยิบตา")]
    W, H = 1500, 1260
    sh = Image.new("RGBA", (W, H), (251, 228, 236, 255))
    d = ImageDraw.Draw(sh)
    for x in range(0, W, 60):
        d.rectangle((x, 0, x + 28, H), fill=(253, 236, 242))
    d.text((W / 2, 40), "Nagaji · mascot sheet", font=ft, fill=(214, 70, 130), anchor="mt")
    for i, (p, fa, lab) in enumerate(combos):
        c, r = i % 3, i // 3
        ch = draw_nagaji(p, fa, height=470)
        x = 120 + c * 450
        y = 150 + r * 560
        sh.alpha_composite(ch, (x + 160 - ch.width // 2, y))
        d.rounded_rectangle((x + 80, y + 478, x + 240, y + 524), radius=23, fill=(255, 255, 255))
        d.text((x + 160, y + 501), lab, font=f, fill=(43, 34, 48), anchor="mm")
    sh.convert("RGB").save(path)


if __name__ == "__main__":
    sheet(sys.argv[1] if len(sys.argv) > 1 else "nagaji-sheet.png")
