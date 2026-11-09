"""ทริค AI EP.1 v2 (ปรับให้แมส): เปิดเต็มจอปาดดิบ→เสร็จ, แชทจริง, กระพริบ 16 เวอร์ชัน, จบวนกลับต้น (~17.5 วิ)"""
import math
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, "/home/user/marketing-dashboard/office/editor")
sys.path.insert(0, ".")
import emoji_quiz as q
from build_ai_clip import (BG, CLEAN, DARK, E, FINAL, FPS, H, PINK, PINK_BG, PINK_FG, RAW, W, YELLOW,
                           check_icon, frames, header, label, rounded)

U = "/root/.claude/uploads/4fb0ae1d-39b3-5573-9ed2-8168ea5e1189/"
CHAT = U + "896998e8-ScreenRecording_11-09-2569_21-33-49_1.mp4"
VERS = ["moo-yoo-preview.mp4", "moo-yoo-preview-v2.mp4", "moo-yoo-preview-v3.mp4", "moo-yoo-preview-v4-nomusic.mp4",
        "moo-yoo-preview-v5-itim.mp4", "moo-yoo-preview-v6.mp4", "moo-yoo-preview-v7.mp4",
        "moo-yoo-preview-v8-sparkle.mp4", "moo-yoo-preview-v9-glow.mp4", "moo-yoo-preview-v10.mp4",
        "moo-yoo-preview-v11.mp4", "moo-yoo-v12-voice.mp4", "moo-yoo-v13.mp4", "moo-yoo-v14.mp4", "moo-yoo-v15.mp4",
        "moo-yoo-v16-newsubs.mp4"]
SEG = [("hook", 2.5), ("grid", 2.0), ("chat", 2.0), ("checks", 2.5), ("photo", 2.0), ("versions", 3.0), ("outro", 3.5)]


