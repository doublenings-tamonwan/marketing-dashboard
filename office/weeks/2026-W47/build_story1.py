"""ประกอบคลิป ซีรีส์ไม่ได้บอก EP.1 จากเสียงพากย์ 3 ไฟล์ + ฉากหลัง AI + น้องนางาจิชุดนักเรียน
python3 build_story1.py <workdir with vo1.wav vo2.wav vo3.wav>
ผลลัพธ์ในworkdir: vo.wav, base.mp4, subs.json, scenes.json
"""
import sys, os, json, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_mockframes as M
from character import draw_nagaji

WD = sys.argv[1]
SR = 48000; FPS = 30; W, H = M.W, M.H

# ฉาก -> (ไฟล์, ช่วงพูด) จับคู่จากช่วงเงียบในไฟล์เสียง
PLAN = [(1, 1.25, 7.10), (1, 7.75, 13.45), (1, 14.90, 19.50), (2, 1.45, 8.45), (2, 9.05, 20.05),
        (3, 1.70, 7.75), (3, 8.65, 15.20), (3, 15.75, 20.70), [(3, 21.55, 30.65), (4, 0.90, 2.60)]]  # ไฟล์ 4 = "เจอกันคลิปหน้านะ"
# ท่อนเสียงที่ตัดทิ้ง (ไฟล์, เริ่ม, จบ) — "ตอนหน้าจะมาเล่าเรื่องโซจูต่อ" (เจ้าของช่องขอตัด)
CUTS = [(3, 26.3, 27.8)]
END_CARD = "เจอกันคลิปหน้า!"  # ข้อความปิดท้ายหลังเสียงพูดจบ
# ซับ (ตามบท v2 — ต้องให้เจ้าของช่องเช็กกับที่พูดจริง)
SUBS = [
  ["ใครดูซีรีส์เกาหลีบ่อย ๆ\nเคยสังเกตไหมคะ", "ฉากวันเกิดเนี่ย\nต้องมี[ซุปสาหร่าย]ตลอดเลย"],
  ["แต่รู้ไหม\nถ้าไปกินวันสอบนะ…", "คนเกาหลีเขาบอกว่า\n[สอบตก]เลยนะ", "เดี๋ยวเล่าให้ฟัง"],
  ["ซุปนี้ชื่อ [มิยอกกุก] ค่ะ", "ก็คือซุปสาหร่าย\nของเขานั่นแหละ"],
  ["คือที่เกาหลี\nผู้หญิงที่เพิ่งคลอดลูก", "เขาจะกินซุปนี้กัน\nเป็นอาทิตย์ ๆ เลย", "[เชื่อกันว่า]ช่วยบำรุงแม่"],
  ["พอถึงวันเกิด\nก็เลยกินซุปนี้", "เหมือนนึกถึงวันที่\n[แม่คลอดเรา]ออกมา…", "น่ารักเนอะ\nแต่ยังไม่จบนะ", "มีเรื่องที่[แปลกกว่านี้]อีก\nเดี๋ยวเล่าให้ฟัง"],
  ["มี[เรื่องเล่า]ตั้งแต่\nสมัยโชซอนเลยนะ", "ว่ามีคนไปเห็นวาฬ\nที่เพิ่งคลอดลูก", "กินสาหร่ายเข้าไป\n[เต็มท้อง]เลย"],
  ["ทีนี้ วันสอบ\n[ห้ามกิน]เด็ดขาดเลยนะ", "เพราะสาหร่ายมัน[ลื่น]\nใช่ไหม…", "ความรู้ก็จะ\nลื่นหลุดไปด้วย"],
  ["ขนาดคำว่า\n\"กินซุปสาหร่าย\"", "ในภาษาเกาหลี\nเขายังใช้แปลว่า[สอบตก]"],
  ["เพื่อน ๆ เคยเห็นฉากนี้\nในเรื่องไหนบ้าง", "มา[เมนต์]บอกกันหน่อยน้า", "อย่าลืม[กดติดตาม]ไว้นะคะ"],
]

