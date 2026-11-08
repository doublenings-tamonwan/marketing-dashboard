"""ใส่ซับภาษาไทยลงวิดีโอ โดยวาดตัวอักษรด้วย Pillow + raqm (วางวรรณยุกต์ไทยถูกต้อง)

ทำไมไม่ใช้ ffmpeg ass/subtitles: libass ในเครื่องนี้ทำวรรณยุกต์ที่ซ้อนบนสระบนหาย
(เช่น "เดี๋ยว" กลายเป็น "เดียว", "ที่" กลายเป็น "ที") จึงต้องวาดเป็นภาพแล้วซ้อนแทน

ตัวอย่าง:
    python3 office/editor/burn_subs.py --video in.mp4 --subs subs.json --out out.mp4 \
        [--audio music.wav | --mute] [--font Itim-Regular.ttf]

subs.json: [{"start": 0.0, "end": 2.0, "text": "บรรทัดแรก\nบรรทัดที่สอง"}, ...]
สไตล์ประจำช่อง: ตัวขาว ขอบชมพู เงาชมพูเข้ม ค่อย ๆ ลอยขึ้นตอนเข้า — ห้ามใส่อีโมจิ
"""
import argparse
import json
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
W, H = 1080, 1920
SIDE = 70          # ระยะขอบซ้ายขวา
BOTTOM = 520       # ระยะจากขอบล่าง (เว้นที่ให้ปุ่มของ TikTok)
WHITE = (255, 255, 255, 255)
PINK = (255, 105, 180, 255)
SHADOW = (190, 40, 120, 170)


def render(text, font_path, size, path):
    while True:
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        box = probe.multiline_textbbox((0, 0), text, font=font, stroke_width=8,
                                       align="center", spacing=12)
        if box[2] - box[0] <= W - 2 * SIDE or size <= 50:
            break
        size -= 4  # ย่อฟอนต์อัตโนมัติถ้าบรรทัดยาวเกินจอ
    pad = 30
    box = [int(round(v)) for v in box]
    tw, th = box[2] - box[0] + 2 * pad, box[3] - box[1] + 2 * pad + 8
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    org = (tw // 2, pad - box[1])
    kw = dict(font=font, anchor="ma", align="center", spacing=12)
    d.multiline_text((org[0], org[1] + 6), text, fill=SHADOW, stroke_width=8,
                     stroke_fill=SHADOW, **kw)
    d.multiline_text(org, text, fill=WHITE, stroke_width=8, stroke_fill=PINK, **kw)
    im.save(path)
    return tw, th


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--subs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--font", default="Itim-Regular.ttf")
    ap.add_argument("--size", type=int, default=96)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--audio", help="ไฟล์เสียงที่จะใส่แทนเสียงเดิม")
    g.add_argument("--mute", action="store_true", help="ใส่แทร็กเสียงเงียบ")
    a = ap.parse_args()

    font_path = a.font if os.path.isabs(a.font) else os.path.join(FONT_DIR, a.font)
    subs = json.load(open(a.subs, encoding="utf-8"))
    tmp = tempfile.mkdtemp(prefix="subs-")

    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", a.video]
    chain, last = [], "0:v"
    for i, s in enumerate(subs):
        png = os.path.join(tmp, f"s{i}.png")
        tw, th = render(s["text"], font_path, a.size, png)
        dur = s["end"] - s["start"]
        cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
        st = s["start"]
        chain.append(
            f"[{i + 1}:v]format=rgba,fade=in:st=0:d=0.15:alpha=1,"
            f"fade=out:st={max(0, dur - 0.1):.3f}:d=0.1:alpha=1,"
            f"setpts=PTS+{st:.3f}/TB[t{i}]"
        )
        y = f"{H - BOTTOM - th}+max(0\\,(0.18-(t-{st:.3f}))*160)"  # ลอยขึ้นตอนเข้า
        chain.append(
            f"[{last}][t{i}]overlay=x=(W-w)/2:y='{y}':eof_action=pass:eval=frame[v{i}]"
        )
        last = f"v{i}"

    n = len(subs) + 1
    if a.audio:
        cmd += ["-i", a.audio]
        amap = f"{n}:a"
    elif a.mute:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        amap = f"{n}:a"
    else:
        amap = "0:a?"
    cmd += ["-filter_complex", ";".join(chain), "-map", f"[{last}]", "-map", amap,
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
