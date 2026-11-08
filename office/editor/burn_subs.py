"""ใส่ซับภาษาไทยลงวิดีโอ โดยวาดตัวอักษรด้วย Pillow + raqm (วางวรรณยุกต์ไทยถูกต้อง)

ทำไมไม่ใช้ ffmpeg ass/subtitles: libass ในเครื่องนี้ทำวรรณยุกต์ที่ซ้อนบนสระบนหาย
(เช่น "เดี๋ยว" กลายเป็น "เดียว", "ที่" กลายเป็น "ที") จึงต้องวาดเป็นภาพแล้วซ้อนแทน

ตัวอย่าง:
    python3 office/editor/burn_subs.py --video in.mp4 --subs subs.json --out out.mp4 \
        [--audio music.wav | --mute] [--style clean|cute]

subs.json: [{"start": 0.0, "end": 2.0, "text": "บรรทัดแรก\nบรรทัดที่สอง"}, ...]
  ใส่ "pos": "top" และ "size": 120 ได้ สำหรับหัวข้อตัวใหญ่ด้านบนจอ (ซ้อนพร้อมซับล่างได้)

สไตล์ประจำช่อง (--style clean, ค่าเริ่มต้น ตั้งแต่ 2026-11-08):
  Prompt Medium ตัวขาว เงาดำนุ่ม; ครอบคำสำคัญด้วย [วงเล็บเหลี่ยม] = แถบป้ายชมพู
  เช่น "เดินริมน้ำ…\n[ใจฟู]แบบงง ๆ" — ใช้ 1 คำต่อซับ
--style cute = แบบเดิม (Itim ขอบชมพูหนา) — ห้ามใส่อีโมจิทั้งสองแบบ
"""
import argparse
import json
import os
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
W, H = 1080, 1920
SIDE = 70          # ระยะขอบซ้ายขวา
BOTTOM = 520       # ระยะจากขอบล่าง (เว้นที่ให้ปุ่มของ TikTok)
TOP = 260          # ระยะจากขอบบน สำหรับหัวข้อ (pos=top)
WHITE = (255, 255, 255, 255)
PINK = (255, 105, 180, 255)
SHADOW = (190, 40, 120, 170)
PILL_BG = (255, 214, 231, 255)    # #FFD6E7
PILL_FG = (122, 14, 59, 255)      # #7A0E3B


def render_clean(text, font_path, size, path):
    """ตัวขาวเงานุ่ม + คำใน [ ] เป็นแถบป้ายชมพู"""
    lines = [[(seg[1:-1], True) if seg.startswith("[") else (seg, False)
              for seg in re.split(r"(\[[^\]]+\])", ln) if seg]
             for ln in text.split("\n")]
    while True:
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        padx, pady = int(size * 0.32), int(size * 0.06)
        widths = [sum(font.getlength(t) + (2 * padx + 8 if pill else 0) for t, pill in ln)
                  for ln in lines]
        if max(widths) <= W - 2 * SIDE or size <= 44:
            break
        size -= 4
    asc, desc = font.getmetrics()
    lh = int((asc + desc) * 1.12)
    pad = 40
    tw = int(max(widths)) + 2 * pad
    th = lh * len(lines) + 2 * pad
    shadow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    top = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(top)
    for li, (ln, lw) in enumerate(zip(lines, widths)):
        x = (tw - lw) / 2
        base = pad + li * lh + asc
        for t, pill in ln:
            w = font.getlength(t)
            if pill:
                x += 4
                dt.rounded_rectangle((x, base - asc + pady, x + w + 2 * padx, base + desc - pady),
                                     radius=(asc + desc) // 2, fill=PILL_BG)
                dt.text((x + padx, base), t, font=font, fill=PILL_FG, anchor="ls")
                x += w + 2 * padx + 4
            else:
                ds.text((x, base + 3), t, font=font, fill=(0, 0, 0, 215), anchor="ls",
                        stroke_width=max(2, size // 22), stroke_fill=(0, 0, 0, 215))
                dt.text((x, base), t, font=font, fill=WHITE, anchor="ls")
                x += w
    # เงานุ่มกว้าง + ขอบเข้มบาง ๆ → อ่านออกแม้บนพื้นขาว (ผนังตึก/เสื้อขาว)
    soft = shadow.filter(ImageFilter.GaussianBlur(size * 0.16))
    edge = shadow.filter(ImageFilter.GaussianBlur(1.6))
    out = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(soft, soft), edge), top)
    out.save(path)
    return tw, th


def render_cute(text, font_path, size, path):
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
    ap.add_argument("--style", choices=["clean", "cute"], default="clean")
    ap.add_argument("--font", help="ค่าเริ่มต้น: clean=Prompt-Medium.ttf, cute=Itim-Regular.ttf")
    ap.add_argument("--size", type=int, help="ค่าเริ่มต้น: clean=74, cute=96")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--audio", help="ไฟล์เสียงที่จะใส่แทนเสียงเดิม")
    g.add_argument("--mute", action="store_true", help="ใส่แทร็กเสียงเงียบ")
    a = ap.parse_args()

    clean = a.style == "clean"
    a.font = a.font or ("Prompt-Medium.ttf" if clean else "Itim-Regular.ttf")
    a.size = a.size or (74 if clean else 96)
    render = render_clean if clean else render_cute
    font_path = a.font if os.path.isabs(a.font) else os.path.join(FONT_DIR, a.font)
    subs = json.load(open(a.subs, encoding="utf-8"))
    tmp = tempfile.mkdtemp(prefix="subs-")

    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", a.video]
    chain, last = [], "0:v"
    for i, s in enumerate(subs):
        png = os.path.join(tmp, f"s{i}.png")
        tw, th = render(s["text"], font_path, s.get("size", a.size), png)
        dur = s["end"] - s["start"]
        cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
        st = s["start"]
        chain.append(
            f"[{i + 1}:v]format=rgba,fade=in:st=0:d=0.15:alpha=1,"
            f"fade=out:st={max(0, dur - 0.1):.3f}:d=0.1:alpha=1,"
            f"setpts=PTS+{st:.3f}/TB[t{i}]"
        )
        base_y = TOP if s.get("pos") == "top" else H - BOTTOM - th
        y = f"{base_y}+max(0\\,(0.18-(t-{st:.3f}))*160)"  # ลอยขึ้นตอนเข้า
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
