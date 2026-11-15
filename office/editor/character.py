"""ตัวละครประจำช่อง "น้องนางาจิ" — วาดด้วยโค้ด หน้าตาเหมือนเดิมทุกคลิป

ใช้งาน:
    from character import draw_nagaji
    img = draw_nagaji(pose="wave", face="smile", height=900)   # RGBA พื้นโปร่งใส

pose:  stand | wave | point | think | cheer
face:  smile | talk | surprised | wink | happy | think
หากต้องการขยับปากตอนพูด ให้สลับ face="smile" กับ "talk" ทุก ~0.12 วิ
สั่งแสดงแผ่นตัวละคร: python3 office/editor/character.py sheet.png
"""
import math
import sys

from PIL import Image, ImageDraw

S = 4                      # วาดใหญ่ 4 เท่าแล้วย่อ = ขอบเนียน
BW, BH = 600, 900          # กรอบตัวละครพื้นฐาน
SKIN = (255, 219, 196)
SKIN_D = (240, 188, 160)
HAIR = (74, 44, 40)
HAIR_L = (138, 90, 68)
INK = (59, 42, 46)
BLUSH = (255, 150, 170, 150)
BLOUSE = (250, 250, 255)
DOT = (120, 160, 220)
PANTS = (122, 78, 53)
SHOE = (240, 235, 230)
GLASS = (45, 35, 40)


def _p(*xy):
    return [v * S for v in xy]


def _limb(d, a, b, w, col):
    d.line(_p(*a, *b), fill=col, width=w * S)
    r = w * S / 2
    for x, y in (a, b):
        d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=col)