def frames_fast(path, ss, dur_src, w, h, n):
    """อ่านช่วง dur_src วินาทีแล้วบีบให้เหลือ n เฟรม (เร่งความเร็ว)"""
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(ss), "-t", str(dur_src), "-i", path,
           "-vf", f"setpts=PTS*{n / (dur_src * FPS):.4f},fps={FPS},scale={w}:{h}:force_original_aspect_ratio=decrease,"
                  f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x101010",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    sz = w * h * 3
    out = [Image.frombytes("RGB", (w, h), raw[i * sz:(i + 1) * sz]) for i in range(len(raw) // sz)]
    while len(out) < n:
        out.append(out[-1])
    return out[:n]


def make_sfx(total):
    import wave
    import numpy as np
    sr = 48000
    mix = np.zeros(int(total * sr))
    n = int(0.45 * sr)
    tt = np.arange(n) / sr
    noise = np.random.default_rng(1).normal(0, 1, n)
    k = np.exp(-((tt - 0.12) ** 2) / 0.006)  # วูบขึ้นแล้วหาย
    sweep = np.convolve(noise, np.ones(30) / 30, "same") * k
    s0 = int(0.88 * sr)
    mix[s0:s0 + n] += 0.5 * sweep / (np.abs(sweep).max() + 1e-9)
    tick_t = np.arange(int(0.05 * sr)) / sr
    tick = np.sin(2 * np.pi * 1800 * tick_t) * np.exp(-tick_t * 70)
    for x in [0.2, 0.4, 0.6, 0.8]:  # ติ๊กตอนตัดสลับฟุตเทจ
        a = int(x * sr)
        mix[a:a + len(tick)] += 0.18 * tick
    pcm = (np.stack([mix, mix], 1) * 32767 * 0.9).astype("<i2")
    with wave.open("sfx.wav", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main(out):
    make_sfx(sum(d for _, d in SEG))
    ff = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "sfx.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    raw_full = frames(RAW[0], 0.6, 0.1, W, H, 1)  # เฟรมแรกของคลิป (ใช้ตอนจบให้วนเนียน)
    first_raw = raw_full[0]  # ภาพดิบสีจริง ไม่ปรับให้หม่น
    for name, dur in SEG:
        n = int(round(dur * FPS))
        if name == "hook":  # ตัดสลับฟุตเทจดิบเร็ว ๆ → แฟลช → ซูมกระแทกช็อตสวยสุด + หัวข้อใหญ่
            raws = [frames(p, 0.6, 0.25, W, H, 6) for p in RAW]
            best = frames(CLEAN, 0.2, 1.5, W, H)
            hf1, hf2 = q.F("Prompt-SemiBold.ttf", 58), q.F("Prompt-SemiBold.ttf", 86)
            for i in range(n):
                t = i / FPS
                if t < 1.0:
                    j = min(4, int(t // 0.2))
                    im = raws[j][min(5, int((t - j * 0.2) * FPS))].convert("RGBA")
                    label(im, W / 2, 1440, "ฟุตเทจดิบจากมือถือ", (235, 230, 240), DARK, 44)
                else:
                    tt = t - 1.0
                    fr = best[min(len(best) - 1, int(tt * FPS))]
                    z = 1.14 - 0.14 * q.ease(tt / 0.35)  # ซูมกระแทก
                    w2, h2 = int(W * z), int(H * z)
                    big = fr.resize((w2, h2), Image.LANCZOS)
                    im = big.crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H)).convert("RGBA")
                    if tt < 0.12:  # แฟลช
                        im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - tt / 0.12)))))
                    label(im, W / 2, 1440, "AI ตัดแล้ว", PINK_BG, PINK_FG, 44)
                # กล่องหัวข้อใหญ่ ตลอดช่วงฮุก
                d = ImageDraw.Draw(im)
                d.rounded_rectangle((70, 170, 1010, 420), radius=36, fill=DARK)
                d.text((W / 2, 200), "คลิปมือถือธรรมดา", font=hf1, fill=(255, 255, 255), anchor="mt")
                d.text((W / 2, 285), "AI ตัดเป็นแบบนี้!", font=hf2, fill=YELLOW, anchor="mt")
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "grid":
            tiles = [frames(p, 0.3, dur, 176, 313) for p in RAW]
            for ph in ["p8430.jpg", "photo.jpg", "p8260.jpg"]:
                st = ImageOps.fit(Image.open(E + ph).convert("RGB"), (176, 313), Image.LANCZOS)
                tiles.append([st] * n)
            for i in range(n):
                t = i / FPS
                im = BG.copy()
                header(im, "ของที่มีแค่นี้")
                for j, tl in enumerate(tiles):
                    r, c = divmod(j, 4)
                    kk = q.ease((t - 0.05 * j) / 0.2)
                    q.paste_center(im, rounded(tl[i], 22, 4, PINK if j >= 5 else (200, 190, 210)),
                                   210 + c * 220, 590 + r * 325, 0.85 + 0.15 * kk, kk)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "chat":  # อัดหน้าจอแชทจริง ในกรอบมือถือ (เร่ง 2.5 เท่า)
            ch = frames_fast(CHAT, 1.0, 5.0, 300, 652, n)
            for i in range(n):
                t = i / FPS
                im = BG.copy()
                header(im, "ส่งไฟล์ในแชท สั่งงานเลย")
                k = q.ease(t / 0.25)
                q.paste_center(im, rounded(ch[i], 40, 10, DARK), W / 2, 765, 0.9 + 0.1 * k, k)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "checks":
            F = frames(FINAL, 2.2, dur, W, H)
            items = ["เลือกช็อตที่ดีที่สุด", "ใส่ซับไทย", "จัดเสียงพากย์ให้ตรงภาพ"]
            f52 = q.F("Prompt-SemiBold.ttf", 52)
            for i in range(n):
                t = i / FPS
                im = F[i].convert("RGBA")
                sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rectangle((0, 0, W, 760), fill=(20, 12, 24, 120))
                im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
                for j, it in enumerate(items):
                    kk = q.ease((t - 0.2 - 0.55 * j) / 0.2)
                    if kk <= 0:
                        continue
                    lay = Image.new("RGBA", (W, 120), (0, 0, 0, 0))
                    q.pill(ImageDraw.Draw(lay), W / 2 + 30, 10, it, f52, bg=(255, 255, 255), fg=DARK, padx=40, pady=12)
                    tw = ImageDraw.Draw(lay).textlength(it, font=f52)
                    lay.alpha_composite(check_icon(64), (int(W / 2 + 30 - tw / 2 - 40 - 74), 22))
                    q.paste_center(im, lay, W / 2, 300 + 150 * j, 0.85 + 0.15 * kk, kk)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "photo":
            st = ImageOps.fit(Image.open(E + "photo.jpg").convert("RGB"), (340, 604), Image.LANCZOS, centering=(0.6, 0.45))
            R = frames(CLEAN, 14.2, 2.0, 340, 604, n)
            for i in range(n):
                im = BG.copy()
                header(im, "รูปนิ่ง ก็ขยับได้")
                q.paste_center(im, rounded(ImageEnhance.Color(st).enhance(0.7), border=6, col=(90, 80, 100)), W / 2 - 190, 780)
                q.paste_center(im, rounded(R[i], border=6, col=PINK), W / 2 + 190, 780)
                label(im, W / 2 - 190, 450, "รูปนิ่ง", (230, 225, 235), DARK)
                label(im, W / 2 + 190, 450, "ซูม + แสงฟุ้ง + วิ้ง", PINK_BG, PINK_FG, 32)
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "versions":  # กระพริบ 16 เวอร์ชัน แล้วหยุดที่ v16
            shots = [frames(E + v, 9.5, 0.1, 340, 604, 1)[0] for v in VERS]
            flash = 0.11
            for i in range(n):
                t = i / FPS
                j = min(15, int(t // flash))
                im = BG.copy()
                header(im, "แก้ไป 16 เวอร์ชัน!")
                col = (120, 200, 140) if j == 15 else (255, 255, 255)
                bump = 1.06 - 0.06 * q.ease((t - 15 * flash) / 0.25) if j == 15 else 1.0
                q.paste_center(im, rounded(shots[j], border=6, col=col), W / 2, 780, bump)
                label(im, W / 2, 424, f"เวอร์ชัน {j + 1}/16", YELLOW if j == 15 else (255, 255, 255), DARK, 40)
                if j == 15:
                    q.paste_center(im, check_icon(110), W / 2 + 180, 500, q.ease((t - 15 * flash) / 0.2))
                ff.stdin.write(im.convert("RGB").tobytes())
        elif name == "outro":
            F = [f.filter(ImageFilter.GaussianBlur(22)) for f in frames(FINAL, 11.0, dur, W, H)]
            opts = ["เลือกช็อต", "ซับไทย", "แสงฟุ้ง + วิ้ง"]
            for i in range(n):
                t = i / FPS
                if t > dur - 0.4:  # 0.4 วิสุดท้าย = เฟรมแรกของคลิป (ดูวนต่อเนียน)
                    ff.stdin.write(first_raw.convert("RGB").tobytes())
                    continue
                im = F[i].convert("RGBA")
                im.alpha_composite(Image.new("RGBA", (W, H), (20, 12, 24, 150)))
                k = q.ease(t / 0.3)
                q.paste_center(im, q.text_layer([("อยากให้สอนขั้นไหน?", q.F("Prompt-SemiBold.ttf", 76), (255, 255, 255))]),
                               W / 2, 470, 0.9 + 0.1 * k, k)
                for j, o in enumerate(opts):
                    kk = q.ease((t - 0.25 - 0.12 * j) / 0.2)
                    if kk > 0:
                        lay = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
                        q.pill(ImageDraw.Draw(lay), W / 2, 10, f"{j + 1}. {o}", q.F("Prompt-SemiBold.ttf", 48),
                               bg=PINK_BG, fg=PINK_FG, padx=40, pady=10)
                        q.paste_center(im, lay, W / 2, 610 + 110 * j, 1.0, kk)
                q.paste_center(im, q.text_layer([("เมนต์ตัวเลขบอกได้เลย", q.F("Prompt-Medium.ttf", 40), (255, 255, 255))]),
                               W / 2, 960, 1.0, q.ease((t - 0.6) / 0.2))
                if t > 0.8:
                    kk = q.ease((t - 0.8) / 0.25)
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
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main(sys.argv[1])
