"""พามารีวิว EP.2 — ดูบัว คาเฟ่ (build v4 → ไฟล์ preview-v5: "ครบ 3 อย่าง" + เบลอหน้าเพื่อน 2 คนในรูปกระจก + ไม่มีเสียง — เจ้าของช่องขอ 2026-11-17)

ใช้: python3 office/projects/dubua-cafe/build_v2.py [--src <โฟลเดอร์ฟุตเทจ>] [--work <โฟลเดอร์งาน>]
ผลลัพธ์: <work>/out/dubua-ep2-preview-v5-sound.mp4, <work>/out/dubua-ep2-cover-v5.jpg (ไม่ commit วิดีโอ/ภาพ)

แผน: script.md หัวข้อ "เวอร์ชัน 2 (2026-11-17)" · ซับ: subs-v2.json (ข้อความตามไฟล์ทุกคำ เวลาคำนวณจากช็อต)

หมายเหตุ
- เจ้าของช่องสั่ง: ไม่ใส่ฟิลเตอร์ (ไม่แสงฟุ้ง ไม่วิ้ง ไม่ปรับสี) — ทำแค่การแปลงสีที่จำเป็น:
  วิดีโอ iPhone HDR (HLG) → SDR และรูป JPG แบบ Display P3 → sRGB (ไม่งั้นสีซีดกว่าที่เห็นในมือถือ)
- รูปนิ่ง = Ken Burns ซูมเข้าช้า ๆ ~10% (กรอบครอป 9:16 เสมอ ไม่ยืดภาพผิดสัดส่วน) ไม่มีแฟลชขาว (ถือเป็นเอฟเฟกต์)
- IMG_2744 (โต๊ะอาหาร) ใช้ช่วง 3.0–4.5 วิ ที่ไม่เห็นหน้าคน + ครอปตัดขอบบน 20% (ตัดลำตัวคนนั่ง)
- ป้ายเล็กช็อตเปิด วาดด้วย Pillow (raqm) แล้ว overlay — ไม่ใช้ libass กับภาษาไทย
- ดนตรี make_music.py --mood cute --seed 7 ไม่มีเสียงป๊อป
"""
import argparse
import io
import json
import os
import subprocess

from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ED = os.path.join(REPO, "office", "editor")
FONTS = os.path.join(REPO, "office", "assets", "fonts")
HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("--src", default="/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/")
ap.add_argument("--work", default="/tmp/claude-0/-home-user-marketing-dashboard/"
                "3fe5eb85-c984-5962-ae79-e39ba747511b/scratchpad/cafe2")
ap.add_argument("--check", action="store_true", help="เรนเดอร์แค่เฟรมเช็กของรูปนิ่ง (ต้น/กลาง/ท้าย)")
a = ap.parse_args()
U = a.src.rstrip("/") + "/"
W_ = os.path.join(a.work, "work-v5")
OUT = os.path.join(a.work, "out")
os.makedirs(W_, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
os.chdir(W_)


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


TM = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
FIT = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1"
FPS = 30
SRGB = ImageCms.createProfile("sRGB")


def F(name, size, wght=None):
    ft = ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)
    if wght:
        ft.set_variation_by_axes([wght])
    return ft


def load_photo(path):
    """เปิดรูป + แปลง Display P3 → sRGB (การจัดการสีที่จำเป็น ไม่ใช่การแต่งสี)"""
    im = Image.open(path)
    icc = im.info.get("icc_profile")
    im = im.convert("RGB")
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, SRGB, outputMode="RGB")
    if os.path.basename(path) in BLUR:
        for cx, cy, rx, ry in BLUR[os.path.basename(path)]:
            bx = (cx - rx, cy - ry, cx + rx, cy + ry)
            m = Image.new("L", im.size, 0)
            ImageDraw.Draw(m).ellipse(bx, fill=255)
            m = m.filter(ImageFilter.GaussianBlur(6))
            im = Image.composite(im.filter(ImageFilter.GaussianBlur(18)), im, m)
    return im


