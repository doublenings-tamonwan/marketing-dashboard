"""Scrapbook (style D) graphics overlay + end card + cover for Izakaya NANA.
usage: python3 scrap.py overlay IN.mp4 OUT.mp4   |   python3 scrap.py cover OUT.png   |  python3 scrap.py still T OUT.png
"""
import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

U = "/root/.claude/uploads/4c923d2c-8f5d-5971-8899-b8d14570e947"
F = "/home/user/marketing-dashboard/office/assets/fonts/"
ST = "/home/user/marketing-dashboard/office/assets/stickers/owner/"
W, H, FPS = 1080, 1920, 30
YEL, BLU, PNK, DARK = "#F7E36B", "#8FD3EA", "#E0569A", (58, 32, 48, 255)
MAROON = (122, 14, 59, 110)


def font(n, s):
    return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)


def trim(im):
    return im.crop(im.getbbox())


def outlined(text, f, fill, stroke=14, scol="white", angle=0, shadow=True):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.textbbox((0, 0), text, font=f, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 60
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = (30 - bb[0], 30 - bb[1])
    if shadow:
        d.text((o[0] + 8, o[1] + 10), text, font=f, fill=MAROON, stroke_width=stroke, stroke_fill=MAROON)
    d.text(o, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=scol)
    return trim(im.rotate(angle, expand=True, resample=Image.BICUBIC))


def mint_label(text, size=88, angle=5):
    f = font("Kanit-Bold.ttf", size)
    tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f)
    w, h = int(tw + 90), int(size * 1.75)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, w + 10, h + 10], fill="#C9F0EA", outline="white", width=8)
    d.text(((w + 20) / 2, (h + 20) / 2 + 4), text, font=f, fill=PNK, anchor="mm", stroke_width=6, stroke_fill="white")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 70), mask=im.split()[3])
    out = Image.new("RGBA", (im.width + 30, im.height + 30), (0, 0, 0, 0))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (14, 16))
    out.alpha_composite(im, (0, 0))
    return trim(out.rotate(angle, expand=True, resample=Image.BICUBIC))


