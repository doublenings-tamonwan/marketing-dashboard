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
- "theme": "bold" = ธีมจัดจ้าน (พื้นแดง แสงรัศมีหมุน กล่องหัวข้อเข้ม ตัวเหลือง การ์ดขอบหนา) เห็นแล้วหยุดดู
  "theme": "party" = ธีมเกมโชว์ (พื้นม่วง-ชมพู ของลอย พลุกระดาษตอนเฉลย) / "cream" = เรียบ (ค่าเริ่มต้น)
- "challenge": {"text": "ได้ครบ 5 = สายซีรีส์ตัวจริง!", "until": 2.2} = สติกเกอร์ท้าทายช่วงเปิดคลิป (ฮุก)
- outro "follow": "ติดตามไว้ พรุ่งนี้เฉลย!" = ปุ่ม "+ ติดตาม" เด้ง ๆ ตอนจบ (เพิ่มยอดติดตาม)
- "image": "path.jpg" (ไม่บังคับ) = ตอนเฉลยโชว์ภาพในกรอบรูปบนการ์ด แทนแถวอีโมจิเล็ก
  ใช้ "PLACEHOLDER" เพื่อดูตำแหน่งก่อนมีภาพจริง — ภาพจากซีรีส์มีลิขสิทธิ์ ใช้เมื่อเจ้าของช่องตัดสินใจเองเท่านั้น
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

import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


def base_frame_party(plan, qi, n):
    top, bot = np.array([34, 16, 54]), np.array([118, 30, 96])
    grad = (top + (bot - top) * np.linspace(0, 1, H)[:, None]).astype("uint8")
    im = Image.fromarray(np.repeat(grad[:, None, :], W, axis=1), "RGB").convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((40, 420, 1040, 1240), fill=(255, 105, 180, 120))
    gd.ellipse((-200, 1450, 500, 2150), fill=(255, 140, 90, 70))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(im)
    pill(d, W / 2, 222, plan.get("kicker", ""), F("Prompt-Medium.ttf", 34))
    tf = F("Prompt-SemiBold.ttf", 84)
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(tl).text((W / 2, 300), plan["title"], font=tf, fill=(255, 105, 180, 255), anchor="mt")
    im.alpha_composite(tl.filter(ImageFilter.GaussianBlur(14)))
    d.text((W / 2, 300), plan["title"], font=tf, fill=(255, 255, 255), anchor="mt")
    gap = 46
    x0 = W / 2 - gap * (n - 1) / 2
    for i in range(n):
        r = 12 if i == qi else 8
        col = (255, 105, 180) if i <= qi else (96, 62, 110)
        d.ellipse((x0 + i * gap - r, 450 - r, x0 + i * gap + r, 450 + r), fill=col)
    cg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cg).rounded_rectangle((80, CARD[0] - 10, 1000, CARD[1] + 10), radius=64,
                                         fill=(255, 105, 180, 200))
    im.alpha_composite(cg.filter(ImageFilter.GaussianBlur(28)))
    d.rounded_rectangle((90, CARD[0], 990, CARD[1]), radius=56, fill=(255, 255, 255),
                        outline=(255, 105, 180), width=8)
    return im


YELLOW = (255, 211, 77)
DARK = (35, 26, 40)


def make_rays():
    size = 2600
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    for k in range(24):
        a0, a1 = math.radians(k * 15), math.radians(k * 15 + 7.5)
        d.polygon([(c, c), (c + size * math.cos(a0), c + size * math.sin(a0)),
                   (c + size * math.cos(a1), c + size * math.sin(a1))], fill=(255, 255, 255, 26))
    return im


