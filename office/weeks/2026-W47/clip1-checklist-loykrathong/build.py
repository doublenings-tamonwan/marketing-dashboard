"""เช็กลิสต์เที่ยว EP.1 · ไปลอยกระทงคนเยอะ เช็กอะไรบ้าง — คลิปกราฟิกล้วน (ไม่มีฟุตเทจ ไม่มีเสียง)

    python3 office/weeks/2026-W47/clip1-checklist-loykrathong/build.py [--out-dir DIR] [--only cover|video]

ขั้นตอน: วาดพื้น + ไอคอน (PIL ทุกตัว ไม่ใช้ฟอนต์อีโมจิ) → base.mp4
        → ซับไทยด้วย office/editor/burn_subs.py --mute → loykrathong-ep1-preview.mp4
        → ปก: วาดภาพพื้น + กระทง แล้วส่งเข้า office/editor/make_cover.py → cover.png
ข้อความบนจอ = สคริปต์มุม A (แก้ตาม fact-checker แล้ว) · ไม่มีอีโมจิ · คำ [ตรวจ]/(มุก) ไม่ขึ้นจอ
พื้นที่ปลอดภัย: บน 180px · ล่าง 350px · ขวา 140px (ข้อความสำคัญอยู่ในกรอบ x 100–940, y 180–1570)
"""
import argparse
import json
import math
import os
import random
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EDITOR = os.path.join(ROOT, "editor")
FONTS = os.path.join(ROOT, "assets", "fonts")
sys.path.insert(0, EDITOR)
from burn_subs import render_clean  # noqa: E402  (ใช้วัดขนาดซับให้ตรงกับที่ burn_subs วาดจริง)

DEFAULT_OUT = ("/tmp/claude-0/-home-user-marketing-dashboard/d151a6a9-7df2-5f3b-8b43-ea4e410e4670/"
               "scratchpad/loykrathong")
