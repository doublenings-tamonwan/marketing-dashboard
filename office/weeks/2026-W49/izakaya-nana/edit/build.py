"""Build graded shots for Izakaya NANA clip (v2: rapid open + close-up photos).
usage: python3 build.py OUTDIR [--nograde]
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

U = "/root/.claude/uploads/4c923d2c-8f5d-5971-8899-b8d14570e947"
FONTS = "/home/user/marketing-dashboard/office/assets/fonts"
STICKER = "/home/user/marketing-dashboard/office/assets/stickers/owner/reaction-save.png"
W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1]
NOGRADE = "--nograde" in sys.argv
ONLY = [a.split("=")[1] for a in sys.argv if a.startswith("--only=")]
os.makedirs(OUT, exist_ok=True)

FOOD = ("curves=all='0/0.02 0.25/0.29 0.7/0.73 1/1',eq=contrast=1.05:saturation=1.07,"
        "vibrance=intensity=0.22,colorbalance=rs=0.02:bs=-0.025:rm=0.015:bm=-0.02,"
        "unsharp=5:5:0.75:5:5:0")
PEOPLE = ("curves=all='0/0.02 0.25/0.29 0.7/0.72 1/1',eq=contrast=1.03:saturation=1.03,"
          "vibrance=intensity=0.08,unsharp=5:5:0.45:5:5:0")


def photo(name):
    return Image.open(f"{U}/{name}-image.jpg").convert("RGB")


def smooth(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def view(src, box, z, focus):
    """box = (x0,y0,w) 9:16 base crop in src px; zoom z toward focus (fx,fy)."""
    x0, y0, w = box
    h = w * 16 / 9
    cx, cy = x0 + w / 2, y0 + h / 2
    fx, fy = focus
    cx, cy = fx + (cx - fx) / z, fy + (cy - fy) / z
    w2, h2 = w / z, h / z
    b = (cx - w2 / 2, cy - h2 / 2, cx + w2 / 2, cy + h2 / 2)
    return src.resize((W, H), Image.BICUBIC, box=b)


def blur_ellipses(im, ells, r=28):
    """ells: list of (cx,cy,rx,ry) in im px — heavy blur inside soft ellipse."""
    if not ells:
        return im
    bl = im.filter(ImageFilter.GaussianBlur(r))
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    for cx, cy, rx, ry in ells:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(8))
    return Image.composite(bl, im, m)


def lerp_keys(keys, t):
    """keys: [(t, (a,b,...)), ...] piecewise linear."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            return tuple(a + (b - a) * k for a, b in zip(v0, v1))
    return keys[-1][1]


def video_frames(name, start, n):
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{start}", "-i", f"{U}/{name}.mov",
                        "-frames:v", str(n), "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    a = np.frombuffer(p.stdout, np.uint8).reshape(-1, 1920, 1080, 3)
    assert len(a) >= n, (name, len(a))
    return [Image.fromarray(f) for f in a[:n]]


def encode(path, frames, grade):
    vf = (grade + ",") if (grade and not NOGRADE) else ""
    vf += "format=yuv420p,setsar=1"
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf", vf, "-c:v", "libx264",
                          "-preset", "medium", "-crf", "16", "-r", str(FPS), "-an", path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close()
    assert p.wait() == 0


# ---------------- end card ----------------
def font(n, s):
    return ImageFont.truetype(f"{FONTS}/{n}", s, layout_engine=ImageFont.Layout.RAQM)


def asterisk(size, color):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    for k in range(4):
        a = math.radians(k * 45)
        dx, dy = math.cos(a) * s * 0.46, math.sin(a) * s * 0.46
        d.line((c - dx, c - dy, c + dx, c + dy), fill=color, width=int(s * 0.16))
    d.ellipse((c - s * 0.12, c - s * 0.12, c + s * 0.12, c + s * 0.12), fill=color)
    return im.resize((size, size), Image.LANCZOS)


def shadow_text(layer, xy, text, f, fill, anchor="mm", blur=14, alpha=150):
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 5), text, font=f, fill=(0, 0, 0, alpha), anchor=anchor)
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(layer).text(xy, text, font=f, fill=fill, anchor=anchor)


CREAM = (252, 228, 150, 255)
PINK = (255, 130, 190, 255)


