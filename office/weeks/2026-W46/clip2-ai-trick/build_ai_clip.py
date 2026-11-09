"""ทริค AI EP.1: ฟุตเทจดิบ → คลิปเสร็จ (ร่าง ไม่มีเสียง) — compositor แบบเฟรมต่อเฟรม"""
import json
import math
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, "/home/user/marketing-dashboard/office/editor")
import emoji_quiz as q  # ใช้ฟอนต์/ฟังก์ชัน pill, text_layer, ease, paste_center

W, H, FPS = 1080, 1920, 30
E = "/tmp/claude-0/-home-user-marketing-dashboard/4fb0ae1d-39b3-5573-9ed2-8168ea5e1189/scratchpad/edit/"
U = "/root/.claude/uploads/4fb0ae1d-39b3-5573-9ed2-8168ea5e1189/"
RAW = [U + "c23d24fe-IMG_5942.MOV", U + "8b5f1a8e-IMG_5943.MOV", U + "92778cc4-IMG_5944.MOV",
       U + "0ffb9241-IMG_5948.MOV", U + "54ff146a-v14044g50000db512pvog65phgdopbjg.MP4"]
FINAL = E + "moo-yoo-v16-newsubs.mp4"
CLEAN = E + "base15-fx.mp4"
V1 = E + "moo-yoo-preview.mp4"
V8 = E + "moo-yoo-preview-v8-sparkle.mp4"
PINK, PINK_BG, PINK_FG, DARK, YELLOW = (255, 105, 180), (255, 214, 231), (122, 14, 59), (35, 26, 40), (255, 211, 77)
SEG = [("split", 3.0), ("grid", 3.5), ("checks", 3.5), ("photo", 3.5), ("versions", 4.0), ("outro", 4.0)]


def frames(path, ss, dur, w, h, n=None):
    n = n or int(round(dur * FPS))
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(ss), "-t", str(dur + 0.5), "-i", path,
           "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    sz = w * h * 3
    out = [Image.frombytes("RGB", (w, h), raw[i * sz:(i + 1) * sz]) for i in range(len(raw) // sz)]
    while len(out) < n:
        out.append(out[-1])
    return out[:n]


def rounded(img, r=28, border=0, col=DARK):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    out = Image.new("RGBA", (w + 2 * border, h + 2 * border), (0, 0, 0, 0))
    if border:
        ImageDraw.Draw(out).rounded_rectangle((0, 0, w + 2 * border - 1, h + 2 * border - 1), radius=r + border, fill=col)
    out.paste(img.convert("RGBA"), (border, border), m)
    return out


def bg():
    top, bot = np.array([36, 24, 46]), np.array([74, 30, 70])
    g = (top + (bot - top) * np.linspace(0, 1, H)[:, None]).astype("uint8")
    im = Image.fromarray(np.repeat(g[:, None, :], W, axis=1), "RGB").convert("RGBA")
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((80, 500, 1000, 1300), fill=(255, 105, 180, 90))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(140)))
    return im


BG = bg()


def header(im, title, kicker="ทริค AI · EP.1"):
    d = ImageDraw.Draw(im)
    q.pill(d, W / 2, 200, kicker, q.F("Prompt-Medium.ttf", 34))
    tf = q.fit_font(title, "Prompt-SemiBold.ttf", 82, 980)
    d.text((W / 2, 270), title, font=tf, fill="white", anchor="mt")


def label(im, cx, y, text, bg_=PINK_BG, fg=PINK_FG, size=36):
    q.pill(ImageDraw.Draw(im), cx, y, text, q.F("Prompt-SemiBold.ttf", size), bg=bg_, fg=fg, padx=26, pady=6)