W, H, FPS = 1080, 1920, 30
SAFE_R = 940            # ขอบขวาของข้อความสำคัญ (เว้น 140px ให้ปุ่ม TikTok)
SAFE_B = H - 350        # ขอบล่างของข้อความสำคัญ
TEXT_MAXW = 2 * (SAFE_R - W // 2)  # ซับวางกึ่งกลาง → กว้างได้ไม่เกิน 800px

INK = (28, 24, 48)
PINK_BG = (255, 214, 231)
PINK_FG = (122, 14, 59)
ACCENT = (232, 90, 150)
CREAM = (255, 248, 236)
WARM = (255, 196, 110)

# ---------------- เส้นเวลา ----------------
HOOK_END = 1.5
ITEM0, ITEM_LEN, N_ITEMS = 1.5, 2.0, 7
SUM_START = ITEM0 + ITEM_LEN * N_ITEMS        # 15.5
OUTRO_START = SUM_START + 3.0                 # 18.5 (การ์ดสรุปนิ่งเต็ม ~2.55 วิ)
TOTAL = OUTRO_START + 2.5                     # 21.0

ITEMS = [
    # (ไอคอน, บรรทัดใหญ่, บรรทัดใหญ่แบบ 2 บรรทัดถ้ายาวเกิน, บรรทัดเล็ก, ข้อความในการ์ดสรุป)
    ("battery", "1 [แบตสำรอง] ชาร์จเต็ม", None,
     "คนแน่น หาแก๊งไม่เจอ\nแบตหมด = จบ", "แบตสำรอง ชาร์จเต็ม"),
    ("pin", "2 นัด [จุดเจอ] ก่อนเข้างาน", "2 นัด [จุดเจอ]\nก่อนเข้างาน",
     "หลงกันเมื่อไหร่ ไปรอตรงนั้นเลย", "นัดจุดเจอ ก่อนเข้างาน"),
    ("money", "3 พก [แบงก์ย่อย] ติดตัว", None,
     "เผื่อไว้ ซื้อของจุกจิกคล่องมือ", "พกแบงก์ย่อย ติดตัว"),
    ("bag", "4 [กระเป๋า]ปิดซิป ไว้ด้านหน้า", "4 [กระเป๋า]ปิดซิป\nไว้ด้านหน้า",
     "คนเบียด ระวังของหาย", "กระเป๋าปิดซิป ไว้ด้านหน้า"),
    ("shoes", "5 [รองเท้า]ใส่สบาย ไม่ลื่น", "5 [รองเท้า]ใส่สบาย\nไม่ลื่น",
     "ริมน้ำพื้นอาจเปียก\nส้นสูงเก็บไว้ถ่ายรูปที่บ้าน", "รองเท้าใส่สบาย ไม่ลื่น"),
    ("mosquito", "6 [ยากันยุง]", None,
     "ยุงริมน้ำก็มาเที่ยวงานนะ\nแต่ไม่ได้มาลอยกระทง", "ยากันยุง"),
    ("krathong", "7 กระทง[วัสดุธรรมชาติ] ไม่เอาโฟม", "7 กระทง[วัสดุธรรมชาติ]\nไม่เอาโฟม",
     "ไปเป็นแก๊ง ลอยรวมกระทงเดียวก็ได้", "กระทงวัสดุธรรมชาติ ไม่เอาโฟม"),
]
OPTIONS = ["แฟน", "แก๊ง", "ลอยใจอยู่บ้าน"]
ICON_C = (540, 715)     # กลางไอคอนในหน้าข้อ
ICON_S = 430


def F(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def clamp(x):
    return max(0.0, min(1.0, x))


def ease(x):
    return 1 - (1 - clamp(x)) ** 3


def back(x, s=2.2):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def bounce(x):
    x = clamp(x)
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d
        return n * x * x + 0.75
    if x < 2.5 / d:
        x -= 2.25 / d
        return n * x * x + 0.9375
    x -= 2.625 / d
    return n * x * x + 0.984375


# ---------------- ปากกาวาดไอคอน (พิกัด 0–100, วาด 2 เท่าแล้วย่อให้ขอบเนียน) ----------------
class Pen:
    def __init__(self, S, ss=2):
        self.S, self.N = S, S * ss
        self.k = self.N / 100
        self.im = Image.new("RGBA", (self.N, self.N), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def p(self, *v):
        return [x * self.k for x in v]

    def w(self, v):
        return max(1, int(round(v * self.k)))

    def ell(self, x0, y0, x1, y1, fill, ol=INK, w=1.5):
        if ol:
            e = w * 0.5
            self.d.ellipse(self.p(x0 - e, y0 - e, x1 + e, y1 + e), fill=ol)
            self.d.ellipse(self.p(x0 + e, y0 + e, x1 - e, y1 - e), fill=fill)
        else:
            self.d.ellipse(self.p(x0, y0, x1, y1), fill=fill)

    def circ(self, cx, cy, r, fill, ol=INK, w=1.5):
        self.ell(cx - r, cy - r, cx + r, cy + r, fill, ol, w)

    def rr(self, x0, y0, x1, y1, r, fill, ol=INK, w=1.5):
        self.d.rounded_rectangle(self.p(x0, y0, x1, y1), radius=r * self.k, fill=fill,
                                 outline=ol, width=self.w(w) if ol else 0)

    def poly(self, pts, fill, ol=INK, w=1.5):
        flat = [(x * self.k, y * self.k) for x, y in pts]
        if ol:
            self.d.polygon(flat, fill=ol)
            self.d.line(flat + [flat[0]], fill=ol, width=self.w(w), joint="curve")
            # เติมสีด้านในโดยหดรูปเข้าหาจุดกึ่งกลางเล็กน้อย
            cx = sum(x for x, _ in pts) / len(pts)
            cy = sum(y for _, y in pts) / len(pts)
            inner = []
            for x, y in pts:
                dx, dy = cx - x, cy - y
                L = math.hypot(dx, dy) or 1
                inner.append(((x + dx / L * w * 0.5) * self.k, (y + dy / L * w * 0.5) * self.k))
            self.d.polygon(inner, fill=fill)
        else:
            self.d.polygon(flat, fill=fill)

    def line(self, pts, fill=INK, w=1.5):
        self.d.line([(x * self.k, y * self.k) for x, y in pts], fill=fill, width=self.w(w), joint="curve")
        r = self.w(w) / 2
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse((x * self.k - r, y * self.k - r, x * self.k + r, y * self.k + r), fill=fill)

    def arc(self, box, a0, a1, fill=INK, w=1.5):
        self.d.arc(self.p(*box), a0, a1, fill=fill, width=self.w(w))

    def star(self, cx, cy, r, fill=(255, 236, 160)):
        pts = []
        for i in range(8):
            rr_ = r if i % 2 == 0 else r * 0.32
            a = math.pi / 4 * i - math.pi / 2
            pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
        self.poly(pts, fill, ol=None)

    def text(self, x, y, s, size, fill=INK, font="Prompt-SemiBold.ttf"):
        self.d.text((x * self.k, y * self.k), s, font=F(font, int(size * self.k)), fill=fill, anchor="mm")

    def done(self, sticker=True):
        im = self.im
        if sticker:  # ขอบขาวแบบสติกเกอร์ ให้ไอคอนเด่นบนพื้นกลางคืน
            a = im.getchannel("A").filter(ImageFilter.GaussianBlur(self.k * 1.6))
            a = a.point(lambda v: 255 if v > 6 else 0).filter(ImageFilter.GaussianBlur(self.k * 0.3))
            border = Image.new("RGBA", im.size, (255, 250, 244, 0))
            border.putalpha(a)
            border.alpha_composite(im)
            im = border
        return im.resize((self.S, self.S), Image.LANCZOS)


def place(dst, part, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    p = part
    if abs(scale - 1) > 1e-3:
        p = p.resize((max(1, int(p.width * scale)), max(1, int(p.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.05:
        p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        p = p.copy()
        p.putalpha(p.getchannel("A").point(lambda v: int(v * alpha)))
    dst.alpha_composite(p, (int(round(cx - p.width / 2)), int(round(cy - p.height / 2))))


def canvas(S):
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


# ---------------- ไอคอน ----------------
def icon_battery(S, t):
    P = Pen(S)
    P.rr(80, 40, 90, 60, 3, (205, 205, 220))
    P.rr(10, 28, 82, 72, 10, (252, 250, 244), w=2)
    n = 4 if t > 0.85 else min(4, int(t / 0.2) + 1)
    for i in range(n):
        x0 = 17 + i * 15.5
        col = (120, 222, 150) if (i < 3 or t > 0.85) else (190, 240, 200)
        P.rr(x0, 35, x0 + 12.5, 65, 3, col, ol=None)
    if t > 0.85:  # เต็มแล้วยิ้ม
        P.circ(38, 47, 2.6, INK, ol=None)
        P.circ(54, 47, 2.6, INK, ol=None)
        P.arc((40, 46, 52, 58), 20, 160, INK, 1.6)
        P.circ(33, 55, 2.6, (255, 160, 190), ol=None)
        P.circ(59, 55, 2.6, (255, 160, 190), ol=None)
        k = clamp((t - 0.85) / 0.2)
        P.star(92, 22, 7 * k)
        P.star(8, 80, 5 * k)
    # สายฟ้าเล็กบนหัว
    P.poly([(50, 6), (40, 22), (48, 22), (44, 34), (58, 16), (50, 16), (54, 6)], (255, 210, 80), w=1.2)
    return P.done()


def icon_pin(S, t):
    P = Pen(S)
    # แผนที่พับ
    P.poly([(10, 74), (36, 66), (62, 76), (90, 68), (90, 90), (62, 98), (36, 88), (10, 96)], (205, 236, 220))
    P.line([(36, 66), (36, 88)], (150, 190, 170), 0.8)
    P.line([(62, 76), (62, 98)], (150, 190, 170), 0.8)
    for i in range(6):
        x = 16 + i * 6
        P.circ(x, 89 - i * 1.6, 1.1, (232, 90, 150), ol=None)
    drop = -38 * (1 - bounce(t / 0.55))
    sh = 0.5 + 0.5 * bounce(t / 0.55)
    P.ell(50 - 12 * sh, 80 - 3 * sh, 50 + 12 * sh, 80 + 3 * sh, (60, 80, 70, 120), ol=None)
    y = drop
    P.poly([(31, 44 + y), (69, 44 + y), (50, 80 + y)], ACCENT, w=2)
    P.circ(50, 34 + y, 21, ACCENT, w=2)
    P.d.polygon([(32.5 * P.k, (44 + y) * P.k), (67.5 * P.k, (44 + y) * P.k), (50 * P.k, (76 + y) * P.k)],
                fill=ACCENT)
    P.circ(50, 34 + y, 8.5, (255, 255, 255), w=1.4)
    P.circ(42, 27 + y, 2.4, (255, 190, 215), ol=None)
    return P.done()


def note_img(S, col, dark, label):
    P = Pen(S)
    P.rr(4, 22, 96, 78, 6, col, w=2)
    P.rr(11, 29, 89, 71, 4, col, ol=dark, w=1.2)
    P.circ(50, 50, 14, (255, 255, 255, 170), ol=dark, w=1.2)
    P.text(50, 51, label, 13, dark)
    P.circ(22, 50, 4, dark, ol=None)
    P.circ(78, 50, 4, dark, ol=None)
    return P.done(sticker=False)


_NOTES = {}


def icon_money(S, t):
    if S not in _NOTES:
        _NOTES[S] = [note_img(int(S * 0.72), c, d, l) for c, d, l in
                     [((160, 214, 160), (50, 120, 60), "20"), ((150, 190, 240), (40, 80, 150), "50"),
                      ((245, 160, 160), (160, 40, 50), "100")]]
    im = canvas(S)
    for i, n in enumerate(_NOTES[S]):
        k = back((t - i * 0.12) / 0.35)
        ang = (14 - i * 14) + 3 * math.sin(t * 5 + i)
        place(im, n, S * (0.40 + 0.1 * i), S * (0.42 + 0.03 * i), scale=k, rot=ang)
    # เหรียญ
    P = Pen(S)
    for j, (x, y) in enumerate([(76, 84), (86, 78)]):
        if t > 0.5 + j * 0.12:
            P.circ(x, y, 9, (255, 205, 80), w=1.4)
            P.circ(x, y, 5.5, (255, 225, 130), ol=(200, 150, 40), w=0.8)
    P.circ(14, 22, 0.1, (0, 0, 0, 0), ol=None)
    coins = P.done(sticker=False)
    im.alpha_composite(coins)
    out = Pen(S)
    out.im = im.resize((out.N, out.N), Image.LANCZOS)
    out.d = ImageDraw.Draw(out.im)
    return out.done()


def icon_bag(S, t):
    P = Pen(S)
    P.arc((20, 6, 80, 86), 185, 355, INK, 6)
    P.arc((20, 6, 80, 86), 186, 354, (196, 140, 110), 3.4)
    P.rr(12, 38, 88, 88, 14, (255, 186, 206), w=2)
    P.rr(26, 60, 74, 80, 7, (255, 206, 222), ol=(214, 120, 150), w=1)
    # หัวใจบนกระเป๋าหน้า
    P.circ(46, 68, 3.6, ACCENT, ol=None)
    P.circ(54, 68, 3.6, ACCENT, ol=None)
    P.poly([(42.6, 69.4), (57.4, 69.4), (50, 77)], ACCENT, ol=None)
    # ซิป: ปิดจากซ้ายไปขวา
    xp = 20 + 58 * ease(t / 0.75)
    P.line([(20, 49), (80, 49)], (120, 70, 90), 1.4)
    if xp < 78:
        P.ell(xp, 46, 80, 52, (70, 30, 50), ol=None)
    for i in range(20):
        x = 21 + i * 3
        if x < xp:
            P.line([(x, 47.3), (x, 50.7)], (240, 200, 90), 0.9)
    P.rr(xp - 3, 47, xp + 3, 52, 1.5, (240, 190, 70), w=1)
    P.rr(xp - 2.4, 52, xp + 2.4, 63, 2, (240, 190, 70), w=1)
    if t > 0.75:
        k = clamp((t - 0.75) / 0.2)
        P.star(90, 38, 8 * k)
        P.star(84, 26, 4.5 * k)
    return P.done()


def part_sneaker(S):
    P = Pen(S)
    P.poly([(8, 66), (10, 44), (24, 38), (34, 42), (46, 54), (70, 58), (88, 64), (90, 70), (8, 72)],
           (252, 250, 246), w=2)
    P.rr(5, 68, 93, 80, 5, (255, 214, 231), w=2)
    P.line([(30, 50), (40, 64)], ACCENT, 2.4)
    P.line([(40, 49), (50, 63)], ACCENT, 2.4)
    for x in (22, 28):
        P.line([(x, 44), (x + 8, 44)], INK, 1.1)
    return P.done()


def part_heel(S):
    P = Pen(S)
    P.poly([(14, 34), (24, 30), (30, 42), (44, 56), (64, 66), (88, 70), (92, 78), (60, 78),
            (40, 66), (26, 52), (24, 86), (18, 86)], (236, 72, 96), w=2)
    P.line([(28, 38), (44, 54)], (255, 160, 175), 1.4)
    return P.done()


def part_nosign(S):
    P = Pen(S)
    P.circ(50, 50, 44, (0, 0, 0, 0), ol=(235, 40, 55), w=9)
    P.line([(20, 20), (80, 80)], (235, 40, 55), 9)
    return P.done(sticker=False)


_SH = {}


def icon_shoes(S, t):
    if S not in _SH:
        _SH[S] = (part_sneaker(int(S * 0.6)), part_heel(int(S * 0.56)), part_nosign(int(S * 0.58)))
    sn, he, ns = _SH[S]
    im = Image.new("RGBA", (int(S * 1.3), S), (0, 0, 0, 0))
    hop = abs(math.sin(t * math.pi * 2.6)) * S * 0.03 if t > 0.5 else 0
    place(im, sn, S * 0.32, S * 0.56 - hop, rot=4 * math.sin(t * 8) if t > 0.5 else 0)
    hit = 0.45
    shake = 0
    if t > hit:
        dt = t - hit
        shake = 14 * math.sin(dt * 38) * math.exp(-dt * 3.5)
    place(im, he, S * 0.96, S * 0.56, rot=shake)
    if t > hit - 0.1:
        k = clamp((t - hit + 0.1) / 0.25)
        place(im, ns, S * 0.96, S * 0.55, scale=1.9 - 0.9 * back(k, 3.0), alpha=ease(k * 2))
    return im


def part_mosquito(S, t):
    P = Pen(S)
    flap = abs(math.sin(t * 46))
    # ขา
    for x0, x1 in ((44, 36), (50, 48), (56, 60)):
        P.line([(x0, 57), (x0 - 2, 66), (x1, 78)], INK, 1.1)
    # ปีก (กระพือ)
    P.ell(40, 40 - 22 * flap, 58, 42, (205, 232, 255, 190), ol=(120, 150, 190), w=1)
    P.ell(48, 40 - 18 * flap, 72, 42, (205, 232, 255, 170), ol=(120, 150, 190), w=1)
    # ตัว
    P.ell(56, 46, 92, 60, (150, 136, 160), w=1.6)
    for x in (64, 72, 80):
        P.line([(x, 47.5), (x, 58.5)], (90, 76, 100), 1.6)
    P.ell(40, 40, 60, 60, (160, 146, 172), w=1.6)
    # หัว + ตาโต + ปากเข็ม
    P.line([(28, 52), (8, 60)], INK, 1.3)
    P.circ(32, 46, 10, (170, 156, 182), w=1.6)
    P.circ(30, 44, 5.4, (255, 255, 255), w=1)
    P.circ(29, 44.5, 2.6, INK, ol=None)
    P.circ(30, 43.5, 0.9, (255, 255, 255), ol=None)
    P.circ(36, 51, 2.2, (255, 160, 190), ol=None)
    # หมวกปาร์ตี้
    hat = [(25, 38), (39, 34), (28, 12)]
    P.poly(hat, (255, 120, 170), w=1.4)
    P.line([(27, 30), (35, 28)], (255, 226, 110), 2)
    P.line([(27, 22), (32, 21)], (255, 226, 110), 2)
    P.circ(28, 11, 3.6, (255, 226, 110), w=1.2)
    return P.done()


def part_spray(S, t):
    P = Pen(S)
    P.rr(40, 10, 60, 20, 3, (230, 230, 240), w=1.6)
    P.rr(34, 6, 46, 14, 2, (245, 245, 250), w=1.4)
    P.rr(28, 20, 72, 94, 10, (150, 220, 190), w=2)
    P.rr(32, 42, 68, 74, 5, (250, 250, 244), ol=None)
    # ใบไม้บนฉลาก
    P.poly([(42, 66), (50, 48), (58, 66)], (90, 170, 110), ol=None)
    P.line([(50, 52), (50, 70)], (60, 130, 80), 1)
    return P.done()


_SP = {}


def scene_mosquito(im, t, cx, cy, S, alpha=1.0):
    """ยุงใส่หมวกปาร์ตี้บินวน + สเปรย์กันยุงมุมซ้ายล่าง"""
    if S not in _SP:
        _SP[S] = part_spray(int(S * 0.42), 0)
    k = back(t / 0.3)
    place(im, _SP[S], cx - S * 0.30, cy + S * 0.24, scale=k, rot=4 * math.sin(t * 6), alpha=alpha)
    # puff
    for j in range(3):
        ph = ((t - 0.4) * 1.4 - j * 0.33) % 1.0
        if t > 0.4:
            r = 10 + 40 * ph
            a = int(130 * (1 - ph) * alpha)
            x = cx - S * 0.30 + 50 + 140 * ph
            y = cy + S * 0.24 - 70 - 60 * ph
            g = Image.new("RGBA", (int(2 * r + 4), int(2 * r + 4)), (0, 0, 0, 0))
            ImageDraw.Draw(g).ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=(230, 255, 245, a))
            im.alpha_composite(g, (int(x - r), int(y - r)))
    # เส้นทางบิน (จุดประ) + ยุง
    ang = t * 2 * math.pi / 1.5
    rx, ry = S * 0.26, S * 0.14
    ox, oy = cx + S * 0.08, cy - S * 0.08
    d = ImageDraw.Draw(im)
    for j in range(1, 10):
        a2 = ang - j * 0.22
        x, y = ox + rx * math.cos(a2), oy + ry * math.sin(a2) * 1.0
        r = 4.5
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(150 * (1 - j / 10) * alpha)))
    x, y = ox + rx * math.cos(ang), oy + ry * math.sin(ang) + 10 * math.sin(t * 9)
    vx = -math.sin(ang)  # ทิศบิน
    m = part_mosquito(int(S * 0.74), t)
    if vx > 0:  # ยุงหันหัวไปทางที่บิน (วาดหันซ้ายไว้)
        m = m.transpose(Image.FLIP_LEFT_RIGHT)
    place(im, m, x, y, scale=k, rot=8 * math.sin(t * 5), alpha=alpha)


def icon_krathong(S, t, mood="happy", sweat=0.0):
    P = Pen(S)
    flick = 1 + 0.12 * math.sin(t * 23) + 0.06 * math.sin(t * 37)
    # ธูป 3 ดอก
    for x0, x1 in ((40, 33), (43, 39), (46, 44)):
        P.line([(x0, 50), (x1, 18)], (150, 90, 60), 1.0)
        P.circ(x1, 18, 1.4, (255, 90, 60), ol=None)
    # เทียน + เปลวไฟ
    P.rr(53, 24, 61, 50, 2, (252, 244, 214), w=1.4)
    fh = 13 * flick
    P.poly([(57, 23 - fh), (52.4, 18), (54, 24), (60, 24), (61.6, 18)], (255, 196, 70), ol=None)
    P.circ(57, 19.5, 4.4, (255, 196, 70), ol=None)
    P.circ(57, 20.5, 2.2, (255, 244, 200), ol=None)
    # กลีบใบตองพับแหลมรอบขอบ (ด้านหลัง)
    for i in range(6):
        x = 20 + i * 12
        P.poly([(x - 7, 60), (x + 7, 60), (x, 41)], (98, 168, 86) if i % 2 else (124, 190, 100), w=1.3)
    # ดอกไม้
    for x, y, c in ((30, 50, (255, 170, 50)), (72, 50, (255, 140, 180)), (66, 46, (255, 190, 60))):
        for a in range(6):
            r_ = math.radians(a * 60)
            P.circ(x + 3.8 * math.cos(r_), y + 3.8 * math.sin(r_), 3.4, c, ol=None)
        P.circ(x, y, 2.4, (255, 236, 150), ol=None)
    # กลีบด้านหน้า
    for i in range(5):
        x = 26 + i * 12
        P.poly([(x - 8, 66), (x + 8, 66), (x, 50)], (112, 182, 94) if i % 2 else (88, 156, 78), w=1.3)
    # ฐานหยวกกล้วย
    P.rr(10, 62, 90, 84, 11, (196, 226, 150), w=1.8)
    P.line([(16, 72), (84, 72)], (160, 196, 120), 1)
    # หน้า
    P.circ(40, 74, 2.2, INK, ol=None)
    P.circ(60, 74, 2.2, INK, ol=None)
    if mood == "sad":
        P.arc((45, 77, 55, 85), 200, 340, INK, 1.4)
        P.line([(35, 70.5), (41, 68.5)], INK, 0.9)
        P.line([(59, 68.5), (65, 70.5)], INK, 0.9)
    else:
        P.arc((45, 72, 55, 80), 20, 160, INK, 1.4)
        P.circ(34, 78, 2.4, (255, 170, 190), ol=None)
        P.circ(66, 78, 2.4, (255, 170, 190), ol=None)
    if sweat > 0:
        y = 52 + 6 * sweat
        P.poly([(84, y - 9), (80.5, y), (87.5, y)], (150, 210, 255), w=1)
        P.circ(84, y + 0.5, 3.5, (150, 210, 255), w=1)
        P.d.polygon(P.p(81.6, y, 86.4, y, 84, y - 6.5), fill=(150, 210, 255))
    return P.done()


def icon_lantern(S, t=0):
    P = Pen(S)
    P.line([(50, 0), (50, 14)], (240, 190, 80), 1.4)
    P.ell(20, 16, 80, 82, (228, 62, 66), w=2)
    P.ell(34, 17, 66, 81, (0, 0, 0, 0), ol=(180, 36, 48), w=1.4)
    P.ell(45, 17, 55, 81, (0, 0, 0, 0), ol=(180, 36, 48), w=1.4)
    P.ell(28, 24, 44, 44, (255, 120, 110, 120), ol=None)
    P.rr(36, 10, 64, 21, 3, (245, 196, 84), w=1.6)
    P.rr(36, 77, 64, 88, 3, (245, 196, 84), w=1.6)
    for x in (46, 50, 54):
        P.line([(x, 88), (x, 99)], (245, 196, 84), 1.4)
    return P.done()


def check_badge(r, p):
    """วงกลมชมพูพร้อมเครื่องหมายถูก p=0–1 = ความยาวเส้นที่วาดแล้ว"""
    S = int(r * 2 + 16)
    im = Image.new("RGBA", (S * 2, S * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S
    R = r * 2
    d.ellipse((c - R - 12, c - R - 12, c + R + 12, c + R + 12), fill=(255, 250, 244))
    d.ellipse((c - R, c - R, c + R, c + R), fill=ACCENT)
    pts = [(-0.48, 0.02), (-0.14, 0.36), (0.52, -0.36)]
    pts = [(c + x * R, c + y * R) for x, y in pts]
    L1 = math.dist(pts[0], pts[1])
    L2 = math.dist(pts[1], pts[2])
    want = p * (L1 + L2)
    path = [pts[0]]
    if want <= L1:
        f = want / L1
        path.append((pts[0][0] + (pts[1][0] - pts[0][0]) * f, pts[0][1] + (pts[1][1] - pts[0][1]) * f))
    else:
        f = (want - L1) / L2
        path += [pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * f, pts[1][1] + (pts[2][1] - pts[1][1]) * f)]
    lw = int(R * 0.26)
    if p > 0:
        d.line(path, fill="white", width=lw, joint="curve")
        for x, y in (path[0], path[-1]):
            d.ellipse((x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2), fill="white")
    return im.resize((S, S), Image.LANCZOS)


ICONS = {"battery": icon_battery, "pin": icon_pin, "money": icon_money, "bag": icon_bag,
         "shoes": icon_shoes, "krathong": icon_krathong}


# ---------------- พื้นหลัง ----------------
def soft_dot(r, col):
    s = int(r * 4)
    im = Image.new("RGBA", (s, s), col + (0,))
    a = Image.new("L", (s, s), 0)
    ImageDraw.Draw(a).ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=255)
    im.putalpha(a.filter(ImageFilter.GaussianBlur(r * 0.6)))
    return im


WATER_Y = 1560


def make_moon():
    """พระจันทร์เต็มดวง (ขึ้น 15 ค่ำ) เล็ก ๆ — โชว์เฉพาะฮุก+หน้าข้อ (หลบหัวข้อการ์ดสรุป/คำถาม)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(m).ellipse((110, 300, 250, 440), fill=(255, 236, 190, 70))
    im.alpha_composite(m.filter(ImageFilter.GaussianBlur(30)))
    ImageDraw.Draw(im).ellipse((148, 338, 212, 402), fill=(252, 240, 210))
    ImageDraw.Draw(im).ellipse((164, 354, 178, 368), fill=(236, 222, 190))
    return im


def make_bg():
    top, bot = np.array([20, 33, 61]), np.array([31, 58, 95])  # #14213D → #1F3A5F
    grad = (top + (bot - top) * np.linspace(0, 1, H)[:, None] ** 1.2).astype("uint8")
    im = Image.fromarray(np.repeat(grad[:, None, :], W, axis=1), "RGB").convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse((80, 360, 1000, 1180), fill=(90, 120, 190, 60))        # แสงฟุ้งกลางจอ
    gd.ellipse((-200, WATER_Y - 260, W + 200, WATER_Y + 380), fill=(255, 170, 90, 70))  # แสงเทียนอุ่น
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(140)))
    # ผิวน้ำ
    water = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(water)
    for y in range(WATER_Y, H):
        f = (y - WATER_Y) / (H - WATER_Y)
        wd.line([(0, y), (W, y)], fill=(12, 24, 48, int(120 + 90 * f)))
    im.alpha_composite(water)
    ImageDraw.Draw(im).line([(0, WATER_Y), (W, WATER_Y)], fill=(255, 210, 150, 60), width=2)
    return im


def make_lights():
    rnd = random.Random(7)
    dots = [soft_dot(r, c) for r, c in [(5, (255, 210, 130)), (8, (255, 190, 110)), (12, (255, 170, 90)),
                                        (4, (255, 236, 190))]]
    lights = []
    for _ in range(46):
        y = rnd.uniform(WATER_Y + 20, H - 20)
        depth = (y - WATER_Y) / (H - WATER_Y)
        lights.append((rnd.uniform(0, W), y, dots[min(3, int(rnd.uniform(0, 3) * (0.5 + depth)))],
                       rnd.uniform(0, 6.28), rnd.uniform(1.5, 4.0), rnd.uniform(4, 14)))
    stars = [(rnd.uniform(20, W - 20), rnd.uniform(180, 1100), rnd.uniform(0, 6.28), rnd.uniform(1, 3))
             for _ in range(26)]
    streaks = [(rnd.uniform(0, W), rnd.uniform(WATER_Y + 30, H - 30), rnd.uniform(40, 140), rnd.uniform(0, 6.28))
               for _ in range(18)]
    return lights, stars, streaks


def draw_lights(im, t, lights, stars, streaks):
    d = ImageDraw.Draw(im)
    for x, y, ph, sp in stars:
        a = int(70 + 80 * (0.5 + 0.5 * math.sin(t * sp + ph)))
        r = 2.2
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 220, a))
    sl = Image.new("RGBA", (W, H - WATER_Y), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sl)
    for x, y, L, ph in streaks:
        a = int(30 + 60 * (0.5 + 0.5 * math.sin(t * 2.3 + ph)))
        dx = 18 * math.sin(t * 0.8 + ph)
        sd.ellipse((x + dx - L / 2, y - WATER_Y - 3, x + dx + L / 2, y - WATER_Y + 3), fill=(255, 200, 130, a))
    im.alpha_composite(sl.filter(ImageFilter.GaussianBlur(2.5)), (0, WATER_Y))
    for x, y, dot, ph, sp, drift in lights:
        tw = 0.5 + 0.5 * math.sin(t * sp + ph)
        a = 0.35 + 0.65 * tw ** 2
        xx = x + drift * math.sin(t * 0.5 + ph)
        place(im, dot, xx, y, alpha=a)


# ---------------- ป้ายมุมบน ----------------
def pill_img(text, f, bg, fg, padx=26, pady=8):
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = probe.textlength(text, font=f)
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * pady
    im = Image.new("RGBA", (int(tw + 2 * padx), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=h // 2, fill=bg)
    d.text((im.width / 2, h / 2), text, font=f, fill=fg, anchor="mm")
    return im


# ---------------- ซับ (ส่งให้ burn_subs.py) ----------------
_MEASURE = os.path.join(tempfile.gettempdir(), "_lk_measure.png")


def measure(text, size):
    tw, th = render_clean(text, os.path.join(FONTS, "Prompt-Medium.ttf"), size, _MEASURE)
    return tw - 80, th  # tw รวมขอบ 40px สองข้าง


def sub(text, start, end, size, y_top=None, y_center=None, **kw):
    tw, th = measure(text, size)
    assert tw <= TEXT_MAXW + 1, (text, size, tw)
    y = y_top if y_top is not None else int(y_center - th / 2)
    s = {"start": round(start, 3), "end": round(end, 3), "text": text, "size": size, "y": int(y)}
    s.update(kw)
    return s, y + th - 40  # ขอบล่างของตัวหนังสือจริง (ไม่รวมเงา)


def build_subs():
    subs = []
    # หน้า 1 ฮุก
    s, _ = sub("ไปลอยกระทง\nพกแค่กระทง =", 0.0, HOOK_END, 80, y_top=250, fade_in=0.08)
    subs.append(s)
    pang_c = 1265
    steps = [(0.30, 0.36, 230), (0.36, 0.42, 168), (0.42, 0.48, 196), (0.48, HOOK_END, 184)]
    for a, b, sz in steps:  # คำว่า [พัง] เด้ง (ขยาย-หด-ขยาย)
        s, _ = sub("[พัง]", a, b, sz, y_center=pang_c, rise=False, fade_in=0, fade_out=0)
        subs.append(s)
    s, bot = sub("7 ข้อ เช็กก่อนออกจากบ้าน", 0.55, HOOK_END, 48, y_top=1395)
    subs.append(s)
    assert bot <= SAFE_B, bot
    # หน้า 2–8
    for i, (_, big, big2, small, _) in enumerate(ITEMS):
        st = ITEM0 + i * ITEM_LEN
        # บรรทัดเดียวถ้าใส่ได้ (ตัวไม่เล็กกว่า 68) ไม่งั้นแบ่ง 2 บรรทัด
        txt, size = next((tx, sz) for tx, sz in [(big, 80), (big, 76), (big, 72), (big, 68), (big2, 80), (big2, 76)]
                         if tx and measure(tx, sz)[0] <= TEXT_MAXW)
        s, bot = sub(txt, st + 0.04, st + ITEM_LEN, size, y_top=990)
        subs.append(s)
        s, bot = sub(small, st + 0.35, st + ITEM_LEN, 46, y_top=bot - 6)
        subs.append(s)
        assert bot <= SAFE_B, (small, bot)
    # หน้า 9 การ์ดสรุป
    s, _ = sub("[เซฟไว้]ก่อนไป 24 พ.ย.", SUM_START, OUTRO_START, 80, y_top=230)
    subs.append(s)
    # หน้า 10 คำถาม + EP ต่อไป
    s, _ = sub("ปีนี้ลอยกับ[ใคร]?\nเมนต์เลขมาเลย", OUTRO_START, TOTAL, 84, y_top=230)
    subs.append(s)
    s, bot = sub("EP.2 อังคารหน้า: ใช้ AI วางแผนทริปหน้าหนาว\nกดติดตามไว้", OUTRO_START + 0.6, TOTAL, 40,
                 y_top=1300)
    subs.append(s)
    assert bot <= SAFE_B, bot
    return subs


# ---------------- เรนเดอร์ ----------------
def render_video(out_mp4, stills=None):
    bg = make_bg()
    lights, stars, streaks = make_lights()
    moon = make_moon()
    label = pill_img("เช็กลิสต์เที่ยว · EP.1", F("Prompt-Medium.ttf", 34), PINK_BG, PINK_FG)
    count_f = F("Prompt-SemiBold.ttf", 40)
    counters = [pill_img(f"{i + 1}/7", count_f, (255, 255, 255), INK, padx=30) for i in range(7)]
    glow_warm = soft_dot(70, (255, 190, 100))
    glow_icon = soft_dot(170, (150, 170, 255))
    row_f = F("Prompt-Medium.ttf", 46)
    mini = {}
    for key, *_ in ITEMS:
        if key == "mosquito":
            mi = canvas(200)
            place(mi, part_mosquito(200, 0.02), 100, 100)
            mini[key] = mi.resize((84, 84), Image.LANCZOS)
        else:
            mini[key] = ICONS[key](200, 5.0).resize((84, 84), Image.LANCZOS)
    lantern = icon_lantern(150)
    opt_f = F("Prompt-SemiBold.ttf", 66)
    dig_f = F("Prompt-SemiBold.ttf", 92)

    ff = None if stills else subprocess.Popen(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-an",
         "-movflags", "+faststart", out_mp4], stdin=subprocess.PIPE)

    def ripples(im, cx, cy, t, w0=170):
        d = ImageDraw.Draw(im)
        for j in range(3):
            ph = (t * 0.6 + j / 3) % 1.0
            rw, rh = w0 * (0.7 + 0.8 * ph), 26 * (0.7 + 0.8 * ph)
            d.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), outline=(255, 220, 170, int(110 * (1 - ph))), width=3)

    nframes = int(round(TOTAL * FPS))
    frames = [int(round(x * FPS)) for x in stills] if stills else range(nframes)
    for fi in frames:
        t = fi / FPS
        im = bg.copy()
        draw_lights(im, t, lights, stars, streaks)
        if t < SUM_START:
            im.alpha_composite(moon)
        im.alpha_composite(label, (60, 186))
        if t < HOOK_END:
            # ฮุก: กระทงอันเดียวลอยเหงา ๆ กลางจอ
            cx, cy = 540, 845 + 8 * math.sin(t * 3.2)
            hit = 0.30
            shake = 0
            if t > hit:
                dt = t - hit
                shake = 9 * math.sin(dt * 40) * math.exp(-dt * 4)
            ripples(im, 540, 985, t, 210)
            place(im, glow_warm, cx + 30, cy - 120, scale=1.6, alpha=0.55)
            kr = icon_krathong(460, t, mood="sad", sweat=ease((t - 0.4) / 0.5) if t > 0.4 else 0)
            place(im, kr, cx, cy, scale=0.9 + 0.1 * ease(t / 0.2), rot=3 * math.sin(t * 2.4) + shake)
        elif t < SUM_START:
            i = int((t - ITEM0) // ITEM_LEN)
            lt = t - ITEM0 - i * ITEM_LEN
            key = ITEMS[i][0]
            # ตัวนับมุมขวาบน (เด้งตอนเปลี่ยน)
            c = counters[i]
            place(im, c, SAFE_R - c.width / 2, 186 + c.height / 2, scale=back(lt / 0.3, 3.0) if lt < 0.3 else 1)
            cx, cy = ICON_C
            place(im, glow_icon, cx, cy, alpha=0.35)
            pop = back(lt / 0.32)
            bob = 6 * math.sin(lt * 4.2)
            wob = 3.5 * math.sin(lt * 5.0)
            if key == "mosquito":
                scene_mosquito(im, lt, cx, cy, ICON_S)
            elif key == "krathong":
                ripples(im, cx, cy + 150, lt, 190)
                place(im, glow_warm, cx + 30, cy - 120, scale=1.3, alpha=0.5)
                place(im, icon_krathong(ICON_S, lt, "happy"), cx, cy + bob, scale=pop, rot=wob)
            elif key == "shoes":
                place(im, icon_shoes(ICON_S, lt), cx, cy + 10, scale=pop * 1.15)
            else:
                place(im, ICONS[key](ICON_S, lt), cx, cy + bob, scale=pop, rot=wob)
            # ติ๊กถูกเด้ง
            if lt > 0.22:
                k = (lt - 0.22) / 0.3
                b = check_badge(52, ease((lt - 0.3) / 0.25))
                place(im, b, cx + 190, cy - 175, scale=back(k, 3.2))
        elif t < OUTRO_START:
            lt = t - SUM_START
            c = counters[6]
            place(im, c, SAFE_R - c.width / 2, 186 + c.height / 2)
            # การ์ดสรุป 7 ข้อ
            x0, x1, y0 = 100, SAFE_R, 440
            rh = 112
            y1 = y0 + 40 + rh * 7 + 10
            k = ease(lt / 0.2)
            card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            cd.rounded_rectangle((x0, y0 + 30 * (1 - k), x1, y1 + 30 * (1 - k)), radius=44,
                                 fill=(12, 22, 46, int(200 * k)), outline=(255, 214, 231, int(200 * k)), width=4)
            im.alpha_composite(card)
            place(im, lantern, x1 - 70, y0 + 85 + 5 * math.sin(t * 3), rot=5 * math.sin(t * 2.2), alpha=k)
            d = ImageDraw.Draw(im)
            for j, (key, *_r, label_txt) in enumerate(ITEMS):
                ya = lt - 0.05 - j * 0.045
                if ya <= 0:
                    continue
                ry = y0 + 40 + rh * j + rh / 2
                a = ease(ya / 0.15)
                xo = 30 * (1 - a)
                place(im, check_badge(24, ease((ya - 0.05) / 0.15)), x0 + 62 + xo, ry, scale=back(ya / 0.2), alpha=a)
                place(im, mini[key], x0 + 150 + xo, ry, alpha=a)
                d.text((x0 + 210 + xo, ry), label_txt, font=row_f, fill=(255, 255, 255, int(255 * a)), anchor="lm")
        else:
            lt = t - OUTRO_START
            # คำถามชวนเมนต์ 1/2/3
            for j, opt in enumerate(OPTIONS):
                ya = lt - 0.15 - j * 0.12
                if ya <= 0:
                    continue
                cy = 760 + j * 190
                hl = (int((lt - 0.6) / 0.45) % 3 == j) if lt > 0.6 else False
                pulse = 1.08 if hl else 1.0
                s = back(ya / 0.3) * pulse
                r = 72
                bimg = Image.new("RGBA", (2 * r + 24, 2 * r + 24), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bimg)
                bd.ellipse((4, 10, 2 * r + 20, 2 * r + 22), fill=(10, 16, 36, 160))
                bd.ellipse((2, 2, 2 * r + 18, 2 * r + 18), fill=(255, 250, 244))
                bd.ellipse((10, 10, 2 * r + 10, 2 * r + 10), fill=ACCENT if hl else (255, 128, 178))
                bd.text((r + 10, r + 8), str(j + 1), font=dig_f, fill="white", anchor="mm")
                place(im, bimg, 230, cy, scale=s)
                a = ease(ya / 0.2)
                tl = Image.new("RGBA", (700, 140), (0, 0, 0, 0))
                td = ImageDraw.Draw(tl)
                td.text((4, 74), opt, font=opt_f, fill=(0, 0, 0, 160), anchor="lm")
                tl = tl.filter(ImageFilter.GaussianBlur(6))
                ImageDraw.Draw(tl).text((0, 70), opt, font=opt_f, fill=(255, 255, 255), anchor="lm")
                im.alpha_composite(tl, (int(330 + 30 * (1 - a)), int(cy - 70)))
        if stills:
            im.convert("RGB").save(os.path.join(os.path.dirname(out_mp4), f"still-{t:05.2f}.png"))
            continue
        ff.stdin.write(im.convert("RGB").tobytes())
    if ff:
        ff.stdin.close()
        if ff.wait() != 0:
            raise SystemExit("ffmpeg failed")


def render_cover_photo(path):
    """ภาพพื้นสำหรับปก: กลางคืน + ผิวน้ำ + กระทงมุมล่างขวา (ที่ของน้องนางาจิในอนาคต)"""
    bg = make_bg()
    lights, stars, streaks = make_lights()
    draw_lights(bg, 1.3, lights, stars, streaks)
    place(bg, soft_dot(90, (255, 190, 100)), 790, 1250, scale=1.5, alpha=0.6)
    d = ImageDraw.Draw(bg)
    for j, ph in enumerate((0.2, 0.55, 0.9)):
        rw, rh = 200 * (0.7 + 0.8 * ph), 28 * (0.7 + 0.8 * ph)
        d.ellipse((780 - rw, 1530 - rh, 780 + rw, 1530 + rh), outline=(255, 220, 170, int(120 * (1 - ph))), width=3)
    place(bg, icon_krathong(460, 0.4, "happy"), 780, 1380, rot=-4)
    place(bg, icon_lantern(170), 190, 1290, rot=6)
    bg.convert("RGB").save(path, quality=95)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--only", choices=["video", "cover"])
    ap.add_argument("--stills", help="ดูตัวอย่างเฟรม (ไม่มีซับ) เช่น 0.8,2.5 — ไม่ทำวิดีโอ")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    if a.stills:
        render_video(os.path.join(a.out_dir, "x.mp4"), [float(v) for v in a.stills.split(",")])
        return
    if a.only != "cover":
        subs = build_subs()
        sp = os.path.join(a.out_dir, "subs.json")
        json.dump(subs, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(subs, open(os.path.join(HERE, "subs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        base = os.path.join(a.out_dir, "base.mp4")
        render_video(base)
        subprocess.run([sys.executable, os.path.join(EDITOR, "burn_subs.py"), "--video", base, "--subs", sp,
                        "--out", os.path.join(a.out_dir, "loykrathong-ep1-preview.mp4"), "--mute"], check=True)
    if a.only != "video":
        photo = os.path.join(a.out_dir, "cover-bg.png")
        render_cover_photo(photo)
        subprocess.run([sys.executable, os.path.join(EDITOR, "make_cover.py"), "--photo", photo,
                        "--out", os.path.join(a.out_dir, "cover.png"),
                        "--kicker", "เช็กลิสต์เที่ยว · EP.1",
                        "--title", "Loy Krathong\\nChecklist",
                        "--pill", "ไปลอยกระทงคนเยอะ เช็กอะไรบ้าง?"], check=True)


if __name__ == "__main__":
    main()
