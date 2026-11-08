"""เอฟเฟกต์ "วิ้ง ๆ" (ประกายดาวกระพริบ) ซ้อนบนคลิปแนวตั้ง 1080x1920

ตัวอย่าง:
    python3 office/editor/sparkles.py --video base.mp4 --out sparkly.mp4 \
        --bursts 0,2,4,6,9,11,13 --boost 2-4,11-13

- ประกายเบา ๆ ลอยระยิบตลอดคลิป (ส่วนบนของจอ = ท้องฟ้า/วิว)
- --bursts: เวลา (วินาที) ที่มีประกายวิ้งรอบแถบซับ (ใส่เวลาที่ซับเปลี่ยน)
- --boost: ช่วงเวลาที่ให้วิ้งมากขึ้น เช่น ช็อตเด่น "2-4,11-13"
- --density: จำนวนประกายพื้นหลังต่อวินาที (ค่าเริ่มต้น 2 = เบา ๆ พอดี เจ้าของช่องบอกว่า 6 เยอะไป)
- --burst-count: จำนวนประกายต่อครั้งที่ซับเปลี่ยน (ค่าเริ่มต้น 3)
ใส่เอฟเฟกต์ก่อน แล้วค่อยใส่ซับด้วย burn_subs.py (ซับจะอยู่บนสุด)
"""
import argparse
import json
import math
import random
import subprocess

from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
COLORS = [(255, 255, 255), (255, 214, 235), (255, 236, 179), (230, 220, 255)]
SUB_Y = (1250, 1460)  # แถบซับโดยประมาณ (ตรงกับ burn_subs.py)


def star_sprite(color, size=160):
    """4-point twinkle star with soft glow."""
    s = size * 4  # supersample
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    long_, thin = s * 0.48, s * 0.06
    for ang in (0, 90):
        a = math.radians(ang)
        pts = []
        for k, r in enumerate([long_, thin, long_, thin]):
            t = a + k * math.pi / 2
            pts.append((c + r * math.cos(t), c + r * math.sin(t)))
        d.polygon(pts, fill=color + (255,))
    im = im.resize((size, size), Image.LANCZOS)
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((size * 0.3, size * 0.3, size * 0.7, size * 0.7), fill=color + (200,))
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.1))
    return Image.alpha_composite(glow, im)


def parse_ranges(s):
    out = []
    for part in filter(None, s.split(",")):
        a, b = part.split("-")
        out.append((float(a), float(b)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bursts", default="")
    ap.add_argument("--boost", default="")
    ap.add_argument("--density", type=float, default=2.0)
    ap.add_argument("--burst-count", type=int, default=3, help="จำนวนประกายต่อครั้งที่ซับเปลี่ยน")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()

    dur = float(json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", a.video],
        capture_output=True, text=True, check=True).stdout)["format"]["duration"])
    rnd = random.Random(a.seed)
    sprites = [star_sprite(c) for c in COLORS]
    boost = parse_ranges(a.boost)

    # each sparkle: (start, life, x, y, max_size, sprite_idx, spin)
    sparks = []
    t = 0.0
    while t < dur:
        mult = 2.2 if any(x <= t < y for x, y in boost) else 1.0
        t += rnd.expovariate(a.density * mult)
        sparks.append((t, rnd.uniform(0.6, 1.1), rnd.uniform(60, W - 60),
                       rnd.uniform(80, H * 0.48), rnd.uniform(50, 115),
                       rnd.randrange(len(sprites)), rnd.uniform(-40, 40)))
    for b in filter(None, a.bursts.split(",")):
        b = float(b)
        for _ in range(a.burst_count):
            sparks.append((b + rnd.uniform(0, 0.35), rnd.uniform(0.5, 0.8),
                           rnd.uniform(150, W - 150), rnd.uniform(*SUB_Y),
                           rnd.uniform(70, 140), rnd.randrange(len(sprites)),
                           rnd.uniform(-40, 40)))

    ff = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", a.video,
         "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", a.out],
        stdin=subprocess.PIPE)
    n = int(round(dur * FPS))
    for f in range(n):
        tt = f / FPS
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for st, life, x, y, size, si, spin in sparks:
            p = (tt - st) / life
            if not 0 <= p <= 1:
                continue
            k = math.sin(math.pi * p) ** 1.5  # grow then shrink = twinkle
            sz = max(2, int(size * k))
            spr = sprites[si].rotate(spin * p, resample=Image.BICUBIC).resize(
                (sz, sz), Image.LANCZOS)
            canvas.alpha_composite(spr, (int(x - sz / 2), int(y - sz / 2)))
        ff.stdin.write(canvas.tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")


if __name__ == "__main__":
    main()