# เบลอหน้าเพื่อน (พิกัดรูปต้นฉบับ 1932x2576) — หน้าเจ้าของช่องถูกมือถือบังอยู่แล้ว
BLUR = {"268d99d0-image.jpg": [(808, 1628, 48, 60), (1033, 1617, 48, 60)]}


def box(cx, cy, h, im):
    """กรอบ 9:16 สูง h จุดกลาง (cx, cy) — เลื่อนให้อยู่ในรูปเสมอ"""
    w = h * 9 / 16
    W, H = im.size
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return (x0, y0, x0 + w, y0 + h)


def kenburns(im, b0, b1, dur, out):
    n = round(dur * FPS)
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", "1080x1920", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast",
                          "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / max(n - 1, 1)
        bx = tuple(b0[i] + (b1[i] - b0[i]) * t for i in range(4))
        p.stdin.write(im.resize((1080, 1920), Image.LANCZOS, box=bx).tobytes())
    p.stdin.close()
    p.wait()


# ---------- ช็อต ----------
# วิดีโอ: ("v", ไฟล์, เริ่มในไฟล์, ความยาวในคลิป, vf เพิ่มก่อน FIT)
# รูป:   ("p", ไฟล์, (cx, cy, h) เริ่ม, (cx, cy, h) จบ, ความยาวในคลิป)  พิกัดเป็นพิกเซลรูปต้นฉบับ 1932x2576
SHOTS = [
    ("v", "4e6a7915-IMG_2737.mov", 3.2, 2.0, ""),                      # 0 เซลฟี่ + ป้ายเล็ก
    ("p", "b8f6d7b8-image.jpg", (1024, 1288, 2576), (1020, 1360, 2342), 2.0),  # 1 ป้าย Dubua CAFE บนกำแพง
    ("v", "3a4d493b-IMG_2747.mov", 7.5, 1.5, ""),                      # 2a ริมบึง เพื่อนหันหลัง มองร้าน
    ("v", "f6d86073-IMG_2748.mov", 0.5, 1.5, ""),                      # 2b ป้ายหิน DubuaCafe
    ("v", "c7350462-IMG_2749.mov", 1.0, 1.0, ""),                      # 3a ตึกดำกระจกใส
    ("v", "c9c98111-IMG_2752.mov", 2.2, 1.2, ""),                      # 3b ตู้เค้ก
    ("v", "1135d74b-IMG_2753.mov", 0.3, 0.8, ""),                      # 3c ตู้มาการอง
    ("v", "8270c542-IMG_2744.mov", 3.0, 1.5, "crop=iw*0.8:ih*0.8:iw*0.1:ih*0.2,"),  # 4a โต๊ะอาหาร (ไม่เห็นหน้า)
    ("p", "48d80f69-image.jpg", (960, 1548, 2056), (1040, 1680, 1869), 1.5),  # 4b แกง/ส้มตำ/ไก่ย่าง
    ("p", "268d99d0-image.jpg", (946, 1996, 1160), (946, 2000, 1054), 2.0),   # 6 กระจก Secret Backyard 3 คน
]
CARD = 2.5
SEGS = [[0], [1], [2, 3], [4, 5, 6], [7, 8], [9]]   # ซับแต่ละอันครอบช็อตไหน
TOP_SUBS = (0, 1, 2)  # 0 หลบหน้าเซลฟี่ · 1 หลบป้าย Dubua · 2 หลบหลังเพื่อน/ป้ายหิน · 5 หลบป้ายมินิซู

if a.check:
    for i, s in enumerate(SHOTS):
        if s[0] != "p":
            continue
        im = load_photo(U + s[1])
        for tag, t in (("a", 0), ("b", 0.5), ("c", 1)):
            b0, b1 = box(*s[2], im), box(*s[3], im)
            bx = tuple(b0[j] + (b1[j] - b0[j]) * t for j in range(4))
            im.resize((540, 960), Image.LANCZOS, box=bx).save(f"chkp{i}{tag}.jpg")
    raise SystemExit