def bubble(text, size=56, angle=-6, tail="left", fill="#FFE1EE"):
    f = font("Mali-Bold.ttf", size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.textbbox((0, 0), text, font=f, anchor="mm")
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    ew, eh = int(tw * 1.32 + 60), int(th * 2.2 + 40)
    im = Image.new("RGBA", (ew + 40, eh + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tx = 0.22 * ew if tail == "left" else 0.78 * ew
    d.polygon([(tx, eh - 10), (tx - 40 if tail == "left" else tx + 40, eh + 70), (tx + 50 if tail == "left" else tx - 50, eh - 20)],
              fill=fill, outline=DARK, width=6)
    d.ellipse([10, 10, ew, eh], fill=fill, outline=DARK, width=6)
    d.polygon([(tx + 4, eh - 22), (tx + 40 if tail == "left" else tx - 40, eh - 26), (tx + 10 if tail == "left" else tx - 10, eh - 2)], fill=fill)
    d.text(((ew + 10) / 2, (eh + 10) / 2 + 2), text, font=f, fill=DARK, anchor="mm")
    return trim(im.rotate(angle, expand=True, resample=Image.BICUBIC))


def note(lines, size=42, angle=0, head=None):
    """white rounded box, dark outline, Mali. lines: list[str]"""
    fb, fm = font("Mali-Bold.ttf", size), font("Mali-Medium.ttf", int(size * 0.92))
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    rows = ([(head, fb)] if head else []) + [(l, fm if head else fb) for l in lines]
    lh = int(size * 1.45)
    tw = max(d0.textlength(t, font=f) for t, f in rows)
    w, h = int(tw + 70), int(lh * len(rows) + 34)
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([12, 16, w + 12, h + 16], radius=min(40, h // 2), fill=(0, 0, 0, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, w + 8, h + 8], radius=min(40, h // 2), fill="white", outline=DARK, width=4)
    for k, (t, f) in enumerate(rows):
        y = 8 + 17 + lh * k + lh / 2
        if head and k == 0:
            d.text(((w + 16) / 2, y), t, font=f, fill=PNK, anchor="mm")
        else:
            d.text((8 + 35, y), t, font=f, fill=DARK, anchor="lm")
    return trim(im.rotate(angle, expand=True, resample=Image.BICUBIC))


def star5(r, color, angle=0):
    s = r * 2 + 20
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s * 2
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5 + math.radians(angle)
        rr = r * 4 if i % 2 == 0 else r * 4 * 0.45
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=color, outline="white", width=12)
    return im.resize((s, s), Image.LANCZOS)


def asterisk(r, color):
    s = r * 2 + 20
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s * 2
    for k in range(4):
        a = k * math.pi / 4
        p = [(c - 4 * r * math.cos(a), c - 4 * r * math.sin(a)), (c + 4 * r * math.cos(a), c + 4 * r * math.sin(a))]
        d.line(p, fill="white", width=int(r * 2.1))
    for k in range(4):
        a = k * math.pi / 4
        p = [(c - 4 * r * math.cos(a), c - 4 * r * math.sin(a)), (c + 4 * r * math.cos(a), c + 4 * r * math.sin(a))]
        d.line(p, fill=color, width=int(r * 1.3))
    return im.resize((s, s), Image.LANCZOS)


def sticker(name, w, angle=0):
    im = Image.open(ST + name).convert("RGBA")
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    return trim(im.rotate(angle, expand=True, resample=Image.BICUBIC))


def stripes(seed=3):
    bg = Image.new("RGBA", (W, H), "#FFF4F8")
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 90):
        d.rectangle([x, 0, x + 44, H], fill="#F9D3E2")
    rnd = random.Random(seed)
    for _ in range(26):
        st = star5(rnd.randint(12, 24), rnd.choice(["#E58BB0", "#7CCBE0", "#F7B7CF"]), rnd.uniform(-20, 20))
        bg.alpha_composite(st, (rnd.randint(0, W - 40), rnd.randint(0, H - 40)))
    return bg


def polaroid(photo, angle):
    fr = Image.new("RGBA", (photo.width + 44, photo.height + 120), "white")
    fr.paste(photo, (22, 22))
    fr = fr.rotate(angle, expand=True, resample=Image.BICUBIC)
    out = Image.new("RGBA", (fr.width + 40, fr.height + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 80), mask=fr.split()[3])
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (16, 22))
    out.alpha_composite(fr, (0, 0))
    return out


def grade_photo(im):
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    a = np.asarray(im).astype(np.float32)
    a = 255 * ((a / 255) ** 0.92)
    a[..., 0] *= 1.02
    a[..., 2] *= 0.97
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(2, 60, 3))


def photo(name, box, size):
    im = ImageOps.exif_transpose(Image.open(f"{U}/{name}-image.jpg")).convert("RGB")
    return grade_photo(im.resize(size, Image.LANCZOS, box=box)).convert("RGBA")


# ---------------- timeline ----------------
class El:
    def __init__(self, img, cx, cy, t0, t1, pop=True):
        self.img, self.cx, self.cy, self.t0, self.t1, self.pop = img, cx, cy, t0, t1, pop
        self.cache = {}

    def scale(self, t):
        if not self.pop:
            return 1.0
        u = t - self.t0
        if u >= 0.2:
            return 1.0
        if u < 0.13:
            return 1.1 * (u / 0.13)
        return 1.1 - 0.1 * (u - 0.13) / 0.07

    def draw(self, frame, t):
        if not (self.t0 <= t < self.t1):
            return
        s = round(self.scale(t), 3)
        if s <= 0.02:
            return
        im = self.img
        if s != 1.0:
            if s not in self.cache:
                self.cache[s] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
            im = self.cache[s]
        frame.alpha_composite(im, (int(self.cx - im.width / 2), int(self.cy - im.height / 2)))


def build_els():
    E = []
    ds = font("DancingScript-Bold.ttf", 172)
    # hook: label from frame 0, title pops with yukke at 0.6
    E.append(El(mint_label("พามารีวิว", 84), 300, 615, 0.0, 2.4))
    E.append(El(outlined("Izakaya", ds, YEL, angle=6), 450, 232, 0.6, 2.4))
    E.append(El(outlined("NANA", ds, BLU, angle=6), 715, 385, 0.65, 2.4))
    E.append(El(asterisk(30, YEL), 975, 205, 0.7, 2.4))
    E.append(El(star5(30, BLU, 10), 95, 420, 0.7, 2.4))
    E.append(El(bubble("น่ากินทุกจาน!", 54, -6, "left"), 812, 590, 0.8, 2.4))
    E.append(El(sticker("reaction-wow.png", 300, -6), 185, 1590, 1.05, 2.4))
    E.append(El(note(["* ต้องสั่ง!"], 44, 4), 770, 1650, 1.5, 2.4))
    # menu notes
    E.append(El(note(["* แซลมอนสดมาก"], 42, -3), 760, 575, 2.7, 3.9))
    E.append(El(star5(22, YEL, 5), 1000, 530, 2.75, 3.9))
    E.append(El(note(["* ผักเยอะมาก"], 42, 3), 300, 585, 4.2, 5.4))
    E.append(El(asterisk(20, BLU), 520, 540, 4.25, 5.4))
    E.append(El(sticker("reaction-yes.png", 280, 5), 175, 1610, 4.4, 5.4))
    E.append(El(note(["* งาเต็มไม้"], 42, -3), 235, 575, 5.7, 6.9))
    E.append(El(star5(22, "#F7B7CF", 0), 440, 520, 5.75, 6.9))
    E.append(El(asterisk(18, YEL), 960, 560, 7.1, 8.4))
    return E


def card_layers():
    """end card 11.4-14.9 : (static bg, popping elements)"""
    T = 11.4
    bg = stripes(5)
    E = []
    front = photo("7ce4021c", (526, 760, 1576, 2072), (560, 700))
    E.append(El(polaroid(front, -5), 370, 1090, T + 0.03, 99))
    ds = font("DancingScript-Bold.ttf", 175)
    E.append(El(outlined("Izakaya", ds, YEL, angle=6), 430, 235, T + 0.05, 99))
    E.append(El(outlined("NANA", ds, BLU, angle=6), 690, 395, T + 0.1, 99))
    E.append(El(outlined("อิซากะยะนานะ", font("Kanit-Bold.ttf", 66), "#FF7DB5", stroke=8, angle=0, shadow=True), 540, 548, T + 0.2, 99))
    pf = font("Kanit-Medium.ttf", 48)
    txt = "ปากน้ำ · สมุทรปราการ"
    tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(txt, font=pf)
    pill = Image.new("RGBA", (int(tw + 100), 96), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([4, 4, pill.width - 4, 92], radius=44, fill="white", outline=DARK, width=4)
    pd.text((pill.width / 2, 50), txt, font=pf, fill=DARK, anchor="mm")
    E.append(El(pill, 540, 648, T + 0.25, 99))
    E.append(El(note(["- ยุคเกะไข่แดง", "- ซาชิมิรวม", "- ยำปลาดิบ"], 44, 4, head="เมนูที่ต้องสั่ง"), 775, 1130, T + 0.4, 99))
    E.append(El(asterisk(30, YEL), 975, 790, T + 0.45, 99))
    E.append(El(star5(26, BLU, 12), 90, 1440, T + 0.45, 99))
    E.append(El(sticker("reaction-save.png", 300, -6), 200, 1600, T + 0.55, 99))
    E.append(El(bubble("เซฟไว้ไปกินกับเพื่อน", 50, -4, "left", "#FFFFFF"), 660, 1560, T + 0.7, 99))
    return T, bg, E


def overlay(inp, out):
    E = build_els()
    T, cbg, CE = card_layers()
    dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", "-an", out], stdin=subprocess.PIPE)
    n = 0
    fs = W * H * 3
    while True:
        b = dec.stdout.read(fs)
        if len(b) < fs:
            break
        t = n / FPS
        if t >= T:
            fr = cbg.copy()
            for e in CE:
                e.draw(fr, t)
        else:
            fr = Image.frombuffer("RGB", (W, H), b).convert("RGBA")
            for e in E:
                e.draw(fr, t)
        enc.stdin.write(fr.convert("RGB").tobytes())
        n += 1
    enc.stdin.close()
    assert enc.wait() == 0 and dec.wait() == 0
    print("frames", n)


def cover(out):
    bg = stripes(9)
    yk = photo("7e14678d", (298, 521, 1138, 1571), (680, 850))
    bg.alpha_composite(pol := polaroid(yk, -4), (540 - pol.width // 2, 1170 - pol.height // 2))
    ds = font("DancingScript-Bold.ttf", 235)
    for img, cx, cy in [(outlined("Izakaya", ds, YEL, stroke=16, angle=6), 450, 400),
                        (outlined("NANA", ds, BLU, stroke=16, angle=6), 700, 590),
                        (mint_label("พามารีวิว", 80, 5), 270, 790),
                        (bubble("ปากน้ำ", 58, -8, "left"), 870, 790),
                        (asterisk(34, YEL), 985, 330),
                        (asterisk(26, BLU), 95, 560),
                        (star5(28, "#F7B7CF", 0), 990, 1530)]:
        bg.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))
    bg.convert("RGB").save(out)
    bg.convert("RGB").crop((0, 240, 1080, 1680)).save(out.replace(".png", "-3x4-check.jpg"), quality=90)


if __name__ == "__main__":
    if sys.argv[1] == "overlay":
        overlay(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "cover":
        cover(sys.argv[2])
    elif sys.argv[1] == "still":  # preview card at time t
        T, bg, CE = card_layers()
        fr = bg.copy()
        for e in CE:
            e.draw(fr, float(sys.argv[2]))
        fr.convert("RGB").save(sys.argv[3])