def check_icon(size=56):
    ic = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(ic)
    d.ellipse((0, 0, size - 1, size - 1), fill=(46, 170, 96))
    w = max(4, size // 9)
    d.line([(size * 0.27, size * 0.52), (size * 0.44, size * 0.69), (size * 0.74, size * 0.34)], fill="white", width=w,
           joint="curve")
    return ic


def main(out):
    ff = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i",
                           "anullsrc=r=48000:cl=stereo", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    starts, t0 = {}, 0.0
    for name, dur in SEG:
        starts[name] = t0
        n = int(round(dur * FPS))
        if name == "split":  # ดิบ vs เสร็จ
            L = frames(RAW[0], 0.5, dur, 360, 640)
            R = frames(FINAL, 6.2, dur, 360, 640)
            for i in range(n):
                t = i / FPS
                im = BG.copy()
                header(im, "ฟุตเทจดิบ → คลิปเสร็จ")
                k = q.ease(t / 0.3)
                lf = ImageEnhance.Color(L[i]).enhance(0.6)
                q.paste_center(im, rounded(lf, border=6, col=(90, 80, 100)), W / 2 - 200, 760, 0.9 + 0.1 * k, k)
                q.paste_center(im, rounded(R[i], border=6, col=PINK), W / 2 + 200, 760, 0.9 + 0.1 * k, k)
                label(im, W / 2 - 200, 400, "ฟุตเทจดิบ", (230, 225, 235), DARK)
                label(im, W / 2 + 200, 400, "AI ตัดแล้ว", PINK_BG, PINK_FG)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "grid":  # ของที่มี: 5 วิดีโอ + 3 รูป
            tiles = [frames(p, 0.3, dur, 190, 338) for p in RAW]
            for ph in ["p8430.jpg", "photo.jpg", "p8260.jpg"]:
                st = ImageOps.fit(Image.open(E + ph).convert("RGB"), (190, 338), Image.LANCZOS)
                tiles.append([st] * n)
            for i in range(n):
                t = i / FPS
                im = BG.copy()
                header(im, "ของที่มีแค่นี้")
                for j, tl in enumerate(tiles):
                    r, c = divmod(j, 4)
                    cx = 195 + c * 230
                    cy = 590 + r * 360
                    kk = q.ease((t - 0.08 * j) / 0.25)
                    q.paste_center(im, rounded(tl[i], 22, 4, PINK if j >= 5 else (200, 190, 210)), cx, cy, 0.85 + 0.15 * kk, kk)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "checks":  # คลิปเสร็จเต็มจอ + เช็กลิสต์
            F = frames(FINAL, 2.2, dur, W, H)
            items = ["เลือกช็อตที่ดีที่สุด", "ใส่ซับไทย", "จัดเสียงพากย์ให้ตรงภาพ"]
            for i in range(n):
                t = i / FPS
                im = F[i].convert("RGBA")
                sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rectangle((0, 0, W, 760), fill=(20, 12, 24, 120))
                im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
                for j, it in enumerate(items):
                    kk = q.ease((t - 0.35 - 0.8 * j) / 0.25)
                    if kk <= 0:
                        continue
                    lay = Image.new("RGBA", (W, 120), (0, 0, 0, 0))
                    q.pill(ImageDraw.Draw(lay), W / 2 + 30, 10, it, q.F("Prompt-SemiBold.ttf", 52), bg=(255, 255, 255), fg=DARK,
                           padx=40, pady=12)
                    tw = ImageDraw.Draw(lay).textlength(it, font=q.F("Prompt-SemiBold.ttf", 52))
                    lay.alpha_composite(check_icon(64), (int(W / 2 + 30 - tw / 2 - 40 - 74), 22))
                    q.paste_center(im, lay, W / 2, 300 + 130 * j, 0.85 + 0.15 * kk, kk)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "photo":  # รูปนิ่ง → ซูม + แสงฟุ้ง + วิ้ง
            st = ImageOps.fit(Image.open(E + "photo.jpg").convert("RGB"), (360, 640), Image.LANCZOS, centering=(0.6, 0.45))
            R = frames(CLEAN, 14.2, 2.5, 360, 640, n)
            for i in range(n):
                t = i / FPS
                im = BG.copy()
                header(im, "รูปนิ่ง ก็ขยับได้")
                q.paste_center(im, rounded(ImageEnhance.Color(st).enhance(0.7), border=6, col=(90, 80, 100)), W / 2 - 200, 760)
                q.paste_center(im, rounded(R[i], border=6, col=PINK), W / 2 + 200, 760)
                label(im, W / 2 - 200, 400, "รูปนิ่ง", (230, 225, 235), DARK)
                label(im, W / 2 + 200, 400, "ซูม + แสงฟุ้ง + วิ้ง", PINK_BG, PINK_FG, 32)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "versions":  # แก้ไป 16 เวอร์ชัน
            shots = [(V1, 11.5, "v1 · วรรณยุกต์หาย", True), (V8, 7.0, "v8 · วิ้งเยอะไป", False),
                     (FINAL, 9.5, "v16 · ใช้ได้แล้ว!", False)]
            imgs = [frames(p, s, 0.1, 440, 782, 1)[0] for p, s, _, _ in shots]
            per = dur / 3
            for i in range(n):
                t = i / FPS
                j = min(2, int(t // per))
                tl = t - j * per
                im = BG.copy()
                header(im, "แก้ไป 16 เวอร์ชัน!")
                fr = imgs[j].copy()
                if shots[j][3]:  # วงแดงตรงซับที่วรรณยุกต์หาย
                    dd = ImageDraw.Draw(fr)
                    dd.ellipse((90, 470, 350, 600), outline=(255, 60, 60), width=8)
                kk = q.ease(tl / 0.2)
                col = (120, 200, 140) if j == 2 else (255, 90, 90)
                q.paste_center(im, rounded(fr, border=6, col=col), W / 2, 830, 0.9 + 0.1 * kk, kk)
                label(im, W / 2, 1238, shots[j][2], YELLOW if j == 2 else (255, 225, 225), DARK, 40)
                # ตัวนับเวอร์ชัน
                vnum = 1 + int(15 * min(1, t / (dur - 0.4)))
                label(im, W / 2, 418, f"เวอร์ชัน {vnum}/16", (255, 255, 255), DARK, 34)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "outro":  # คำถาม + ปุ่มติดตาม
            F = [f.filter(ImageFilter.GaussianBlur(22)) for f in frames(FINAL, 11.0, dur, W, H)]
            opts = ["เลือกช็อต", "ซับไทย", "แสงฟุ้ง + วิ้ง"]
            for i in range(n):
                t = i / FPS
                im = F[i].convert("RGBA")
                dim = Image.new("RGBA", (W, H), (20, 12, 24, 150))
                im.alpha_composite(dim)
                d = ImageDraw.Draw(im)
                k = q.ease(t / 0.3)
                q.paste_center(im, q.text_layer([("อยากให้สอนขั้นไหน?", q.F("Prompt-SemiBold.ttf", 76), (255, 255, 255))]),
                               W / 2, 470, 0.9 + 0.1 * k, k)
                for j, o in enumerate(opts):
                    kk = q.ease((t - 0.3 - 0.15 * j) / 0.25)
                    if kk > 0:
                        lay = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
                        q.pill(ImageDraw.Draw(lay), W / 2, 10, f"{j + 1}. {o}", q.F("Prompt-SemiBold.ttf", 48),
                               bg=PINK_BG, fg=PINK_FG, padx=40, pady=10)
                        q.paste_center(im, lay, W / 2, 610 + 110 * j, 1.0, kk)
                q.paste_center(im, q.text_layer([("เมนต์ตัวเลขบอกได้เลย", q.F("Prompt-Medium.ttf", 40), (255, 255, 255))]),
                               W / 2, 960, 1.0, q.ease((t - 0.8) / 0.25))
                if t > 1.0:
                    kk = q.ease((t - 1.0) / 0.25)
                    bump = 1 + 0.06 * math.sin(t * 7)
                    btn = Image.new("RGBA", (620, 150), (0, 0, 0, 0))
                    bd = ImageDraw.Draw(btn)
                    bd.rounded_rectangle((8, 12, 612, 142), radius=65, fill=DARK)
                    bd.rounded_rectangle((0, 0, 604, 130), radius=65, fill=(254, 44, 85), outline=DARK, width=6)
                    bd.text((302, 65), "+ ติดตาม", font=q.F("Prompt-SemiBold.ttf", 64), fill="white", anchor="mm")
                    q.paste_center(im, btn, W / 2, 1130, kk * bump, kk)
                    q.paste_center(im, q.text_layer([("EP หน้าสอนเลย!", q.F("Prompt-SemiBold.ttf", 46), (255, 255, 255))]),
                                   W / 2, 1250, 1.0, kk)
                ff.stdin.write(im.convert("RGB").tobytes())
        t0 += dur
    ff.stdin.close()
    ff.wait()
    json.dump(starts, open("seg_starts.json", "w"))


if __name__ == "__main__":
    main(sys.argv[1])
