"""อีโมจิเด้งบนคลิป (+ พลุกระดาษ) — ใส่ก่อน burn_subs เพื่อให้ซับอยู่บนสุด
python3 emoji_pops.py --video base.mp4 --cues cues.json --out base-emoji.mp4
cues.json: [{"t": 9.85, "emoji": "🎉", "x": 900, "y": 820, "size": 190, "dur": 2.0, "confetti": true}, ...]
"""
import argparse, json, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)
    pad = 14; out = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    out.alpha_composite(im, (pad, pad))
    a = out.getchannel("A").filter(ImageFilter.MaxFilter(11))
    sh = Image.new("RGBA", out.size, (60, 20, 40, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(6)).point(lambda v: v * 0.35))
    rim = Image.new("RGBA", out.size, (255, 255, 255, 0)); rim.putalpha(a)
    res = Image.new("RGBA", out.size, (0, 0, 0, 0)); res.alpha_composite(sh, (0, 4)); res.alpha_composite(rim); res.alpha_composite(out)
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video"); ap.add_argument("--cues"); ap.add_argument("--out")
    a = ap.parse_args()
    cues = json.load(open(a.cues, encoding="utf-8"))
    for c in cues: c["img"] = emoji_img(c["emoji"], c.get("size", 170))
    pr = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                             "stream=width,height,r_frame_rate", "-of", "json", a.video]))["streams"][0]
    W, H = pr["width"], pr["height"]; n, d = map(int, pr["r_frame_rate"].split("/")); fps = n / d
    rd = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", a.video, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    rnd = random.Random(5)
    conf = {}
    for i, c in enumerate(cues):
        if c.get("confetti"):
            conf[i] = [(rnd.uniform(0, W), rnd.uniform(-300, 0), rnd.uniform(-60, 60), rnd.uniform(500, 900), rnd.uniform(0, 6.28),
                        rnd.choice([(255, 99, 99), (255, 209, 102), (120, 190, 255), (150, 220, 140), (255, 160, 210)])) for _ in range(70)]
    fsz = W * H * 3; f = 0
    while True:
        buf = rd.stdout.read(fsz)
        if len(buf) < fsz: break
        t = f / fps; frame = None
        for i, c in enumerate(cues):
            lt = t - c["t"]; dur = c.get("dur", 1.8)
            if not (0 <= lt < dur): continue
            if frame is None: frame = Image.frombytes("RGB", (W, H), buf).convert("RGBA")
            if i in conf:
                dr = ImageDraw.Draw(frame)
                for (x0, y0, vx, vy, ph, col) in conf[i]:
                    x = x0 + vx * lt + 25 * math.sin(lt * 6 + ph); y = y0 + vy * lt
                    s = 9 * abs(math.cos(lt * 8 + ph)) + 3
                    dr.rectangle([x - 8, y - s, x + 8, y + s], fill=col)
            k = min(1, lt / 0.18); scale = (0.2 + 0.8 * k) * (1 + 0.25 * math.sin(k * math.pi))
            alpha = min(1, (dur - lt) / 0.25)
            im = c["img"]; sw = max(1, int(im.width * scale))
            e = im.resize((sw, sw), Image.LANCZOS).rotate(8 * math.sin(lt * 5), resample=Image.BICUBIC)
            if alpha < 1: e.putalpha(e.getchannel("A").point(lambda v: int(v * alpha)))
            yy = c["y"] - 12 * math.sin(lt * 3)
            frame.alpha_composite(e, (int(c["x"] - e.width / 2), int(yy - e.height / 2)))
        wr.stdin.write(buf if frame is None else frame.convert("RGB").tobytes()); f += 1
    wr.stdin.close(); wr.wait()

if __name__ == "__main__":
    main()