def bold_bg(rays, t):
    top, bot = np.array([214, 40, 52]), np.array([120, 14, 40])
    grad = (top + (bot - top) * np.linspace(0, 1, H)[:, None]).astype("uint8")
    im = Image.fromarray(np.repeat(grad[:, None, :], W, axis=1), "RGB").convert("RGBA")
    r = rays.rotate(t * 6, resample=Image.BILINEAR)
    cx, cy = W // 2, (CARD[0] + CARD[1]) // 2
    # แสงรัศมีหมุนรอบกลางการ์ด
    im.alpha_composite(r.crop((r.width // 2 - cx, r.height // 2 - cy,
                               r.width // 2 - cx + W, r.height // 2 - cy + H)))
    return im


def overlay_bold(plan, qi, n):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # กล่องหัวข้อเข้ม ตัวเหลือง
    d.rounded_rectangle((70, 196, 1010, 446), radius=40, fill=DARK)
    d.text((W / 2, 222), plan.get("kicker", ""), font=F("Prompt-Medium.ttf", 34), fill=(255, 255, 255), anchor="mt")
    d.text((W / 2, 268), plan["title"], font=fit_font(plan["title"], "Prompt-SemiBold.ttf", 104, 860),
           fill=YELLOW, anchor="mt")
    # แถบความคืบหน้าเป็นช่อง ๆ
    seg, gap = 120, 14
    x0 = W / 2 - (n * seg + (n - 1) * gap) / 2
    for i in range(n):
        x = x0 + i * (seg + gap)
        d.rounded_rectangle((x, 470, x + seg, 488), radius=9,
                            fill=YELLOW if i <= qi else (255, 255, 255, 90))
    # การ์ดสไตล์การ์ตูน: เงาทึบ + ขอบหนา
    d.rounded_rectangle((104, CARD[0] + 18, 1004, CARD[1] + 18), radius=56, fill=DARK)
    d.rounded_rectangle((90, CARD[0], 990, CARD[1]), radius=56, fill=(255, 250, 240), outline=DARK, width=8)
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
    party = plan.get("theme") == "party"
    bold = plan.get("theme") == "bold"
    if bold:
        rays = make_rays()
        overlays = [overlay_bold(plan, i, n) for i in range(n)]
    else:
        bases = [(base_frame_party if party else base_frame)(plan, i, n) for i in range(n)]

    def get_base(i, t):
        if bold:
            b = bold_bg(rays, t)
            b.alpha_composite(overlays[i])
            return b
        return bases[i].copy()
    rnd = random.Random(5)
    decor = []
    if party:
        sprites = [emoji_strip(e, h) for e, h in
                   [("✨", 64), ("💕", 60), ("🍿", 74), ("📺", 70), ("⭐", 56), ("🎬", 66)]]
        for _ in range(16):
            sp = rnd.choice(sprites)
            a_ = sp.getchannel("A").point(lambda v: int(v * 0.55))
            sp = sp.copy()
            sp.putalpha(a_)
            decor.append((sp, rnd.uniform(40, W - 40), rnd.uniform(0, H), rnd.uniform(40, 90),
                          rnd.uniform(0, 6.28)))
    confetti_cols = [(255, 105, 180), (255, 214, 102), (130, 210, 255), (255, 255, 255), (186, 140, 255)]
    bursts = {}
    for qi_, q_ in enumerate(qs):
        if "reveal" in q_:
            bursts[qi_] = [(rnd.uniform(-1, 1) * 900, rnd.uniform(-1300, -500), rnd.choice(confetti_cols),
                            rnd.uniform(10, 18)) for _ in range(46)]
    big = [emoji_strip(q["emoji"], 230 if plan.get("theme") == "bold" else 190) for q in qs]
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
    def framed(q):
        """กรอบรูปแนวตั้ง 3:4 (เหมาะกับโปสเตอร์) — "image_focus": [x, y] 0–1 = จุดที่ต้องการให้อยู่กลางกรอบ"""
        src = q["image"]
        fw, fh = 216, 288
        if src == "PLACEHOLDER":
            ph = Image.new("RGBA", (fw, fh), (236, 226, 230, 255))
            dd = ImageDraw.Draw(ph)
            dd.text((fw / 2, fh / 2), "ภาพจากซีรีส์", font=F("Prompt-Medium.ttf", 30), fill=MUTED, anchor="mm")
        else:
            from PIL import ImageOps
            fx, fy = q.get("image_focus", [0.5, 0.4])
            ph = ImageOps.fit(Image.open(src).convert("RGBA"), (fw, fh), Image.LANCZOS, centering=(fx, fy))
        mask = Image.new("L", (fw, fh), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, fw - 1, fh - 1), radius=24, fill=255)
        out = Image.new("RGBA", (fw + 20, fh + 20), (0, 0, 0, 0))
        ImageDraw.Draw(out).rounded_rectangle((0, 0, fw + 19, fh + 19), radius=30,
                                              fill=DARK if plan.get("theme") == "bold" else PINK_BG)
        out.paste(ph, (10, 10), mask)
        return out
    imgs = [framed(q) if q.get("image") else None for q in qs]
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
    num_fs = {sz: F("Prompt-SemiBold.ttf", sz) for sz in range(60, 92, 4)}

    def overlay(im, t, qi, q):
        if not (party or bold):
            return
        for sp, x, y0, spd, ph in decor:  # ของลอย: ผ่าน "หลัง" การ์ด
            y = (y0 - spd * t) % (H + 200) - 100
            xx = x + 24 * math.sin(t * 1.3 + ph)
            if 70 < xx < 1010 and (CARD[0] - 40 < y < CARD[1] + 40 or 190 < y < 480):
                continue  # ไม่ทับการ์ดและหัวข้อ
            im.alpha_composite(sp, (int(xx - sp.width / 2), int(y - sp.height / 2)))
        rev = q.get("reveal")
        if rev is not None and 0 <= t - rev < 0.7:  # พลุสั้น ๆ ไม่บังชื่อเรื่องนาน
            dt = t - rev
            d2 = ImageDraw.Draw(im)
            if dt < 0.1:  # แฟลช
                fl = Image.new("RGBA", (W, H), (255, 255, 255, int(110 * (1 - dt / 0.1))))
                im.alpha_composite(fl)
            for vx, vy, col, sz in bursts[qi]:
                x = W / 2 + vx * dt
                y = CARD[0] + 280 + vy * dt + 1900 * dt * dt
                d2.rectangle((x, y, x + sz, y + sz * 0.6), fill=col)
    for fi in range(int(round(total * FPS))):
        t = fi / FPS
        if outro and t >= outro["start"]:
            im = get_base(len(qs) - 1, t)
            d = ImageDraw.Draw(im)
            k = ease((t - outro["start"]) / 0.25)
            paste_center(im, small[-1], W / 2, 660, 1.0)
            paste_center(im, text_layer([(outro["line1"], F("Prompt-SemiBold.ttf", 66), INK)]),
                         W / 2, 830, 0.8 + 0.2 * k, k)
            if k > 0.5:
                pill(d, W / 2, 920, outro["line2"], F("Prompt-Medium.ttf", 38))
            if outro.get("follow") and t - outro["start"] > 0.35:
                kk = ease((t - outro["start"] - 0.35) / 0.25)
                bump = 1 + 0.06 * math.sin((t - outro["start"]) * 7)
                btn = Image.new("RGBA", (620, 150), (0, 0, 0, 0))
                bd = ImageDraw.Draw(btn)
                bd.rounded_rectangle((8, 12, 612, 142), radius=65, fill=DARK)
                bd.rounded_rectangle((0, 0, 604, 130), radius=65, fill=(254, 44, 85), outline=DARK, width=6)
                bd.text((302, 65), "+ ติดตาม", font=F("Prompt-SemiBold.ttf", 64), fill="white", anchor="mm")
                paste_center(im, btn, W / 2, CARD[1] + 120, kk * bump, kk)
                paste_center(im, text_layer([(outro["follow"], F("Prompt-SemiBold.ttf", 46),
                                              (255, 255, 255))]), W / 2, CARD[1] + 245, 1.0, kk)
            overlay(im, t, len(qs) - 1, {})
            ff.stdin.write(im.convert("RGB").tobytes())
            continue
        qi = max(i for i, q in enumerate(qs) if t >= q["start"] or i == 0)
        q = qs[qi]
        im = get_base(qi, t)
        d = ImageDraw.Draw(im)
        rev = q.get("reveal")
        if not (imgs[qi] is not None and rev is not None and t >= rev):
            if bold:
                pill(d, W / 2, CARD[0] - 28, f"ข้อ {qi + 1}", F("Prompt-SemiBold.ttf", 46), bg=YELLOW, fg=DARK,
                     padx=44, pady=8)
            else:
                pill(d, W / 2, CARD[0] + 40, f"ข้อ {qi + 1}", label_f)
        if rev is not None and t >= rev:
            k = ease((t - rev) / 0.22)
            if imgs[qi] is not None:
                paste_center(im, imgs[qi], W / 2, CARD[0] + 172, 0.8 + 0.2 * k, k)
                paste_center(im, answers[qi], W / 2, CARD[0] + 440, 0.85 + 0.15 * k, k)
            else:
                paste_center(im, small[qi], W / 2, CARD[0] + 230, 1.0)
                paste_center(im, answers[qi], W / 2, CARD[0] + 400, 0.85 + 0.15 * k, k)
        else:
            k = ease((t - q["start"]) / 0.22)
            cy = CARD[0] + 230 if q.get("mystery") else CARD[0] + 320
            paste_center(im, big[qi], W / 2, cy, 0.6 + 0.4 * k, k)
            if q.get("mystery"):
                pulse = 1 + (0.07 * math.sin(t * 6) if (party or bold) else 0)
                paste_center(im, qmark, W / 2, CARD[0] + 435, (0.7 + 0.3 * k) * pulse, k)
            cd = q.get("countdown")
            if cd is not None and rev is not None and cd <= t < rev:
                step = (rev - cd) / 3
                num = 3 - int((t - cd) // step)
                p = ((t - cd) % step) / step
                cx, cy2, r = W / 2, CARD[1] + 75, 50  # ใต้การ์ด ไม่ทับอีโมจิ
                if party:  # วงใหญ่ขึ้น เด้งทุกครั้งที่นับ
                    r = 62
                    d.ellipse((cx - r - 6, cy2 - r - 6, cx + r + 6, cy2 + r + 6), fill=(255, 255, 255))
                if bold:
                    r = 66
                    d.ellipse((cx - r - 8, cy2 - r - 8, cx + r + 8, cy2 + r + 8), fill=YELLOW, outline=DARK, width=6)
                track, numcol = ((255, 214, 231), INK) if party else ((240, 220, 228), INK)
                if bold:
                    track = (255, 236, 170)
                d.ellipse((cx - r, cy2 - r, cx + r, cy2 + r), outline=track, width=10)
                d.arc((cx - r, cy2 - r, cx + r, cy2 + r), -90, -90 + 360 * (1 - p), fill=ACCENT, width=10)
                nf = num_fs[min(88, 60 + 4 * int(7 * max(0, 1 - p * 4)))] if (party or bold) else num_f
                d.text((cx, cy2), str(max(1, num)), font=nf, fill=numcol, anchor="mm")
        ch = plan.get("challenge")
        if ch and t < ch.get("until", 2.2):
            kk = ease(t / 0.2)
            st = Image.new("RGBA", (760, 120), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((8, 10, 752, 118), radius=24, fill=DARK)
            sd.rounded_rectangle((0, 0, 744, 108), radius=24, fill=YELLOW, outline=DARK, width=6)
            sd.text((372, 54), ch["text"], font=fit_font(ch["text"], "Prompt-SemiBold.ttf", 52, 680),
                    fill=DARK, anchor="mm")
            st = st.rotate(-4, resample=Image.BICUBIC, expand=True)
            paste_center(im, st, W / 2, CARD[0] + 70, (1.3 - 0.3 * kk) * (1 + 0.03 * math.sin(t * 9)), kk)
        overlay(im, t, qi, q)
        ff.stdin.write(im.convert("RGB").tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")


if __name__ == "__main__":
    main()
