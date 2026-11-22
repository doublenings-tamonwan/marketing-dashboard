"""คลิปลอยกระทง (เวอร์ชันการ์ดกราฟิก ไม่ต้องถ่าย) — พื้นคืนเดือนเพ็ญ + แสงโบเก้ + การ์ดเช็กลิสต์เด้ง
python3 make_loykrathong.py <out.mp4>
"""
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FD = os.path.join(REPO, "office", "assets", "fonts")
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
YEL, INK, WHITE, CREAM = (255, 225, 77), (58, 42, 0), (255, 255, 255), (255, 246, 226)
F = lambda n, s: ImageFont.truetype(os.path.join(FD, n), s)

_ec = {}
def emoji(ch, size):
    if (ch, size) not in _ec:
        im = Image.new("RGBA", (180, 180)); ImageDraw.Draw(im).text((90, 90), ch, font=ImageFont.truetype(EMO, 109), embedded_color=True, anchor="mm")
        im = im.crop(im.getbbox()); s = size / max(im.size)
        _ec[(ch, size)] = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return _ec[(ch, size)]

# ---------- พื้นหลังคืนเดือนเพ็ญ ----------
def make_bg():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(18 + 20 * t), int(22 + 18 * t), int(58 + 10 * t)))
    glow = Image.new("RGBA", (W, H)); g = ImageDraw.Draw(glow)
    g.ellipse((640, 120, 1000, 480), fill=(255, 236, 170, 70)); glow = glow.filter(ImageFilter.GaussianBlur(60))
    bg = bg.convert("RGBA"); bg.alpha_composite(glow)
    ImageDraw.Draw(bg).ellipse((730, 210, 910, 390), fill=(255, 241, 196, 255))
    water = Image.new("RGBA", (W, H)); w = ImageDraw.Draw(water)
    for y in range(1500, H, 18):
        w.line([(0, y), (W, y)], fill=(255, 210, 120, 10 + (y - 1500) // 30), width=3)
    bg.alpha_composite(water)
    return bg
BG = make_bg()
random.seed(4)
BOKEH = [(random.uniform(0, W), random.uniform(500, H), random.uniform(14, 46), random.uniform(0.2, 0.7), random.uniform(0, 6))
         for _ in range(28)]
def bokeh_layer(t):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for x, y, r, sp, ph in BOKEH:
        yy = (y - t * 40 * sp) % (H - 400) + 400
        a = int(60 + 50 * math.sin(t * 2 + ph))
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 196, 92, a))
    return lay.filter(ImageFilter.GaussianBlur(6))

# ---------- องค์ประกอบ ----------
def text_img(text, font, fill=WHITE, stroke=0, sfill=(20, 20, 50), spacing=10):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = (int(v) for v in d.multiline_textbbox((0, 0), text, font=font, stroke_width=stroke, align="center", spacing=spacing))
    im = Image.new("RGBA", (r - l + 40, b - t + 40))
    sh = Image.new("RGBA", im.size); ImageDraw.Draw(sh).multiline_text((20 - l, 26 - t), text, font=font, fill=(0, 0, 0, 140), align="center", spacing=spacing)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).multiline_text((20 - l, 20 - t), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill, align="center", spacing=spacing)
    return im

def pill(text, font, bg=YEL, fg=INK, padx=44, pady=18):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = (int(v) for v in d.textbbox((0, 0), text, font=font))
    w, h = r - l + 2 * padx, b - t + 2 * pady
    im = Image.new("RGBA", (w, h)); ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg)
    ImageDraw.Draw(im).text((padx - l, pady - t), text, font=font, fill=fg)
    return im

def card(lines, w=900):
    """การ์ดครีมมุมมน: lines = [(img, gap)]"""
    hh = sum(i.height + g for i, g in lines) + 70
    im = Image.new("RGBA", (w, hh)); ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, hh - 1), radius=48, fill=CREAM + (245,))
    y = 40
    for i, g in lines:
        im.alpha_composite(i, ((w - i.width) // 2, y)); y += i.height + g
    sh = Image.new("RGBA", (w + 80, hh + 80)); ImageDraw.Draw(sh).rounded_rectangle((40, 54, w + 40, hh + 54), radius=48, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); sh.alpha_composite(im, (40, 40))
    return sh

def num_badge(n):
    im = Image.new("RGBA", (150, 150)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 149, 149), fill=YEL); d.text((75, 78), str(n), font=F("Kanit-Bold.ttf", 96), fill=INK, anchor="mm")
    return im

def calendar():
    """ปฏิทิน 24 พ.ย. วาดเอง (อีโมจิ 📅 ขึ้นวันที่ผิด)"""
    im = Image.new("RGBA", (190, 200)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 10, 189, 199), radius=26, fill=WHITE, outline=(220, 210, 200), width=3)
    d.rounded_rectangle((0, 10, 189, 74), radius=26, fill=(226, 72, 72)); d.rectangle((0, 50, 189, 74), fill=(226, 72, 72))
    d.text((95, 44), "พ.ย.", font=F("Kanit-Bold.ttf", 40), fill=WHITE, anchor="mm")
    d.text((95, 138), "24", font=F("Kanit-Bold.ttf", 100), fill=INK, anchor="mm")
    return im


