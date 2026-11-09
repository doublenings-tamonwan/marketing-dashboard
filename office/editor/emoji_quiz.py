"""ทำคลิปเกม "ทายจากอีโมจิ" 1080x1920 (ไม่ต้องมีฟุตเทจ) สไตล์ช่อง: พื้นครีม การ์ดขาว แถบป้ายชมพู

ตัวอย่าง:
    python3 office/editor/emoji_quiz.py --plan plan.json --out quiz.mp4 [--audio vo.wav]
แล้วใส่ซับต่อด้วย burn_subs.py (ซับอยู่ล่างการ์ด ไม่ทับกัน)

plan.json:
{
  "kicker": "ซีรีส์ชวนเล่น · EP.1",
  "title": "ทายซีรีส์จากอีโมจิ",
  "duration": 25.0,
  "questions": [
    {"emoji": "🏠📝💍", "start": 0.0, "countdown": 2.5, "reveal": 3.7, "end": 5.0,
     "answer": "Full House", "answer_th": "", "hint": "บ้าน · สัญญา · แต่งงาน"},
    {"emoji": "👑💔➡️💍🤴", "start": 18.0, "end": 22.0, "mystery": true}
  ],
  "outro": {"start": 22.0, "line1": "ได้กี่ข้อ? เมนต์บอก", "line2": "เฉลยพรุ่งนี้ในคอมเมนต์ปักหมุด"}
}
- countdown/reveal ไม่ใส่ = ไม่มีนับถอยหลัง/ไม่เฉลย; "mystery": true = โชว์ "?" ตัวใหญ่
- ไม่ใส่ --audio = ใส่เสียง "ติ๊ก" ตอนนับ และ "ติ๊ง" ตอนเฉลยให้อัตโนมัติ
  ใส่ --audio = ผสมเสียงพากย์กับเสียงติ๊ก (พากย์ดังกว่า)
"""
import argparse
import json
import math
import os
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
FONTS = os.path.join(HERE, "..", "assets", "fonts")
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
CREAM = (246, 237, 227)
INK = (43, 34, 48)
MUTED = (107, 90, 102)
PINK_BG = (255, 214, 231)
PINK_FG = (122, 14, 59)
ACCENT = (232, 90, 150)
CARD = (536, 1100)  # y top/bottom ของการ์ด (ซับของ burn_subs อยู่ที่ ~1250–1400)