TEMPO = float(os.environ.get("TEMPO", "1.0"))   # 1.08 = พูดเร็วขึ้น 8%
PITCH = float(os.environ.get("PITCH", "1.0"))   # 1.04 = เสียงสดใสขึ้นเล็กน้อย

def load(n):
    src = f"{WD}/vo{n}.wav"
    if TEMPO != 1.0 or PITCH != 1.0:  # เร่งจังหวะพูด + ปรับเสียงให้สดใส
        fast = f"{WD}/vo{n}-t{TEMPO}-p{PITCH}.wav"
        if not os.path.exists(fast):
            af = f"asetrate={int(SR * PITCH)},aresample={SR},atempo={TEMPO / PITCH:.4f}"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-af", af, "-ar", str(SR), "-ac", "1", fast], check=True)
        src = fast
    w = wave.open(src); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x

def speech_segs(x, a, b):
    win = int(SR * 0.05); seg = x[int(a * SR):int(b * SR)]
    k = len(seg) // win
    db = 20 * np.log10(np.sqrt((seg[:k * win].reshape(k, win) ** 2).mean(1)) + 1e-9)
    on = db > -42; out = []; i = 0
    while i < k:
        if on[i]:
            j = i
            while j < k and on[j]: j += 1
            out.append([a + i * 0.05, a + j * 0.05]); i = j
        else: i += 1
    m = []
    for s in out:
        if m and s[0] - m[-1][1] < 0.2: m[-1][1] = s[1]
        else: m.append(s)
    return m

