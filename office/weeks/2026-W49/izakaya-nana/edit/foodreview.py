"""Food-review (style A) graphics overlay for Izakaya NANA v2.
usage: python3 foodreview.py IN.mp4 OUT.mp4
No colour filters: only a soft dark gradient at the top behind text (legibility), card bg = blurred/dimmed photo.
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

U = "/root/.claude/uploads/4c923d2c-8f5d-5971-8899-b8d14570e947/"
F = "/home/user/marketing-dashboard/office/assets/fonts/"
W, H, FPS = 1080, 1920, 30
CREAM, PINK, BLUE, INK = "#F6E3A8", "#FF8FB8", "#8FD3EA", "#2A1A14"


def font(n, s):
    return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def txt(c, xy, t, f, fill, anchor="mm", shadow=True):
    if shadow:
        l = layer()
        ImageDraw.Draw(l).text((xy[0] + 4, xy[1] + 6), t, font=f, fill=(0, 0, 0, 150), anchor=anchor)
        c.alpha_composite(l.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(c).text(xy, t, font=f, fill=fill, anchor=anchor)


def ast(c, cx, cy, r, col):
    d = ImageDraw.Draw(c)
    for k in range(3):
        a = k * math.pi / 3
        d.line([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=col, width=14)


def pill(c, cx, y, t, f, bg, fg, padx=45, h=90, anchor_left=False):
    d = ImageDraw.Draw(c)
    bw = d.textlength(t, font=f) + 2 * padx
    x0 = cx if anchor_left else cx - bw / 2
    sh = layer()
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 3, y + 6, x0 + bw + 3, y + h + 6], radius=h // 2, fill=(0, 0, 0, 90))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d.rounded_rectangle([x0, y, x0 + bw, y + h], radius=h // 2, fill=bg)
    d.text((x0 + bw / 2, y + h / 2 + 2), t, font=f, fill=fg, anchor="mm")


def gradient(alpha, until):
    g = Image.new("L", (1, H))
    for i in range(H):
        g.putpixel((0, i), int(alpha * max(0, 1 - i / until) ** 1.3))
    lay = Image.new("RGBA", (W, H), (20, 12, 10, 0))
    lay.putalpha(g.resize((W, H)))
    return lay


class El:
    """full-frame RGBA layer, fades in + rises 24px over 0.25s"""
    def __init__(self, img, t0, t1, rise=24):
        self.img, self.t0, self.t1, self.rise = img, t0, t1, rise
        self.arr = np.asarray(img).astype(np.float32)

    def draw(self, fr, t):
        if not (self.t0 <= t < self.t1):
            return
        k = min(1.0, (t - self.t0) / 0.25)
        k = k * k * (3 - 2 * k)
        if k >= 1:
            fr.alpha_composite(self.img)
            return
        a = self.arr.copy()
        a[..., 3] *= k
        im = Image.fromarray(a.astype(np.uint8))
        fr.alpha_composite(im, (0, int(self.rise * (1 - k))))


def hook_layers():
    L = []
    k = layer()
    txt(k, (W // 2, 225), "พามารีวิว · ร้านญี่ปุ่นสไตล์อิซากายะ", font("Kanit-Medium.ttf", 44), "#FFF4E0")
    L.append((k, -0.12))
    t = layer()
    txt(t, (W // 2, 375), "Izakaya", font("Fraunces-SemiBoldItalic.ttf", 170), CREAM)
    L.append((t, -0.06))
    n = layer()
    txt(n, (W // 2, 545), "NANA", font("Fraunces-Bold.ttf", 180), CREAM)
    ast(n, 900, 300, 30, PINK)
    ast(n, 205, 580, 24, BLUE)
    L.append((n, 0.0))
    p = layer()
    pill(p, W // 2, 1370, "ปากน้ำ · สมุทรปราการ", font("Kanit-SemiBold.ttf", 46), "white", INK, h=86)
    L.append((p, 0.12))
    q = layer()
    pill(q, W // 2, 1478, "4 เมนูต้องสั่ง!", font("Kanit-SemiBold.ttf", 44), PINK, "white", padx=35, h=76)
    L.append((q, 0.2))
    return L


def menu_layer(num, en, th):
    c = layer()
    txt(c, (70, 300), f"{num} {en}", font("Fraunces-SemiBoldItalic.ttf", 104), CREAM, anchor="ls")
    pill(c, 74, 335, th, font("Kanit-Medium.ttf", 46), "white", INK, padx=36, h=82, anchor_left=True)
    return c


def card_bg():
    im = ImageOps.exif_transpose(Image.open(U + "7fa7d651-image.jpg")).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = int((im.width - W) * 0.5); y = int((im.height - H) * 0.35)
    im = im.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(18))
    return ImageEnhance.Brightness(im).enhance(0.45).convert("RGBA")


def card_layers():
    L = []
    t = layer()
    txt(t, (W // 2, 390), "Izakaya", font("Fraunces-SemiBoldItalic.ttf", 170), CREAM)
    txt(t, (W // 2, 560), "NANA", font("Fraunces-Bold.ttf", 180), CREAM)
    ast(t, 900, 315, 30, PINK)
    ast(t, 205, 595, 24, BLUE)
    L.append((t, 0.0))
    p = layer()
    pill(p, W // 2, 680, "ปากน้ำ · สมุทรปราการ", font("Kanit-SemiBold.ttf", 46), "white", INK, h=86)
    L.append((p, 0.12))
    m = layer()
    txt(m, (W // 2, 840), "4 เมนูต้องสั่ง", font("Kanit-SemiBold.ttf", 58), PINK)
    fi = font("Kanit-Regular.ttf", 50)
    items = ["ยุคเกะไข่แดง", "ซาชิมิรวม", "ยำปลาไทยซีฟู้ดวาซาบิ", "วากิวย่าง"]
    left = W // 2 - 260
    for k, it in enumerate(items):
        y = 930 + k * 66
        txt(m, (left, y), f"0{k + 1}", font("Fraunces-SemiBoldItalic.ttf", 50), CREAM, anchor="lm")
        txt(m, (left + 80, y), it, fi, "white", anchor="lm")
    L.append((m, 0.28))
    return L


def main(inp, out):
    T_CARD = 11.9
    top_grad = gradient(150, 760)
    menu_grad = gradient(120, 620)
    els = [El(img, t0, 2.3) for img, t0 in hook_layers()]
    menus = [("01", "Yukhoe", "ยุคเกะไข่แดง", 2.3, 4.3), ("02", "Sashimi", "ซาชิมิรวม", 5.5, 7.0),
             ("03", "Seafood Salad", "ยำปลาไทยซีฟู้ดวาซาบิ", 7.0, 8.5), ("04", "Wagyu", "วากิวย่าง", 8.5, 10.0)]
    for num, en, th, a, b in menus:
        els.append(El(menu_layer(num, en, th), a, b))
    cbg = card_bg()
    cels = [El(img, T_CARD + t0, 99) for img, t0 in card_layers()]
    dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", "-an", out], stdin=subprocess.PIPE)
    n, fs = 0, W * H * 3
    while True:
        b = dec.stdout.read(fs)
        if len(b) < fs:
            break
        t = n / FPS
        if t >= T_CARD:
            fr = cbg.copy()
            for e in cels:
                e.draw(fr, t)
        else:
            fr = Image.frombuffer("RGB", (W, H), b).convert("RGBA")
            if t < 2.3:
                fr.alpha_composite(top_grad)
            elif any(a <= t < bb for *_, a, bb in menus):
                fr.alpha_composite(menu_grad)
            for e in els:
                e.draw(fr, t)
        enc.stdin.write(fr.convert("RGB").tobytes())
        n += 1
    enc.stdin.close()
    assert enc.wait() == 0 and dec.wait() == 0
    print("frames", n)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