def card_layers():
    """returns list of (layer RGBA full-frame, appear_time) for staggered entry."""
    layers = []
    cx = W // 2
    # title
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f1 = font("Fraunces-Bold.ttf", 190)
    shadow_text(t, (cx, 400), "Izakaya", f1, CREAM, blur=18, alpha=170)
    shadow_text(t, (cx + 40, 580), "NANA", f1, CREAM, blur=18, alpha=170)
    bb1 = ImageDraw.Draw(t).textbbox((cx, 400), "Izakaya", font=f1, anchor="mm")
    bb2 = ImageDraw.Draw(t).textbbox((cx + 40, 580), "NANA", font=f1, anchor="mm")
    a1 = asterisk(92, PINK)
    t.alpha_composite(a1, (int(bb1[2]) + 8, int(bb1[1]) - 30))
    a2 = asterisk(78, (140, 215, 255, 255))
    t.alpha_composite(a2, (int(bb2[0]) - 100, int((bb2[1] + bb2[3]) / 2) - 39))
    shadow_text(t, (cx, 712), "อิซากะยะนานะ", font("Kanit-Medium.ttf", 54), (255, 255, 255, 255), alpha=200)
    layers.append((t, 0.0))
    # pill (district)
    p = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    pf = font("Kanit-Medium.ttf", 54)
    txt = "ปากน้ำ · สมุทรปราการ"
    tw = d.textlength(txt, font=pf)
    y0, ph = 775, 90
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((cx - tw / 2 - 44, y0 + 6, cx + tw / 2 + 44, y0 + ph + 6), radius=ph // 2, fill=(0, 0, 0, 120))
    p.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((cx - tw / 2 - 44, y0, cx + tw / 2 + 44, y0 + ph), radius=ph // 2, fill=(255, 255, 255, 255))
    d.text((cx, y0 + ph / 2 + 2), txt, font=pf, fill=(20, 20, 20, 255), anchor="mm")
    layers.append((p, 0.15))
    # menu
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hf, itf = font("Kanit-SemiBold.ttf", 60), font("Kanit-Regular.ttf", 54)
    shadow_text(m, (cx, 945), "เมนูที่ต้องสั่ง", hf, (255, 255, 255, 255), alpha=200)
    items = ["ยุคเกะไข่แดง", "ซาชิมิรวม", "ยำปลาดิบ"]
    left = cx - max(ImageDraw.Draw(m).textlength(i, font=itf) for i in items) / 2 - 20
    for k, it in enumerate(items):
        y = 1025 + k * 66
        dd = ImageDraw.Draw(m)
        dd.ellipse((left - 14, y - 7, left, y + 7), fill=PINK)
        shadow_text(m, (left + 22, y), it, itf, (255, 255, 255, 255), anchor="lm", alpha=200)
    layers.append((m, 0.3))
    return layers


def card_shot(n):
    src = photo("7ce4021c")  # 1932x2576 storefront; crop below MONA CLINIC sign
    box = (526, 709, 1050)
    bg_cache = None
    layers = card_layers()
    st = Image.open(STICKER).convert("RGBA")
    sw = 270
    st = st.resize((sw, int(st.height * sw / st.width)), Image.LANCZOS)
    frames = []
    for i in range(n):
        t = i / FPS
        z = 1.0 + 0.04 * t / (n / FPS)
        bg = view(src, box, z, (1051, 1642))
        bg = bg.filter(ImageFilter.GaussianBlur(7))
        bg = ImageEnhance.Brightness(bg).enhance(0.58).convert("RGBA")
        for lay, t0 in layers:
            k = smooth((t - t0) / 0.25)
            if k <= 0:
                continue
            l2 = lay if k >= 1 else Image.fromarray((np.asarray(lay) * np.array([1, 1, 1, k])).astype(np.uint8))
            dy = int((1 - k) * 40)
            bg.alpha_composite(l2, (0, dy) if dy else (0, 0))
        ts = t - 0.3  # sticker pop at card+0.3s
        if ts > 0:
            s = 1.1 * smooth(ts / 0.12) if ts < 0.12 else 1.1 - 0.1 * smooth((ts - 0.12) / 0.08)
            s = max(s, 0.01)
            sp = st.resize((max(1, int(st.width * s)), max(1, int(st.height * s))), Image.LANCZOS).rotate(-8, expand=True, resample=Image.BICUBIC)
            cxs, cys = 870, 1000
            bg.alpha_composite(sp, (cxs - sp.width // 2, cys - sp.height // 2))
        frames.append(bg)
    return frames


# ---------------- shots ----------------
def still_shot(name, n, box, focus, z0=1.0, slow=0.0, punch=None):
    src = photo(name)
    frames = []
    for i in range(n):
        t = i / FPS
        z = z0 + slow * t
        if punch:
            tp, amt = punch
            z += amt * smooth((t - tp) / 0.15)
        frames.append(view(src, box, z, focus))
    return frames


def shots():
    S = []
    # rapid open: 5 x 5 frames
    S.append(("m1", lambda: still_shot("c7db42e2", 5, (700, 750, 620), (1008, 1336), 1.0, 0.3), FOOD))
    S.append(("m2", lambda: still_shot("854b721a", 4, (600, 560, 620), (907, 1058), 1.0, 0.3), FOOD))
    S.append(("m3", lambda: still_shot("ceae1e7c", 5, (184, 280, 976), (689, 1176), 1.0, 0.0), FOOD))

    def m4():
        f = video_frames("0718ff68-IMG_7392", 0.3, 1)[0]
        return [view(f, (130, 0, 760), 1.0 + 0.06 * i / 5, (510, 600)) for i in range(4)]
    S.append(("m4", m4, PEOPLE))
    # yukke hero: 47 frames, punch at 0.3s, slow push after
    S.append(("yukke", lambda: still_shot("7e14678d", 54, (193, 148, 1050), (718, 1046), 1.0, 0.07, (0.3, 0.2)), FOOD))
    # sashimi close: slow push to salmon
    S.append(("sashimi", lambda: still_shot("c7db42e2", 45, (164, 0, 1134), (1008, 1300), 1.0, 0.07), FOOD))
    # yum close: slow drift (pan)
    def yum():
        src = photo("854b721a")
        return [view(src, (150 + 3 * i, 0, 1134), 1.04, (756 + 3 * i, 1058)) for i in range(45)]
    S.append(("yum", yum, FOOD))
    # skewers: meat only, punch 15% at 0.5s
    S.append(("skewer", lambda: still_shot("ceae1e7c", 45, (184, 280, 976), (689, 1176), 1.0, 0.0), FOOD))

    # chef counter 7383 0.0-1.5, crop away bottles, blur chef faces
    def chef():
        fr = video_frames("e2074a94-IMG_7383", 0.0, 45)
        out = []
        for i, f in enumerate(fr):
            t = i / FPS
            c1 = lerp_keys([(0, (648, 985)), (0.75, (593, 962)), (1.45, (435, 985))], t)
            c2 = lerp_keys([(0, (1035, 1022)), (0.75, (983, 1000)), (1.45, (788, 1007))], t)
            f = blur_ellipses(f, [(c1[0], c1[1], 62, 74), (c2[0], c2[1], 62, 74)])
            x0 = lerp_keys([(0, (390,)), (0.75, (320,)), (1.45, (160,))], t)[0]
            out.append(view(f, (x0, 390, 520), 1.0, (0, 0)))
        return out
    S.append(("chef", chef, PEOPLE))

    def lantern():
        fr = video_frames("0718ff68-IMG_7392", 0.0, 45)
        return [view(f, (40, 0, 1000), 1.0 + 0.04 * i / 45, (540, 700)) for i, f in enumerate(fr)]
    S.append(("lantern", lantern, PEOPLE))

    def friend():
        fr = video_frames("75cb1a17-IMG_7381", 6.0, 45)
        out = []
        for i, f in enumerate(fr):
            t = i / FPS
            c = lerp_keys([(0, (288, 540)), (0.5, (242, 712)), (1.0, (194, 745)), (1.6, (162, 712))], t)
            f = blur_ellipses(f, [(c[0], c[1] - 10, 105, 125)])
            out.append(view(f, (27, 0, 1026), 1.0, (540, 960)))
        return out
    S.append(("friend", friend, PEOPLE))
    S.append(("card", lambda: card_shot(105), PEOPLE))
    return S


if __name__ == "__main__":
    names = []
    for k, (name, fn, grade) in enumerate(shots()):
        path = f"{OUT}/{k:02d}-{name}.mp4"
        names.append(path)
        if ONLY and name not in ONLY:
            continue
        encode(path, fn(), grade)
        print("ok", path, flush=True)
    with open(f"{OUT}/list.txt", "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in names)
