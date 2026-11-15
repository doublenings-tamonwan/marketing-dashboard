#!/usr/bin/env python3
"""พามารีวิว EP.2 · บางกะเจ้า — v2
คำติชมเจ้าของช่อง: "สีเป็นคลิปจริง ไม่ต้องใส่สี อยากให้ mood น่ารัก น่าสนใจกว่านี้"
+ อัปเดต: "ตัดให้คลิปดูน่าติดตาม ตลกนิดนึง ยังไม่ต้องใส่ sound" (เจ้าของช่องเลือกเพลงในแอปเอง)

- ไม่มี glow / โทนอุ่น / วิ้ง ไม่ปรับสี/คอนทราสต์/ความอิ่มสี: ใช้ค่าพิกเซลเดิมของไฟล์ (iPhone HLG)
  แล้วติดป้ายสีเป็นวิดีโอปกติ bt709 ให้ทุกเครื่องแสดงเหมือนภาพตัวอย่าง (ไม่ให้มือถือเร่งแสง HDR เอง)
- ไม่มีเสียง (ส่งออกแทร็กเงียบ --mute)
- ช็อต ~0.9–1.2 วิ, whip 3 จุด, ซูมกระแทก, หน้าตกใจ = ซูมเข้าหน้า + หยุดภาพ, ห่าน = ตัดเข้าทันที + เล่นซ้ำ + หยุดภาพ
- สติกเกอร์วาดเองด้วย PIL (หัวใจ/ดาววิ้ง, หยดเหงื่อ/เส้นตกใจ, วงกลม+ลูกศร, โน้ตเพลง/หัวใจ)
- ฮุกเปิดตัวใหญ่เด้งเข้า (วาดด้วย burn_subs.render_clean ตัวเดียวกับซับ -> วรรณยุกต์ถูก)
- ซับ burn_subs.py --style clean; ซับ 2 จังหวะ (ประโยคมาก่อน คำสำคัญในแถบชมพูเด้งตาม 0.5 วิ)
- เห็นเพื่อนได้ (เจ้าของช่องยืนยัน 2026-11-15)

ใช้: python3 office/weeks/2026-W47/clip-bangkrachao/build_v2.py [--from shots|fx|subs]
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = "/home/user/marketing-dashboard"
SRC = "/root/.claude/uploads/d151a6a9-7df2-5f3b-8b43-ea4e410e4670"
W0 = "/tmp/claude-0/-home-user-marketing-dashboard/d151a6a9-7df2-5f3b-8b43-ea4e410e4670/scratchpad/bangkrachao"
W = f"{W0}/v2"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f"{W0}/bangkrachao-ep2-v2-preview.mp4"
FONT = f"{REPO}/office/assets/fonts/Prompt-Medium.ttf"
sys.path.insert(0, f"{REPO}/office/editor")
import burn_subs  # noqa: E402  (ใช้ตัววาดซับไทยตัวเดียวกัน)

FPS, VW, VH = 30, 1080, 1920
VF = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"

# (จำนวนเฟรม, ไฟล์, วินาทีเริ่มในต้นฉบับ, ความเร็ว (1=ปกติ, 0=หยุดภาพ), หมายเหตุ)
SHOTS = [
    (30, "6d9bfc01-IMG_4334", 4.0, 1, "เซลฟี่ยิ้มบนจักรยาน + ฮุก"),
    (27, "6b67125e-IMG_4330", 3.0, 1, "สวนพ่นหมอก ธงสี (ซูมกระแทก 'เขียว')"),
    (33, "293088b3-IMG_4370", 1.0, 1, "บึงกว้าง (whip เข้า)"),
    (36, "270fd557-IMG_4333", 5.0, 1, "ถนนต้นไม้"),
    (27, "6b67125e-IMG_4330", 5.2, 1, "สวน บ่อน้ำ ธงสี (ซูมกระแทก)"),
    (30, "293088b3-IMG_4370", 10.0, 1, "บึง + ศาลาริมน้ำ"),
    (57, "c0ea6a86-IMG_4338", 2.0, 1, "ป้ายราคา + วงกลม/ลูกศรชี้ 100"),
    (36, "8d571341-IMG_4345", 9.0, 1, "หัวคายัค คลองต้นจาก (whip เข้า)"),
    (33, "de32490a-IMG_4359", 3.0, 1, "หัวคายัค ใต้ต้นจาก"),
    (18, "d494221f-IMG_4358", 4.4, 1, "หน้าตกใจจริง"),
    (14, "d494221f-IMG_4358", 5.0, 0, "หยุดภาพหน้าตกใจ + ซูมเข้าหน้า + เหงื่อ/เส้นตกใจ"),
    (28, "d53de6ac-IMG_4348", 1.0, 1, "เพื่อนพายด้านหลัง"),
    (27, "bf8552fd-IMG_4332", 0.5, 1, "ห่านเดิน (ตัดเข้าทันที)"),
    (18, "bf8552fd-IMG_4332", 0.6, 1.5, "เล่นซ้ำเร็ว (replay)"),
    (12, "bf8552fd-IMG_4332", 1.5, 0, "หยุดภาพหน้าห่าน + ซูม + โน้ต/หัวใจ"),
    (36, "de32490a-IMG_4359", 0.3, 1, "คลองต้นจาก (whip เข้า) + การ์ด"),
    (36, "cbcf6bb5-IMG_4331", 3.8, 1, "บ่อปลา + การ์ด"),
    (36, "8d571341-IMG_4345", 6.5, 1, "ต้นจากริมคลอง (พื้นเข้ม อ่านการ์ดง่าย) + การ์ด"),
    (36, "cbcf6bb5-IMG_4331", 7.4, 1, "ห่านชมพูเดินริมบ่อ + การ์ด"),
    (36, "d53de6ac-IMG_4348", 0.6, 1, "เซลฟี่คู่เพื่อนในคายัค"),
    (42, "6d9bfc01-IMG_4334", 10.4, 1, "เซลฟี่แลบลิ้น ปิดท้าย"),
]
CUTS = [0]
for _n, *_ in SHOTS:
    CUTS.append(CUTS[-1] + _n)
TOTAL_F = CUTS[-1]


def ts(shot_idx, extra=0.0):
    """เวลา (วิ) ที่ช็อต shot_idx (เริ่ม 1) เริ่ม"""
    return round(CUTS[shot_idx - 1] / FPS + extra, 4)


WHIPS = [3, 8, 16]  # ช็อตที่เข้าแบบ whip

PINK = (255, 143, 189)
PINK_D = (240, 98, 160)
WHITE = (255, 255, 255)
BLUE_L = (186, 228, 255)


def run(cmd):
    print(" ".join(str(c) for c in cmd)[:220], flush=True)
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- 1. ช็อต
def build_shots():
    os.makedirs(W, exist_ok=True)
    parts = []
    for i, (n, f, ss, speed, _) in enumerate(SHOTS, 1):
        out = f"{W}/shot{i:02d}.mp4"
        if speed == 0:  # หยุดภาพ
            vf = VF + f",trim=end_frame=1,tpad=stop_mode=clone:stop={n - 1}"
            dur = 0.5
        else:
            vf = (f"setpts=PTS/{speed}," if speed != 1 else "") + VF
            dur = n / FPS * speed + 0.2
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(ss), "-t", f"{dur:.3f}",
             "-i", f"{SRC}/{f}.MOV", "-vf", vf, "-frames:v", str(n), "-an",
             "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p", out])
        parts.append(out)
    with open(f"{W}/list.txt", "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", f"{W}/list.txt", "-c", "copy", f"{W}/base-raw.mp4"])


# ---------------------------------------------------------------- 2. สติกเกอร์ (PIL)
SS = 4  # วาดใหญ่ 4 เท่าแล้วย่อ ให้ขอบเนียน


def sticker_from_mask(mask, fill, border=10, outline=None):
    """mask (L, ขนาดใหญ่) -> สติกเกอร์ RGBA: สีพื้น + ขอบขาว + เงานุ่ม"""
    bw = border * SS
    pad = bw * 3
    m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
    m.paste(mask, (pad, pad))
    big = m.filter(ImageFilter.MaxFilter(2 * (bw // 2) + 1))
    for _ in range(1):
        big = big.filter(ImageFilter.MaxFilter(2 * (bw // 2) + 1))
    sh = big.filter(ImageFilter.GaussianBlur(bw * 0.8)).point(lambda v: int(v * 0.35))
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", m.size, (150, 40, 100, 255))
    shadow.putalpha(sh)
    out.alpha_composite(shadow, (0, int(bw * 0.5)))
    wl = Image.new("RGBA", m.size, WHITE + (255,))
    wl.putalpha(big)
    out.alpha_composite(wl)
    if outline:
        inner = m.filter(ImageFilter.MinFilter(2 * (SS * 2) + 1))
        ol = Image.new("RGBA", m.size, outline + (255,))
        ol.putalpha(m)
        out.alpha_composite(ol)
        m = inner
    fl = Image.new("RGBA", m.size, fill + (255,))
    fl.putalpha(m)
    out.alpha_composite(fl)
    out = out.resize((out.width // SS, out.height // SS), Image.LANCZOS)
    return out.crop(out.getbbox())


def heart_mask(s):
    S = s * SS
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    pts = []
    for k in range(200):
        t = 2 * math.pi * k / 200
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((S / 2 + x * S / 36, S / 2 - y * S / 36 - S * 0.04))
    d.polygon(pts, fill=255)
    return m


def sparkle_mask(s):
    S = s * SS
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    c = S / 2
    pts = []
    for k in range(8):
        a = math.pi / 4 * k - math.pi / 2
        r = c * 0.98 if k % 2 == 0 else c * 0.22
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=255)
    return m


def drop_mask(s):
    S = s * SS
    m = Image.new("L", (S, int(S * 1.35)), 0)
    d = ImageDraw.Draw(m)
    r = S * 0.42
    cx, cy = S / 2, S * 1.35 - r - S * 0.04
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    d.polygon([(cx, S * 0.02), (cx - r * 0.93, cy - r * 0.3), (cx + r * 0.93, cy - r * 0.3)], fill=255)
    return m


def lines_mask(s, side=-1):
    """เส้นตกใจ 3 เส้น เรียงเป็นพัด (side=-1 ชี้ซ้าย)"""
    S = s * SS
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    w = int(S * 0.11)
    ox, oy = (S * 0.95, S * 0.95) if side < 0 else (S * 0.05, S * 0.95)
    for a in (200, 235, 270) if side < 0 else (340, 305, 270):
        r0, r1 = S * 0.35, S * 0.9
        ar = math.radians(a)
        d.line([(ox + r0 * math.cos(ar), oy + r0 * math.sin(ar)),
                (ox + r1 * math.cos(ar), oy + r1 * math.sin(ar))], fill=255, width=w)
        for r in (r0, r1):
            x, y = ox + r * math.cos(ar), oy + r * math.sin(ar)
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=255)
    return m


def ring_mask(w_, h_, th=16):
    m = Image.new("L", (w_ * SS, h_ * SS), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([th * SS, th * SS, (w_ - th) * SS, (h_ - th) * SS], outline=255, width=th * SS)
    return m


def arrow_mask(s):
    """ลูกศรชี้ลงซ้าย (ปลายอยู่มุมล่างซ้าย)"""
    S = s * SS
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    w = int(S * 0.13)
    tip = (S * 0.12, S * 0.88)
    d.line([(S * 0.9, S * 0.1), (S * 0.3, S * 0.7)], fill=255, width=w)
    d.polygon([tip, (S * 0.12, S * 0.42), (S * 0.58, S * 0.88)], fill=255)
    return m


def note_mask(s):
    S = s * SS
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    w = int(S * 0.1)
    for hx in (0.28, 0.75):
        cx, cy = S * hx, S * 0.78
        d.ellipse([cx - S * 0.17, cy - S * 0.12, cx + S * 0.13, cy + S * 0.12], fill=255)
        d.rectangle([cx + S * 0.13 - w, S * 0.15, cx + S * 0.13, cy], fill=255)
    d.polygon([(S * 0.41 - w, S * 0.12), (S * 0.88, S * 0.02), (S * 0.88, S * 0.2),
               (S * 0.41 - w, S * 0.3)], fill=255)
    return m


def make_stickers():
    st = {
        "heart": sticker_from_mask(heart_mask(150), PINK),
        "heart_s": sticker_from_mask(heart_mask(95), PINK, border=8),
        "spark": sticker_from_mask(sparkle_mask(120), WHITE, border=7, outline=PINK),
        "spark_s": sticker_from_mask(sparkle_mask(80), (255, 225, 238), border=6, outline=PINK),
        "drop": sticker_from_mask(drop_mask(120), BLUE_L, border=9),
        "lines": sticker_from_mask(lines_mask(185, -1), PINK_D, border=8),
        "ring": sticker_from_mask(ring_mask(300, 190, 13), PINK_D, border=6),
        "arrow": sticker_from_mask(arrow_mask(170), PINK_D, border=9),
        "note": sticker_from_mask(note_mask(120), PINK, border=8),
    }
    os.makedirs(f"{W}/stickers", exist_ok=True)
    for k, v in st.items():
        v.save(f"{W}/stickers/{k}.png")
    return st


# (ชื่อสติกเกอร์, เวลาเริ่ม, เวลาจบ, x กลาง, y กลาง, ท่าขยับ) — ตำแหน่งวัดจากเฟรมจริง
# (เช็กแล้วไม่ทับหน้า/ฮุก/ตัวเลขบนป้าย)
def sticker_plan():
    return [
        # เปิด: หัวใจข้างหน้า + ดาววิ้ง (ฮุกอยู่ด้านบน สติกเกอร์จึงอยู่ข้าง/ล่างหน้า)
        ("heart", 0.15, ts(2) - 0.02, 930, 1000, "bob"),
        ("spark", 0.30, ts(2) - 0.02, 115, 1160, "spin"),
        ("spark_s", 0.45, ts(2) - 0.02, 965, 1330, "spin"),
        # ป้ายราคา: วงกลมรอบ "100/1คน" + ลูกศรจากขอบป้าย
        ("ring", ts(7, 0.5), ts(8) - 0.02, 868, 1135, "drift"),
        ("arrow", ts(7, 0.62), ts(8) - 0.02, 1020, 1000, "poke"),
        # หน้าตกใจ (หยุดภาพ + ซูม): เส้นตกใจข้างหัว + หยดเหงื่อ
        ("lines", ts(11, 0.03), ts(12) - 0.01, 500, 840, "shake"),
        ("drop", ts(11, 0.06), ts(12) - 0.01, 1030, 960, "drop"),
        # ห่าน: โน้ตเพลงตอนเล่นซ้ำ + หัวใจตอนหยุดภาพ
        ("note", ts(14, 0.05), ts(16) - 0.02, 880, 400, "sway"),
        ("heart_s", ts(15, 0.02), ts(16) - 0.02, 560, 440, "sway"),
        # ปิดท้าย: หัวใจเล็กตอนคำว่า "ใคร" เด้ง
        ("heart_s", ts(20, 0.5), ts(22) - 0.05, 960, 600, "sway"),
    ]


# ซูม: (เวลาเริ่ม, เวลาจบ, ขนาด, x, y, ชนิด)  punch = กระแทกแล้วคลาย, hold = ซูมเข้าค้าง
ZOOMS = [
    (ts(2), ts(3), 0.07, 540, 960, "punch"),        # "เขียว"
    (ts(5), ts(6), 0.07, 540, 960, "punch"),        # บางกะเจ้า
    (ts(7, 0.5), ts(8), 0.07, 878, 1122, "punch"),  # 100 บาท
    (ts(11), ts(12), 0.25, 750, 1240, "hold"),      # หน้าตกใจ หยุดภาพ
    (ts(14), ts(15), 0.06, 720, 700, "punch"),      # replay ห่าน
    (ts(15), ts(16), 0.20, 720, 735, "hold"),       # หน้าห่าน หยุดภาพ
    (ts(20), ts(21), 0.06, 840, 1110, "punch"),     # เซลฟี่คู่
    (ts(21), ts(22), 0.07, 300, 900, "punch"),      # แลบลิ้น
]


def pop_scale(age, left):
    """เด้งเข้า: 0 -> ~1.18 -> 1.0 ใน 0.2 วิ, หดออก 0.1 วิสุดท้าย"""
    if age < 0:
        return 0
    s = 1.0
    if age < 0.2:
        u = age / 0.2
        s = 1 + 2.9 * (u - 1) ** 3 + 1.9 * (u - 1) ** 2  # easeOutBack
    if left < 0.1:
        s *= max(0, left / 0.1)
    return s


def zoom_at(t):
    for t0, t1, amp, cx, cy, kind in ZOOMS:
        if t0 <= t < t1:
            age = t - t0
            if kind == "punch":
                return 1 + amp * math.exp(-age / 0.18), cx, cy
            return 1 + amp * min(1, age / 0.1) ** 0.5, cx, cy
    return 1.0, 540, 960


def hblur(arr, k):
    """เบลอแนวนอน (motion blur) ด้วย cumsum"""
    if k < 2:
        return arr
    a = arr.astype(np.float32)
    c = np.cumsum(np.pad(a, ((0, 0), (k, 0), (0, 0)), mode="edge"), axis=1)
    return ((c[:, k:] - c[:, :-k]) / k).clip(0, 255).astype(np.uint8)


def hook_text():
    return json.load(open(f"{HERE}/subs.json"))[0]["text"]


def build_fx():
    st = make_stickers()
    st["arrow"] = st["arrow"].resize((st["arrow"].width * 2 // 3, st["arrow"].height * 2 // 3), Image.LANCZOS)
    st["ring"] = st["ring"].resize((265, 158), Image.LANCZOS)
    plan = sticker_plan()
    hook_png = f"{W}/hook.png"
    burn_subs.render_clean(hook_text(), FONT, 112, hook_png)
    hook = Image.open(hook_png).convert("RGBA")
    whip_f = [CUTS[s - 1] for s in WHIPS]

    dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", f"{W}/base-raw.mp4",
                            "-vf", "format=rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "15", f"{W}/base-fx.mp4"],
                           stdin=subprocess.PIPE)
    fsz = VW * VH * 3
    for i in range(TOTAL_F):
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            raise SystemExit(f"short read at frame {i}")
        t = i / FPS
        img = Image.fromarray(np.frombuffer(buf, np.uint8).reshape(VH, VW, 3))
        # ซูม (ซูมรอบจุด cx,cy -> จุดนั้นอยู่ที่เดิม กรอบไม่หลุดภาพ)
        z, cx, cy = zoom_at(t)
        if z > 1.001:
            x0, y0 = cx - cx / z, cy - cy / z
            img = img.resize((VW, VH), Image.BILINEAR, box=(x0, y0, x0 + VW / z, y0 + VH / z))
        # whip pan: 3 เฟรมก่อน + 3 เฟรมหลังรอยต่อ เลื่อน + เบลอแนวนอน
        for wf in whip_f:
            k = i - wf
            if -3 <= k <= 2:
                shift = {-3: -0.06, -2: -0.2, -1: -0.45, 0: 0.4, 1: 0.15, 2: 0.04}[k]
                blur = {-3: 20, -2: 60, -1: 130, 0: 130, 1: 50, 2: 14}[k]
                a = np.roll(np.asarray(img), int(shift * VW), axis=1)
                img = Image.fromarray(hblur(a, blur))
        img = img.convert("RGBA")
        # ฮุกเปิด: ใหญ่ ด้านบน เด้งเข้า (หน้าอยู่กลางจอ)
        if t < ts(3):
            hs = pop_scale(t + 0.07, ts(3) - t)  # เฟรมแรกเห็นฮุกแล้ว
            if t > 0.25:
                hs *= 1 + 0.02 * math.sin((t - 0.25) * 2 * math.pi * 2.2)
            hw, hh = int(hook.width * hs), int(hook.height * hs)
            if hw > 4 and hh > 4:
                h2 = hook.resize((hw, hh), Image.LANCZOS)
                img.alpha_composite(h2, (VW // 2 - hw // 2, 360 - hh // 2))
        # สติกเกอร์
        for name, t0, t1, x, y, mode in plan:
            if not (t0 <= t < t1):
                continue
            age, left = t - t0, t1 - t
            s = pop_scale(age, left)
            if s <= 0.02:
                continue
            spr, ang = st[name], 0
            if mode == "bob":
                y += 12 * math.sin(age * 2 * math.pi * 1.8)
                ang = 8 * math.sin(age * 2 * math.pi * 1.8)
            elif mode == "spin":
                ang = -60 * age
                s *= 1 + 0.12 * math.sin(age * 2 * math.pi * 2.5)
            elif mode == "poke":  # ลูกศรจิ้มเข้า-ออก
                d = 14 * abs(math.sin(age * 2 * math.pi * 1.6))
                x, y = x - d, y + d
            elif mode == "drift":  # กล้องแพนช้า ๆ -> วงกลมเลื่อนตามป้าย
                u = age / (t1 - t0)
                x, y = x - 32 * u, y + 10 * u
            elif mode == "drop":
                y += min(age, 0.45) * 90
            elif mode == "shake":
                x += 7 * math.sin(age * 70)
            elif mode == "sway":
                y -= 10 * math.sin(age * 2 * math.pi * 1.5)
                ang = 12 * math.sin(age * 2 * math.pi * 1.5)
            sw, sh = max(2, int(spr.width * s)), max(2, int(spr.height * s))
            s2 = spr.resize((sw, sh), Image.LANCZOS)
            if ang:
                s2 = s2.rotate(ang, Image.BICUBIC, expand=True)
            img.alpha_composite(s2, (int(x - s2.width / 2), int(y - s2.height / 2)))
        enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()


# ---------------------------------------------------------------- 3. ซับ (burn_subs.py --mute)
def strip(text):
    return text.replace("[", "").replace("]", "")


def build_subs():
    subs = json.load(open(f"{HERE}/subs.json"))
    t_end = TOTAL_F / FPS
    # (ท่อน, เริ่ม, จบ, เวลาที่คำสำคัญเด้ง หรือ None, y)
    timing = [
        (1, ts(3), ts(5), ts(3, 0.5), None),
        (2, ts(5), ts(7), None, None),
        (3, ts(7), ts(8), ts(7, 0.5), None),
        (4, ts(8), ts(10), None, None),
        (5, ts(10), ts(13), ts(11), 250),       # หน้าอยู่ครึ่งล่าง -> ซับบน; คำเด้งตอนหยุดภาพ
        (6, ts(13), ts(16), ts(13, 0.5), None),
        (7, ts(16), ts(20), None, None),
        (8, ts(20), t_end, ts(20, 0.5), 170),   # หน้าคน 2 คนกินกลาง-ล่างจอ -> ซับบน
    ]
    out = []
    for k, t0, t1, tk, y in timing:
        s = {"text": subs[k]["text"]}
        if k == 7:  # การ์ดข้อมูล: ข้อความเดิมครบทุกตัว ตัดบรรทัดเหมือน v1
            s["text"] = ("บางกะเจ้า\nพระประแดง สมุทรปราการ\nคายัค 100 บาท/คน\nเรือไม้ 500 บาท/5 คน\n"
                         "วาดภาพ 150 บาท/เฟรม\nราคาตามป้าย ณ พ.ค. 2026\n[เซฟไว้] ไปวันหยุด")
            s["size"] = 68
        if y is not None:
            s["y"] = y
        if tk:  # ซับ 2 จังหวะ: ประโยคเปล่ามาก่อน แล้วแถบชมพูเด้งที่คำสำคัญ
            a = dict(s, text=strip(s["text"]), start=t0, end=tk, fade_out=0)
            b = dict(s, start=tk, end=t1, fade_in=0, rise=False)
            if y is None:  # ให้ 2 จังหวะอยู่ระดับเดียวกันพอดี
                a["rise"] = True
            out += [a, b]
        else:
            out.append(dict(s, start=t0, end=t1))
    json.dump(out, open(f"{W}/subs-v2.json", "w"), ensure_ascii=False, indent=1)
    run(["python3", f"{REPO}/office/editor/burn_subs.py", "--video", f"{W}/base-fx.mp4",
         "--subs", f"{W}/subs-v2.json", "--out", OUT, "--mute", "--style", "clean"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default="shots", choices=["shots", "fx", "subs"])
    a = ap.parse_args()
    order = ["shots", "fx", "subs"]
    fns = [build_shots, build_fx, build_subs]
    for name, fn in list(zip(order, fns))[order.index(a.start):]:
        print("==", name, flush=True)
        fn()
    print("total", TOTAL_F / FPS, "s ->", OUT)


if __name__ == "__main__":
    main()