# ป้ายเล็กช็อตเปิด (วาดเอง ไม่ใช้อีโมจิ ไม่ใช้ libass)
label = "นครปฐม · ขับจากกรุงเทพฯ ~1 ชม."
lf = F("Prompt-Medium.ttf", 42)
tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(label, font=lf)
asc, desc = lf.getmetrics()
lh = asc + desc + 26
lab = Image.new("RGBA", (int(tw) + 72, lh), (0, 0, 0, 0))
ld = ImageDraw.Draw(lab)
ld.rounded_rectangle((0, 0, lab.width - 1, lh - 1), radius=lh // 2, fill=(255, 255, 255, 230))
ld.text((lab.width / 2, lh / 2), label, font=lf, fill=(58, 44, 50), anchor="mm")
lab.save("label.png")
LABEL_Y = 1430  # ใต้คาง บนเสื้อขาว (ซับช็อตนี้อยู่บน)

names = []
for i, s in enumerate(SHOTS):
    out = f"s{i}.mp4"
    if s[0] == "v":
        _, f, ss, d, pre = s
        vf = f"{TM},{pre}{FIT}"
        if i == 0:
            run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", ss, "-i", U + f, "-i", "label.png", "-an",
                "-filter_complex", f"[0:v]{vf}[b];[b][1:v]overlay=(W-w)/2:{LABEL_Y},format=yuv420p",
                "-t", d, "-c:v", "libx264", "-preset", "fast", "-crf", "18", out)
        else:
            run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", ss, "-i", U + f, "-an", "-vf", vf,
                "-t", d, "-c:v", "libx264", "-preset", "fast", "-crf", "18", out)
    else:
        _, f, c0, c1, d = s
        im = load_photo(U + f)
        kenburns(im, box(*c0, im), box(*c1, im), d, out)
    names.append(out)
open("list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "base.mp4")

# ---------- การ์ดท้าย (เหมือน v1 เปลี่ยนบรรทัดจุดเด่น) ----------
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", 2.0, "-i", U + "c7350462-IMG_2749.mov",
    "-vf", f"{TM},{FIT}", "-frames:v", "1", "cardbg.png")
bg = Image.open("cardbg.png").convert("RGB").filter(ImageFilter.GaussianBlur(20))
bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 244, 248)), 0.30)

PINK_BG, PINK_FG, INK, SOFT = (255, 214, 231), (122, 14, 59), (58, 44, 50), (130, 112, 120)
PW, PH = 900, 860
panel = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
d = ImageDraw.Draw(panel)
d.rounded_rectangle((0, 0, PW - 1, PH - 1), radius=56, fill=(255, 255, 255, 238))
cx = PW // 2
d.text((cx, 80), "Dubua Cafe", font=F("PlayfairDisplay-Italic.ttf", 108, 500), fill=PINK_FG, anchor="ma")
d.text((cx, 230), "ดูบัว คาเฟ่", font=F("Prompt-SemiBold.ttf", 66), fill=INK, anchor="ma")
loc = "อ.นครชัยศรี จ.นครปฐม"
lf2 = F("Prompt-Medium.ttf", 50)
tw = d.textlength(loc, font=lf2)
px, py = cx - tw / 2 - 30, 395
d.ellipse((px - 20, py - 34, px + 20, py + 6), fill=(236, 92, 140))
d.polygon([(px - 17, py - 6), (px + 17, py - 6), (px, py + 26)], fill=(236, 92, 140))
d.ellipse((px - 8, py - 22, px + 8, py - 6), fill="white")
d.text((cx + 22, py), loc, font=lf2, fill=INK, anchor="mm")
feat = "ริมบึงบัว · คาเฟ่ · อาหารไทย"
fs = 48
while d.textlength(feat, font=F("Prompt-Medium.ttf", fs)) > PW - 120:
    fs -= 2