def F(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def emoji_strip(text, height):
    f = ImageFont.truetype(EMOJI_FONT, 109, layout_engine=ImageFont.Layout.RAQM)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = probe.textbbox((0, 0), text, font=f, embedded_color=True)
    im = Image.new("RGBA", (r - l + 20, b - t + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=f, embedded_color=True)
    w = int(im.width * height / im.height)
    if w > 760:  # อีโมจิหลายตัว: ย่อให้อยู่ในการ์ด
        height, w = int(height * 760 / w), 760
    return im.resize((w, height), Image.LANCZOS)


def pill(d, cx, y, text, f, bg=PINK_BG, fg=PINK_FG, padx=34, pady=10):
    tw = d.textlength(text, font=f)
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * pady
    d.rounded_rectangle((cx - tw / 2 - padx, y, cx + tw / 2 + padx, y + h), radius=h // 2, fill=bg)
    d.text((cx, y + h / 2), text, font=f, fill=fg, anchor="mm")
    return h


def base_frame(plan, qi, n):
    im = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(im)
    d.ellipse((-260, -200, 420, 420), fill=(250, 226, 233))
    d.ellipse((760, 1500, 1360, 2100), fill=(250, 226, 233))
    d.text((W / 2, 250), plan.get("kicker", ""), font=F("Prompt-Medium.ttf", 36), fill=MUTED, anchor="mt")
    d.text((W / 2, 300), plan["title"], font=F("Prompt-SemiBold.ttf", 76), fill=INK, anchor="mt")
    # จุดความคืบหน้า
    gap = 44
    x0 = W / 2 - gap * (n - 1) / 2
    for i in range(n):
        r = 11 if i == qi else 8
        col = ACCENT if i <= qi else (220, 205, 210)
        d.ellipse((x0 + i * gap - r, 440 - r, x0 + i * gap + r, 440 + r), fill=col)
    # การ์ด
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((90, CARD[0] + 14, 990, CARD[1] + 14), radius=56,
                                         fill=(122, 14, 59, 28))
    im.alpha_composite(sh)
    d.rounded_rectangle((90, CARD[0], 990, CARD[1]), radius=56, fill=(255, 255, 255))
    return im


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def paste_center(im, part, cx, cy, scale=1.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    p = part.resize((max(1, int(part.width * scale)), max(1, int(part.height * scale))), Image.LANCZOS)
    if alpha < 1:
        a = p.getchannel("A").point(lambda v: int(v * alpha))
        p.putalpha(a)
    im.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))


def text_layer(lines):
    """lines: [(text, font, color)] → RGBA ภาพข้อความกึ่งกลาง"""
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    boxes = [probe.textbbox((0, 0), t, font=f) for t, f, _ in lines]
    w = int(max(b[2] - b[0] for b in boxes)) + 40
    hs = [int(b[3] - b[1]) + 18 for b in boxes]
    im = Image.new("RGBA", (w, sum(hs) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 10
    for (t, f, c), b, h in zip(lines, boxes, hs):
        d.text((w / 2, y - b[1]), t, font=f, fill=c, anchor="ma")
        y += h
    return im


def fit_font(text, name, size, maxw, weight=None):
    f = F(name, size, weight)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    while probe.textlength(text, font=f) > maxw and size > 40:
        size -= 4
        f = F(name, size, weight)
    return f


def build_audio(plan, total, vo_path, out):
    sr = 44100
    n = int(total * sr)
    mix = np.zeros(n)

    def add(sig, t, g):
        s = int(t * sr)
        e = min(n, s + len(sig))
        if s < n:
            mix[s:e] += g * sig[: e - s]

    tt = np.arange(int(0.07 * sr)) / sr
    tick = np.sin(2 * np.pi * 1700 * tt) * np.exp(-tt * 60)
    td = np.arange(int(0.5 * sr)) / sr
    ding = (np.sin(2 * np.pi * 1320 * td) + 0.5 * np.sin(2 * np.pi * 1980 * td)) * np.exp(-td * 7)
    for q in plan["questions"]:
        if "countdown" in q and "reveal" in q:
            step = (q["reveal"] - q["countdown"]) / 3
            for k in range(3):
                add(tick, q["countdown"] + k * step, 0.25)
        if "reveal" in q:
            add(ding, q["reveal"], 0.22)
    if vo_path:
        with wave.open(vo_path) as w:
            raw = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float) / 32768
            ch = w.getnchannels()
            vo = raw.reshape(-1, ch).mean(axis=1)
            if w.getframerate() != sr:
                idx = np.linspace(0, len(vo) - 1, int(len(vo) * sr / w.getframerate()))
                vo = np.interp(idx, np.arange(len(vo)), vo)
        mix *= 0.6
        add(vo, 0.0, 1.0)
    peak = np.abs(mix).max() or 1
    mix = mix / peak * 0.85
    pcm = (np.stack([mix, mix], axis=1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audio", help="ไฟล์ .wav เสียงพากย์ (จะผสมกับเสียงติ๊ก)")
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding="utf-8"))
    qs = plan["questions"]
    total = plan["duration"]
    n = len(qs)

    # เตรียมชิ้นส่วนล่วงหน้า
    bases = [base_frame(plan, i, n) for i in range(n)]
    big = [emoji_strip(q["emoji"], 190) for q in qs]
    small = [emoji_strip(q["emoji"], 110) for q in qs]
    label_f = F("Prompt-Medium.ttf", 40)
    answers = []
    for q in qs:
        if "answer" not in q:
            answers.append(None)
            continue
        lines = [(q["answer"], fit_font(q["answer"], "PlayfairDisplay-Italic.ttf", 104, 760, 600), INK)]
        if q.get("answer_th"):
            lines.append((q["answer_th"], fit_font(q["answer_th"], "Prompt-Medium.ttf", 50, 760), PINK_FG))
        if q.get("hint"):
            lines.append((q["hint"], F("Prompt-Medium.ttf", 34), MUTED))
        answers.append(text_layer(lines))
    qmark = text_layer([("?", F("PlayfairDisplay-Italic.ttf", 180, 700), ACCENT)])
    outro = plan.get("outro")

    tmp = tempfile.mkdtemp(prefix="quiz-")
    wav = os.path.join(tmp, "a.wav")
    build_audio(plan, total, a.audio, wav)
    ff = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out],
        stdin=subprocess.PIPE)
    num_f = F("Prompt-SemiBold.ttf", 64)
    for fi in range(int(round(total * FPS))):
        t = fi / FPS
        if outro and t >= outro["start"]:
            im = bases[-1].copy()
            d = ImageDraw.Draw(im)
            k = ease((t - outro["start"]) / 0.25)
            paste_center(im, small[-1], W / 2, 660, 1.0)
            paste_center(im, text_layer([(outro["line1"], F("Prompt-SemiBold.ttf", 66), INK)]),
                         W / 2, 830, 0.8 + 0.2 * k, k)
            if k > 0.5:
                pill(d, W / 2, 920, outro["line2"], F("Prompt-Medium.ttf", 38))
            ff.stdin.write(im.convert("RGB").tobytes())
            continue
        qi = max(i for i, q in enumerate(qs) if t >= q["start"] or i == 0)
        q = qs[qi]
        im = bases[qi].copy()
        d = ImageDraw.Draw(im)
        pill(d, W / 2, CARD[0] + 40, f"ข้อ {qi + 1}", label_f)
        rev = q.get("reveal")
        if rev is not None and t >= rev:
            k = ease((t - rev) / 0.22)
            paste_center(im, small[qi], W / 2, CARD[0] + 230, 1.0)
            paste_center(im, answers[qi], W / 2, CARD[0] + 400, 0.85 + 0.15 * k, k)
        else:
            k = ease((t - q["start"]) / 0.22)
            cy = CARD[0] + 230 if q.get("mystery") else CARD[0] + 320
            paste_center(im, big[qi], W / 2, cy, 0.6 + 0.4 * k, k)
            if q.get("mystery"):
                paste_center(im, qmark, W / 2, CARD[0] + 435, 0.7 + 0.3 * k, k)
            cd = q.get("countdown")
            if cd is not None and rev is not None and cd <= t < rev:
                step = (rev - cd) / 3
                num = 3 - int((t - cd) // step)
                p = ((t - cd) % step) / step
                cx, cy2, r = W / 2, CARD[1] + 75, 50  # ใต้การ์ด ไม่ทับอีโมจิ
                d.ellipse((cx - r, cy2 - r, cx + r, cy2 + r), outline=(240, 220, 228), width=10)
                d.arc((cx - r, cy2 - r, cx + r, cy2 + r), -90, -90 + 360 * (1 - p), fill=ACCENT, width=10)
                d.text((cx, cy2), str(max(1, num)), font=num_f, fill=INK, anchor="mm")
        ff.stdin.write(im.convert("RGB").tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")


if __name__ == "__main__":
    main()