def dark(text, size, font="Kanit-SemiBold.ttf"):
    return text_img(text, F(font, size), fill=INK)

# ---------- ฉาก: (เริ่ม, จบ, [(ภาพ, cx, cy, หน่วงเข้า, แบบ)]) ----------
T = text_img
SC = []
def scene(t0, t1, items): SC.append((t0, t1, items))

scene(0.0, 2.8, [
    (T("ลอยกระทงปีนี้", F("Kanit-Bold.ttf", 120), stroke=4), 540, 700, 0.0, "pop"),
    (pill("อังคาร 24 พ.ย.", F("Kanit-Bold.ttf", 92)), 540, 880, 0.25, "pop"),
    (T("ไม่ต้องลางาน!", F("Kanit-Bold.ttf", 130), fill=YEL, stroke=5), 540, 1060, 0.6, "pop"),
    (emoji("🪷", 170), 540, 1330, 0.9, "float"),
])
scene(2.8, 5.0, [
    (card([(calendar(), 20), (dark("ไม่ใช่วันหยุดน้า", 86), 6), (dark("เลิกงานแล้วค่อยไปต่อ", 62, "Prompt-Medium.ttf"), 0)]), 540, 900, 0.0, "pop"),
    (emoji("💼", 120), 860, 1250, 0.4, "wiggle"),
])
ITEMS = [
    ("ใส่ชุดที่ไปต่อได้เลย", "หรือพกเสื้อไว้ในกระเป๋า", "👗", "👜"),
    ("ไม่ต้องไปไกล", "สวน กทม. 35 แห่ง\nเปิดถึงเที่ยงคืน (24 พ.ย.)", "🌳", "🕛"),
    ("ซื้อกระทงไว้ตั้งแต่เช้า", "เย็นไม่ต้องไปแย่งใคร", "🪷", "☀️"),
    ("เลี่ยงช่วงเลิกงานพีค ๆ", "ไปหลัง 2 ทุ่ม ก็ยังทัน", "🚗", "💨"),
    ("ไปไม่ทันจริง ๆ?", "ลอยออนไลน์จากมือถือได้\ngreener.bangkok.go.th", "📱", "✨"),
]
t = 5.0
for i, (a, b, e1, e2) in enumerate(ITEMS, 1):
    dur = 3.4 if i in (2, 5) else 3.0
    scene(t, t + dur, [
        (num_badge(i), 540, 600, 0.0, "pop"),
        (card([(dark(a, 76), 12), (dark(b, 54, "Prompt-Medium.ttf"), 0)]), 540, 930, 0.15, "pop"),
        (emoji(e1, 150), 260, 1290, 0.4, "float"), (emoji(e2, 120), 820, 1290, 0.55, "wiggle"),
    ])
    t += dur
scene(t, t + 3.6, [
    (T("ปีนี้ไปลอยกี่โมง?", F("Kanit-Bold.ttf", 108), stroke=4), 540, 720, 0.0, "pop"),
    (pill("แท็กเพื่อนร่วมงานมาเลย!", F("Kanit-Bold.ttf", 72)), 540, 900, 0.3, "pop"),
    (T("เซฟไว้ก่อนวันอังคาร 🌕".replace(" 🌕", ""), F("Prompt-Medium.ttf", 58)), 540, 1040, 0.6, "pop"),
    (emoji("🪷", 140), 360, 1300, 0.8, "float"), (emoji("🕯️", 120), 720, 1300, 0.9, "float"),
])
TOTAL = t + 3.6

def scale_at(dt):
    if dt < 0: return 0
    if dt < 0.3:
        x = dt / 0.3
        return 1.12 * math.sin(x * math.pi / 2) if x < 0.75 else 1.12 - 0.12 * (x - 0.75) / 0.25
    return 1.0

def frame(tt):
    im = BG.copy(); im.alpha_composite(bokeh_layer(tt))
    for t0, t1, items in SC:
        if not (t0 <= tt < t1): continue
        fade = min(1, (t1 - tt) / 0.18)
        for img, cx, cy, delay, kind in items:
            dt = tt - t0 - delay; s = scale_at(dt)
            if s <= 0.02: continue
            p = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
            if kind == "wiggle": p = p.rotate(7 * math.sin(dt * 8), expand=True, resample=Image.BICUBIC)
            yo = -14 * math.sin(dt * 2.5) if kind == "float" else 0
            if fade < 1:
                a = p.getchannel("A").point(lambda v: int(v * fade)); p.putalpha(a)
            im.alpha_composite(p, (int(cx - p.width / 2), int(cy + yo - p.height / 2)))
    return im.convert("RGB")

def main(out):
    n = int(TOTAL * FPS)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        wr.stdin.write(frame(i / FPS).tobytes())
    wr.stdin.close(); wr.wait()
    frame(1.5).save(out.replace(".mp4", "-frame-hook.png"))
    print("total", round(TOTAL, 2))

if __name__ == "__main__":
    main(sys.argv[1])