d.text((cx, 490), feat, font=F("Prompt-Medium.ttf", fs), fill=INK, anchor="mm")
d.text((cx, 580), "เช็กเวลาเปิดที่เพจร้านก่อนไปนะ", font=F("Prompt-Medium.ttf", 38), fill=SOFT, anchor="mm")
pill = "เซฟไว้ · แท็กเพื่อน"
pf = F("Prompt-Medium.ttf", 50)
tw = d.textlength(pill, font=pf)
asc, desc = pf.getmetrics()
ph = asc + desc + 30
d.rounded_rectangle((cx - tw / 2 - 56, 690, cx + tw / 2 + 56, 690 + ph), radius=ph // 2, fill=PINK_BG)
d.text((cx, 690 + ph / 2), pill, font=pf, fill=PINK_FG, anchor="mm")
sh = Image.new("RGBA", (PW + 160, PH + 160), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((80, 92, PW + 80, PH + 92), radius=56, fill=(60, 30, 45, 70))
sh = sh.filter(ImageFilter.GaussianBlur(26))

n = round(CARD * FPS)
X0, Y0 = (1080 - PW) // 2, (1920 - PH) // 2 - 40
p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                      "-s", "1080x1920", "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "fast",
                      "-crf", "18", "-pix_fmt", "yuv420p", "card.mp4"], stdin=subprocess.PIPE)
for k in range(n):
    z = 1 + 0.05 * k / n
    w, h = 1080 / z, 1920 / z
    fr = bg.resize((1080, 1920), Image.LANCZOS, box=((1080 - w) / 2, (1920 - h) / 2, (1080 + w) / 2, (1920 + h) / 2)).convert("RGBA")
    al = min(1, k / 9)
    off = int((1 - al) * 60)
    for layer, (x, y) in ((sh, (X0 - 80, Y0 - 80 + off)), (panel, (X0, Y0 + off))):
        l2 = layer.copy()
        l2.putalpha(l2.getchannel("A").point(lambda v: int(v * al)))
        fr.alpha_composite(l2, (x, y))
    p.stdin.write(fr.convert("RGB").tobytes())
p.stdin.close()
p.wait()

# ---------- ซับ: ข้อความจาก subs-v2.json ทุกคำ เวลา = จุดเปลี่ยนท่อน ----------
dur = [s[3] if s[0] == "v" else s[4] for s in SHOTS]
subs = json.load(open(os.path.join(HERE, "subs-v3.json")))
assert len(subs) == len(SEGS)
t = 0.0
starts = []
for i, (s, seg) in enumerate(zip(subs, SEGS)):
    dd = sum(dur[j] for j in seg)
    s["start"], s["end"] = round(t, 3), round(t + dd, 3)
    if i in TOP_SUBS:
        s["pos"] = "top"
    starts.append(round(t, 2))
    t += dd
total = round(t + CARD, 2)
json.dump(subs, open("subs-v3.json", "w"), ensure_ascii=False, indent=1)

run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", "base.mp4", "-i", "card.mp4",
    "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[v]",
    "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "base-card.mp4")

run("python3", os.path.join(ED, "make_music.py"), "--mood", "cute", "--seed", "7", "--duration", total,
    "--out", "music.wav")

run("python3", os.path.join(ED, "burn_subs.py"), "--video", "base-card.mp4", "--subs", "subs-v3.json",
    "--out", os.path.join(OUT, "dubua-ep2-preview-v5-sound.mp4"), "--audio", "music.wav")

# ---------- หน้าปก: เฟรมเซลฟี่ยิ้ม (แบบเดิม เปลี่ยน pill) ----------
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", 3.3, "-i", U + "4e6a7915-IMG_2737.mov",
    "-vf", TM, "-frames:v", "1", "cover-src.png")
run("python3", os.path.join(ED, "make_cover.py"), "--photo", "cover-src.png",
    "--out", os.path.join(OUT, "dubua-ep2-cover-v5.jpg"), "--kicker", "พามารีวิว · EP.2",
    "--title", "Lotus Pond Café", "--pill", "ที่เดียวเที่ยวครบ นครปฐม", "--yc", 0.5, "--raw")
print("starts", starts, "total", total)

# ไม่มีเสียง (เจ้าของช่องเลือกเพลงในแอป TikTok เอง)
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(OUT, "dubua-ep2-preview-v5-sound.mp4"),
    "-an", "-c:v", "copy", os.path.join(OUT, "dubua-ep2-preview-v5.mp4"))