def draw_nagaji(pose="stand", face="smile", height=900, glasses=True):
    im = Image.new("RGBA", (BW * S, BH * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # ผมด้านหลัง (ยาวถึงไหล่ ปลายสว่าง)
    d.ellipse(_p(112, 118, 488, 520), fill=HAIR)
    d.rounded_rectangle(_p(122, 300, 478, 600), radius=90 * S, fill=HAIR)
    d.rounded_rectangle(_p(126, 520, 474, 610), radius=60 * S, fill=HAIR_L)   # ปลายผมสว่าง
    for i, x in enumerate(range(132, 420, 58)):                                 # ปลายลอนเรียงในกรอบผม
        d.ellipse(_p(x, 572 + (i % 2) * 10, x + 66, 636 + (i % 2) * 10), fill=HAIR_L)

    # คอ + ตัว
    d.rounded_rectangle(_p(278, 425, 322, 475), radius=12 * S, fill=SKIN_D)
    # กางเกงขายาวทรงกว้าง
    d.polygon(_p(205, 630, 395, 630, 425, 855, 315, 855, 300, 700, 285, 855, 175, 855), fill=PANTS)
    d.ellipse(_p(178, 840, 282, 880), fill=SHOE)
    d.ellipse(_p(318, 840, 422, 880), fill=SHOE)
    # เสื้อแขนตุ๊กตา ลายดอกฟ้า
    d.polygon(_p(222, 460, 378, 460, 408, 645, 192, 645), fill=BLOUSE)
    d.ellipse(_p(160, 455, 250, 545), fill=BLOUSE)
    d.ellipse(_p(350, 455, 440, 545), fill=BLOUSE)
    for (x, y) in [(240, 500), (290, 520), (340, 495), (260, 575), (320, 590), (365, 560), (215, 600),
                   (380, 615), (190, 490), (410, 495), (300, 470)]:
        for k in range(5):
            a = k * 2 * math.pi / 5
            cx, cy = x + 7 * math.cos(a), y + 7 * math.sin(a)
            d.ellipse(_p(cx - 4, cy - 4, cx + 4, cy + 4), fill=DOT)
        d.ellipse(_p(x - 3, y - 3, x + 3, y + 3), fill=(255, 220, 120))
    d.arc(_p(255, 440, 345, 490), 20, 160, fill=(225, 225, 235), width=4 * S)  # คอเสื้อ

    # แขน
    L_sh, R_sh = (190, 505), (410, 505)
    arms = {
        "stand": [(L_sh, (180, 625)), (R_sh, (420, 625))],
        "wave": [(L_sh, (180, 625)), (R_sh, (480, 330))],
        "point": [(L_sh, (180, 625)), (R_sh, (540, 470))],
        "think": [(L_sh, (180, 625)), (R_sh, (330, 430))],
        "cheer": [(L_sh, (110, 330)), (R_sh, (490, 330))],
    }[pose]
    for a, b in arms:
        _limb(d, a, b, 34, SKIN)
        d.ellipse(_p(b[0] - 24, b[1] - 24, b[0] + 24, b[1] + 24), fill=SKIN)
    if pose == "point":  # นิ้วชี้
        _limb(d, (556, 462), (588, 448), 12, SKIN)
    if pose == "think":
        _limb(d, (330, 420), (318, 398), 12, SKIN)

    # หน้า
    d.ellipse(_p(150, 165, 450, 445), fill=SKIN)
    # หน้าม้าปัดข้าง (ด้านบน + ขอบหยัก)
    d.chord(_p(136, 98, 464, 360), 180, 360, fill=HAIR)
    # หน้าม้าปัดข้าง: สองก้อนโค้งซ้อนกัน แสกเยื้องซ้าย
    d.ellipse(_p(140, 168, 300, 262), fill=HAIR)
    d.ellipse(_p(228, 150, 462, 258), fill=HAIR)
    d.polygon(_p(136, 228, 150, 330, 172, 250), fill=HAIR)       # ผมข้างแก้มซ้าย
    d.polygon(_p(464, 228, 450, 330, 428, 250), fill=HAIR)       # ผมข้างแก้มขวา
    if glasses:  # แว่นกันแดดคาดหัว
        d.rounded_rectangle(_p(205, 132, 290, 172), radius=16 * S, fill=GLASS)
        d.rounded_rectangle(_p(310, 132, 395, 172), radius=16 * S, fill=GLASS)
        d.line(_p(288, 150, 312, 150), fill=GLASS, width=6 * S)
        d.line(_p(214, 142, 246, 142), fill=(110, 100, 110), width=4 * S)

    # ตา
    ex = (248, 352)
    ey = 318
    def oval_eye(x, big=False, look=(0, 0)):
        w, h = (19, 25) if big else (16, 21)
        d.ellipse(_p(x - w + look[0], ey - h + look[1], x + w + look[0], ey + h + look[1]), fill=INK)
        d.ellipse(_p(x - 6 + look[0], ey - 12 + look[1], x + 3 + look[0], ey - 3 + look[1]), fill=(255, 255, 255))
    def arc_eye(x):
        d.arc(_p(x - 20, ey - 14, x + 20, ey + 16), 200, 340, fill=INK, width=7 * S)
    if face in ("smile", "talk"):
        oval_eye(ex[0]); oval_eye(ex[1])
    elif face == "surprised":
        oval_eye(ex[0], True); oval_eye(ex[1], True)
    elif face == "wink":
        oval_eye(ex[0]); arc_eye(ex[1])
    elif face == "happy":
        arc_eye(ex[0]); arc_eye(ex[1])
    elif face == "think":
        oval_eye(ex[0], look=(6, -6)); oval_eye(ex[1], look=(6, -6))
    # คิ้วโค้งเล็ก ๆ (ยกขึ้นตอนตกใจ)
    by = ey - (52 if face == "surprised" else 44)
    for x in ex:
        d.arc(_p(x - 20, by, x + 20, by + 22), 200, 340, fill=HAIR, width=6 * S)
    # แก้ม
    bl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bl)
    bd.ellipse(_p(196, 352, 244, 380), fill=BLUSH)
    bd.ellipse(_p(356, 352, 404, 380), fill=BLUSH)
    im.alpha_composite(bl)
    d = ImageDraw.Draw(im)
    # ปาก
    if face == "talk":
        d.chord(_p(280, 378, 320, 418), 0, 180, fill=(190, 70, 90))
        d.chord(_p(288, 398, 312, 414), 0, 180, fill=(255, 150, 160))
    elif face == "surprised":
        d.ellipse(_p(288, 385, 312, 413), fill=(190, 70, 90))
    elif face == "think":
        d.line(_p(286, 398, 314, 394), fill=(190, 70, 90), width=6 * S)
    else:
        d.arc(_p(276, 372, 324, 404), 20, 160, fill=(190, 70, 90), width=7 * S)

    out = im.resize((BW, BH), Image.LANCZOS)
    if height != BH:
        out = out.resize((int(BW * height / BH), height), Image.LANCZOS)
    return out


def sheet(path):
    from PIL import ImageFont
    import os
    fonts = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
    f = ImageFont.truetype(os.path.join(fonts, "Prompt-Medium.ttf"), 30, layout_engine=ImageFont.Layout.RAQM)
    ft = ImageFont.truetype(os.path.join(fonts, "PlayfairDisplay-Italic.ttf"), 64, layout_engine=ImageFont.Layout.RAQM)
    ft.set_variation_by_axes([600])
    combos = [("stand", "smile", "ยืนยิ้ม"), ("wave", "happy", "ทักทาย"), ("point", "talk", "ชี้ + พูด"),
              ("think", "think", "สงสัย"), ("cheer", "surprised", "ตกใจ/ว้าว"), ("stand", "wink", "ขยิบตา")]
    W, H = 1500, 1260
    sh = Image.new("RGBA", (W, H), (251, 228, 236, 255))
    d = ImageDraw.Draw(sh)
    d.text((W / 2, 40), "Nagaji · character sheet", font=ft, fill=(214, 70, 130), anchor="mt")
    for i, (p, fa, lab) in enumerate(combos):
        c, r = i % 3, i // 3
        ch = draw_nagaji(p, fa, height=480)
        x = 120 + c * 450
        y = 150 + r * 560
        d.rounded_rectangle((x - 30, y - 10, x + 350, y + 520), radius=36, fill=(255, 255, 255))
        sh.alpha_composite(ch, (x + 160 - ch.width // 2, y))
        d.text((x + 160, y + 490), lab, font=f, fill=(43, 34, 48), anchor="mm")
    sh.convert("RGB").save(path)


if __name__ == "__main__":
    sheet(sys.argv[1] if len(sys.argv) > 1 else "nagaji-sheet.png")