def build_audio():
    vos = {n: load(n) for n in (1, 2, 3, 4)}
    pieces = [np.zeros(int(SR * 0.35), np.float32)]; t = 0.35; scenes = []
    for entry in PLAN:
        st = t; talk = []
        for j, (n, a, b) in enumerate(entry if isinstance(entry, list) else [entry]):
            a, b = a / TEMPO, b / TEMPO
            x = vos[n]; segs = speech_segs(x, a, b)
            segs = [g for g in segs if not any(cn == n and g[0] * TEMPO < c1 and g[1] * TEMPO > c0 for cn, c0, c1 in CUTS)]
            if j:
                pieces.append(np.zeros(int(SR * 0.3), np.float32)); t += 0.3
            for i, (s0, s1) in enumerate(segs):
                s0 -= 0.08; s1 += 0.08
                if i:
                    gap = min(0.3, max(0.0, s0 - segs[i - 1][1] - 0.16))
                    pieces.append(np.zeros(int(SR * gap), np.float32)); t += gap
                c = x[int(s0 * SR):int(s1 * SR)]
                pieces.append(c); talk.append([t, t + len(c) / SR]); t += len(c) / SR
        t_end = t + 0.35
        pieces.append(np.zeros(int(SR * 0.35), np.float32)); t = t_end
        scenes.append({"start": st - (0.35 if not scenes else 0.35), "speech_start": st, "end": t, "talk": talk})
    scenes[0]["start"] = 0.0
    for i in range(1, len(scenes)): scenes[i]["start"] = scenes[i - 1]["end"]
    tail = 2.0; pieces.append(np.zeros(int(SR * tail), np.float32)); scenes[-1]["end"] += tail
    y = np.concatenate(pieces)
    with wave.open(f"{WD}/vo-raw.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    return scenes

def build_subs(scenes):
    subs = []
    for si_, (sc, lines) in enumerate(zip(scenes, SUBS)):
        talk = sc["talk"][:-1] if (END_CARD and si_ == len(scenes) - 1) else sc["talk"]; total = sum(b - a for a, b in talk)
        weights = [len(l.replace("[", "").replace("]", "")) for l in lines]; tw = sum(weights)
        # แบ่งเวลาพูดตามจำนวนตัวอักษร แล้วยึดจุดเริ่มกับท่อนพูดที่ใกล้ที่สุด
        acc = 0; bounds = []
        for wgt in weights:
            acc += wgt / tw * total; bounds.append(acc)
        def at(sp):  # speech-time -> clip time
            for a, b in talk:
                if sp <= b - a: return a + sp
                sp -= b - a
            return talk[-1][1]
        starts = [talk[0][0]] + [at(bb) for bb in bounds[:-1]]
        starts = [min((a for a, _ in talk), key=lambda v: abs(v - s)) if min(abs(a - s) for a, _ in talk) < 0.45 else s for s in starts]
        for i, l in enumerate(lines):
            end = starts[i + 1] if i + 1 < len(lines) else sc["end"] - 0.1
            ln = l.count("\n") + 1
            subs.append({"start": round(starts[i], 2), "end": round(end, 2), "text": l, "y": 870 - 112 * ln})
    if END_CARD:
        a4 = scenes[-1]["talk"][-1][0]   # ท่อนสุดท้าย = เสียง "เจอกันคลิปหน้านะ"
        subs[-1]["end"] = round(a4 - 0.05, 2)
        subs.append({"start": round(a4 - 0.05, 2), "end": round(scenes[-1]["end"] - 0.05, 2), "text": END_CARD, "y": 758})
    json.dump(subs, open(f"{WD}/subs.json", "w"), ensure_ascii=False, indent=1)
    return subs

def bell_icon(size=130):
    S4 = 4; c = size * S4
    im = Image.new("RGBA", (c, c), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    Y = (255, 205, 70); OUTL = (60, 40, 30)
    def P(v): return v * c / 100
    # body
    d.pieslice([P(22), P(14), P(78), P(70)], 180, 360, fill=Y, outline=OUTL, width=S4 * 4)
    d.polygon([(P(22), P(42)), (P(78), P(42)), (P(86), P(74)), (P(14), P(74))], fill=Y)
    d.line([(P(22), P(42)), (P(14), P(74))], fill=OUTL, width=S4 * 4); d.line([(P(78), P(42)), (P(86), P(74))], fill=OUTL, width=S4 * 4)
    d.rounded_rectangle([P(10), P(70), P(90), P(80)], P(5), fill=Y, outline=OUTL, width=S4 * 4)
    d.ellipse([P(42), P(78), P(58), P(92)], fill=Y, outline=OUTL, width=S4 * 4)
    d.ellipse([P(45), P(5), P(55), P(15)], fill=Y, outline=OUTL, width=S4 * 4)
    d.arc([P(30), P(24), P(50), P(44)], 190, 260, fill=(255, 245, 210), width=S4 * 5)
    for side in (-1, 1):  # เส้นสั่น
        for r in (8, 16):
            x0 = 50 + side * (36 + r)
            d.arc([P(x0 - r), P(40 - r), P(x0 + r), P(40 + r)], 300 if side > 0 else 120, 60 if side > 0 else 240, fill=(255, 255, 255), width=S4 * 4)
    im = im.resize((size, size), Image.LANCZOS)
    a = im.getchannel("A").filter(M.ImageFilter.MaxFilter(9))
    out = Image.new("RGBA", im.size, (255, 255, 255, 0)); out.putalpha(a); out.alpha_composite(im)
    return out


def render(scenes):
    total = scenes[-1]["end"]; N = int(total * FPS)
    # ความดังเสียงต่อเฟรม -> ขยับปาก
    w = wave.open(f"{WD}/vo-raw.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = SR // FPS
    rms = [20 * np.log10(np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean() + 1e-12)) for i in range(N)]
    cache = {}
    def masc(pose, face):
        k = (pose, face)
        if k not in cache: cache[k] = draw_nagaji(pose=pose, face=face, height=780, outfit="school")
        return cache[k]
    pre = []
    for i, (sc, spec) in enumerate(zip(scenes, M.SCENES)):
        bg, zoom, fy, pose, face, label, ko, kofirst, sub = spec
        src = M.cover(f"{M.HERE}/story1-bg/{bg}.jpg", zoom, fy)
        base = Image.new("RGBA", (W, H), M.NAVY + (255,))
        base.paste(src.crop((0, M.SHIFT, W, H)), (0, 0))
        fill = src.crop((0, H - 300, W, H)).resize((W, M.SHIFT + 120)).filter(M.ImageFilter.GaussianBlur(30))
        fm = Image.linear_gradient("L").resize((W, M.SHIFT + 120)).point(lambda v: min(255, v * 3))
        base.paste(fill, (0, H - M.SHIFT - 120), fm)
        top = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.grad(top, True, 420, 190); M.grad(top, False, 760, 235)
        lab = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lab)
        ft = M.font("Prompt-SemiBold.ttf", 40); tag = "ซีรีส์ไม่ได้บอก · EP.1"; tw = d.textlength(tag, font=ft)
        d.rounded_rectangle([W/2-tw/2-28, 110, W/2+tw/2+28, 180], 35, fill=M.CORAL)
        d.text((W/2-tw/2, 116), tag, font=ft, fill="white")
        pl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.pill(ImageDraw.Draw(pl), label, 225, ko, kofirst)
        pre.append((base.convert("RGB"), top, lab, pl, M.doodles(i), pose, face))
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                          f"{WD}/base.mp4"], stdin=subprocess.PIPE)
    subs = json.load(open(f"{WD}/subs.json")); last = next(x for x in subs if "กดติดตาม" in x["text"])
    BELL = bell_icon(170)
    si = 0
    for f in range(N):
        t = f / FPS
        while si + 1 < len(scenes) and t >= scenes[si + 1]["start"]: si += 1
        sc = scenes[si]; lt = t - sc["start"]; dur = sc["end"] - sc["start"]
        base, top, lab, pl, doo, pose, face = pre[si]
        z = 1.0 + 0.06 * (lt / dur) + (0.06 * max(0, 1 - lt / 0.25) ** 2)  # ซูมช้า + กระแทกตอนเปลี่ยนฉาก
        bw, bh = int(W * z), int(H * z)
        frame = base.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 3, (bw - W) // 2 + W, (bh - H) // 3 + H)).convert("RGBA")
        frame.alpha_composite(top); frame.alpha_composite(lab)
        k = min(1.0, lt / 0.18); s = 0.7 + 0.3 * k + 0.08 * math.sin(k * math.pi)  # ป้ายเด้ง
        if s != 1.0:
            box = pl.getbbox(); piece = pl.crop(box)
            pw, ph = int(piece.width * s), int(piece.height * s)
            piece = piece.resize((max(1, pw), max(1, ph)))
            frame.alpha_composite(piece, (int((box[0] + box[2]) / 2 - pw / 2), int((box[1] + box[3]) / 2 - ph / 2)))
        else:
            frame.alpha_composite(pl)
        talking = rms[f] > -38 and any(a - 0.05 <= t <= b for a, b in sc["talk"])
        fc = ("talk" if (f // 4) % 2 == 0 else face) if talking else face
        if not talking and face in ("smile", "talk") and (f % 105) in (0, 1, 2): fc = "happy"  # กะพริบตา
        m = masc(pose, fc)
        bob = int(6 * math.sin(t * 2 * math.pi / 1.6)); hop_in = int(60 * max(0, 1 - lt / 0.2) ** 2)
        frame.alpha_composite(m, (10, H - 190 - m.height + bob + hop_in))
        frame.alpha_composite(doo)
        if last["start"] <= t < last["end"] + 0.3:
            bt = t - last["start"]; sc_ = min(1, bt / 0.15)
            ang = 18 * math.sin(bt * 2 * math.pi * 3) * math.exp(-bt * 1.2) if bt > 0.15 else 0
            b = BELL.rotate(ang, resample=Image.BICUBIC, center=(85, 18))
            if sc_ < 1: b = b.resize((max(1, int(170 * sc_)), max(1, int(170 * sc_))))
            frame.alpha_composite(b, (540 - b.width // 2, 715 - b.height // 2))
        d = ImageDraw.Draw(frame)
        d.rectangle([0, H - 10, W, H], fill=(60, 72, 120)); d.rectangle([0, H - 10, int(W * t / scenes[-1]["end"]), H], fill=M.YEL)
        p.stdin.write(frame.convert("RGB").tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    scenes = build_audio()
    json.dump(scenes, open(f"{WD}/scenes.json", "w"), indent=1)
    build_subs(scenes)
    print("audio", round(scenes[-1]["end"], 2), "s;", [round(s["end"] - s["start"], 2) for s in scenes])
    if "--no-video" not in sys.argv: render(scenes)
