"""EP.2 ดูบัว v8: ใส่สติกเกอร์อีโมจิเด้ง + บับเบิลคำพูดน้องแพะ + ซูมเด้งตอนเปลี่ยนช็อต (ไม่แต่งสีภาพ)
ใช้: python3 stickers_v8.py <in.mp4> <out.mp4>
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FONTS = os.path.join(REPO, "office", "assets", "fonts")
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
CUTS = [2, 4, 5.5, 7, 8, 9.2, 10, 11.5, 13, 15.5, 17, 19]   # จุดเปลี่ยนช็อต (ตาม build_v6)

_cache = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _cache:
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (160, 160))
        ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
        im = im.crop(im.getbbox())
        s = size / max(im.size)
        _cache[k] = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    return _cache[k]

def bubble(text, emo):
    f = ImageFont.truetype(os.path.join(FONTS, "Prompt-SemiBold.ttf"), 56)
    tw = f.getlength(text); e = emoji(emo, 64)
    bw, bh = int(tw + e.width + 90), 120
    im = Image.new("RGBA", (bw + 20, bh + 70))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, bw + 10, bh + 10), radius=60, fill=(255, 255, 255, 245), outline=(58, 42, 0), width=5)
    d.polygon([(70, bh + 2), (130, bh + 2), (40, bh + 62)], fill=(255, 255, 255, 245), outline=(58, 42, 0))
    d.line([(70, bh + 8), (40, bh + 62), (130, bh + 8)], fill=(58, 42, 0), width=5)
    d.rectangle((72, bh - 2, 128, bh + 9), fill=(255, 255, 255, 245))
    d.text((45, 10 + bh / 2), text, font=f, fill=(58, 42, 0), anchor="lm")
    im.alpha_composite(e, (int(55 + tw), int(10 + bh / 2 - e.height / 2)))
    return im

def word(text, size, fill):
    f = ImageFont.truetype(os.path.join(FONTS, "Kanit-Bold.ttf"), size)
    l, t, r, b = f.getbbox(text, stroke_width=10)
    im = Image.new("RGBA", (r - l + 20, b - t + 20))
    ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=f, fill=fill, stroke_width=10, stroke_fill=(58, 42, 0))
    return im

# (เริ่ม, จบ, ภาพ, cx, cy, แบบเคลื่อนไหว)
S = [
    (0.25, 2.0, emoji("✨", 120), 880, 640, "pop"), (0.45, 2.0, emoji("💛", 95), 130, 640, "pop"),
    (2.3, 4.0, emoji("📍", 110), 930, 1250, "pop"),
    (4.3, 7.0, emoji("🪷", 120), 920, 1330, "float"), (4.6, 7.0, emoji("🌿", 95), 150, 1450, "float"),
    (7.3, 10.0, emoji("🍰", 120), 900, 560, "pop"), (7.6, 10.0, emoji("😍", 105), 170, 600, "wiggle"),
    (10.3, 13.0, emoji("😋", 125), 900, 560, "wiggle"), (10.6, 13.0, emoji("🔥", 100), 170, 600, "pop"),
    (13.25, 15.5, bubble("อร่อยจัง ขออีกได้มั้ย", "🥺"), 650, 600, "pop"),
    (13.7, 15.5, word("งั่ม งั่ม!", 80, (255, 225, 77)), 250, 1180, "wiggle"),
    (15.7, 17.0, emoji("🎶", 105), 880, 900, "float"),
    (17.2, 19.0, emoji("📸", 115), 160, 1660, "pop"), (17.45, 19.0, emoji("💕", 105), 930, 1660, "wiggle"),
    (19.3, 21.5, emoji("✨", 100), 150, 520, "pop"), (19.5, 21.5, emoji("🐐", 110), 930, 1420, "wiggle"),
]

def scale_at(dt, kind):
    if dt < 0.28:                        # เด้งเข้า: 0 → 1.18 → 1
        x = dt / 0.28
        return 1.18 * math.sin(x * math.pi / 2) if x < 0.75 else 1.18 - 0.18 * (x - 0.75) / 0.25
    return 1.0 + (0.04 * math.sin(dt * 6) if kind == "pop" else 0)

def main(src, out):
    n = int(round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                    "-of", "csv=p=0", src])) * FPS))
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-an", out], stdin=subprocess.PIPE)
    for i in range(n):
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        t = i / FPS
        im = Image.frombytes("RGB", (W, H), buf)
        for c in CUTS:                   # ซูมเด้งเบา ๆ ตอนเปลี่ยนช็อต
            if 0 <= t - c < 0.22:
                z = 1.06 - 0.06 * (t - c) / 0.22
                cw, ch = W / z, H / z
                im = im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        im = im.convert("RGBA")
        for t0, t1, sp, cx, cy, kind in S:
            if not (t0 <= t < t1):
                continue
            dt = t - t0
            s = scale_at(dt, kind)
            if s <= 0.02:
                continue
            ang = 8 * math.sin(dt * 9) if kind == "wiggle" else 0
            dy = -12 * math.sin(dt * 3) if kind == "float" else 0
            p = sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.LANCZOS)
            if ang:
                p = p.rotate(ang, expand=True, resample=Image.BICUBIC)
            im.alpha_composite(p, (int(cx - p.width / 2), int(cy + dy - p.height / 2)))
        wr.stdin.write(im.convert("RGB").tobytes())
    wr.stdin.close(); wr.wait(); rd.wait()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
