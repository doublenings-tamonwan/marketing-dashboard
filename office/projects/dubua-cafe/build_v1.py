"""พามารีวิว EP.2 — ดูบัว คาเฟ่ (build v1: ข้อความบนจอ + ดนตรีแต่งเอง ไม่มีเสียงพากย์)

ใช้: python3 office/projects/dubua-cafe/build_v1.py [--src <โฟลเดอร์ฟุตเทจ>] [--work <โฟลเดอร์งาน>]
ผลลัพธ์: <work>/out/dubua-ep2-preview.mp4, <work>/out/dubua-ep2-cover.jpg (ไม่ commit วิดีโอ/ภาพ)

หมายเหตุ
- ฟุตเทจ iPhone เป็น HEVC 10-bit HDR (HLG) + rotation -90 → ffmpeg หมุนให้อัตโนมัติ (ได้ภาพตั้ง)
  และต้องแปลง HDR → SDR (zscale + tonemap hable) ไม่งั้นสีซีด/จืด
- ช่วงที่ใช้เลือกจากการดูเฟรมจริง + วัดการสั่นของภาพ (ไม่ใช่ช่วงประมาณในสคริปต์ทุกช็อต)
- ช็อตที่ภาพนิ่งสั้นกว่าท่อน (2747 เพื่อนยืนมองร้าน, 2740 ป้ายกาดบ้านควาย) ยืดเป็นสโลว์นิด ๆ (~0.76x)
- เจ้าของช่องสั่ง (2026-11-17): ไม่ใส่ฟิลเตอร์ใด ๆ — ไม่มีแสงฟุ้ง ไม่ปรับโทนอุ่น/สี ไม่มีวิ้ง
  ใช้ภาพตามต้นฉบับ (มีแค่การแปลง HDR→SDR ซึ่งจำเป็น ไม่งั้นภาพซีดผิดจากที่เห็นในมือถือ)
"""
import argparse
import json
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ED = os.path.join(REPO, "office", "editor")
FONTS = os.path.join(REPO, "office", "assets", "fonts")
HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("--src", default="/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/")
ap.add_argument("--work", default="/tmp/claude-0/-home-user-marketing-dashboard/"
                "3fe5eb85-c984-5962-ae79-e39ba747511b/scratchpad/cafe2")
a = ap.parse_args()
U = a.src.rstrip("/") + "/"
W_ = os.path.join(a.work, "work")
OUT = os.path.join(a.work, "out")
os.makedirs(W_, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
os.chdir(W_)


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


TM = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
FIT = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1"

# (ไฟล์, เริ่มในไฟล์, ความยาวต้นฉบับ, ความยาวในคลิป)
SHOTS = [
    ("4e6a7915-IMG_2737.mov", 3.2, 2.0, 2.0),   # 1 เซลฟี่ยิ้ม ใต้ร่มไม้ (ช่วงที่นิ่งสุด + ยิ้มเข้ากล้อง)
    ("3a4d493b-IMG_2747.mov", 7.5, 1.9, 2.5),   # 2 เพื่อน (หันหลัง) ยืนมองร้านริมบึง เห็นป้าย DubuaCafe
    ("f6d86073-IMG_2748.mov", 0.5, 2.0, 2.0),   # 3 ป้าย DubuaCafe ต้นมะพร้าว
    ("c7350462-IMG_2749.mov", 1.0, 2.0, 2.0),   # 4 ตึกดำกระจกใส (หลัง 1.3 วิ ภาพนิ่ง)
    ("c9c98111-IMG_2752.mov", 2.0, 1.5, 1.5),   # 5a ตู้เค้ก (ช่วงท้ายที่ภาพนิ่ง)
    ("1135d74b-IMG_2753.mov", 0.3, 1.0, 1.0),   # 5b ตู้มาการง
    ("4d791dc7-IMG_2740.mov", 0.0, 1.9, 2.5),   # 6 ป้ายกาดบ้านควาย (หลัง ~1.9 วิ กล้องแพนออก)
    ("95bcdcf9-IMG_2736.mov", 0.4, 2.0, 2.0),   # 7 ทางเดินร่มไม้ รั้วไม้ขาว (จบก่อนเพื่อนเดินเข้าเฟรมใกล้ ๆ ที่ ~2.5 วิ)
]
CARD = 2.5

names = []
for i, (f, ss, src_d, out_d) in enumerate(SHOTS):
    k = out_d / src_d
    vf = f"{TM},setpts={k:.4f}*(PTS-STARTPTS),{FIT}"
    out = f"s{i}.mp4"
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", ss, "-i", U + f, "-an", "-vf", vf,
        "-t", out_d, "-c:v", "libx264", "-preset", "fast", "-crf", "18", out)
    names.append(out)
open("list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "base.mp4")

# ---------- การ์ดท้าย ----------
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", 2.0, "-i", U + "c7350462-IMG_2749.mov",
    "-vf", f"{TM},{FIT}", "-frames:v", "1", "cardbg.png")
bg = Image.open("cardbg.png").convert("RGB").filter(ImageFilter.GaussianBlur(20))
bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 244, 248)), 0.30)


def F(name, size, wght=None):
    ft = ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)
    if wght:
        ft.set_variation_by_axes([wght])
    return ft


PINK_BG, PINK_FG, INK, SOFT = (255, 214, 231), (122, 14, 59), (58, 44, 50), (130, 112, 120)
PW, PH = 900, 860
panel = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
d = ImageDraw.Draw(panel)
d.rounded_rectangle((0, 0, PW - 1, PH - 1), radius=56, fill=(255, 255, 255, 238))
cx = PW // 2
d.text((cx, 80), "Dubua Cafe", font=F("PlayfairDisplay-Italic.ttf", 108, 500), fill=PINK_FG, anchor="ma")
d.text((cx, 230), "ดูบัว คาเฟ่", font=F("Prompt-SemiBold.ttf", 66), fill=INK, anchor="ma")
# หมุดพิกัด (วาดเอง ไม่ใช้อีโมจิ)
loc = "อ.นครชัยศรี จ.นครปฐม"
lf = F("Prompt-Medium.ttf", 50)
tw = d.textlength(loc, font=lf)
px, py = cx - tw / 2 - 30, 395
d.ellipse((px - 20, py - 34, px + 20, py + 6), fill=(236, 92, 140))
d.polygon([(px - 17, py - 6), (px + 17, py - 6), (px, py + 26)], fill=(236, 92, 140))
d.ellipse((px - 8, py - 22, px + 8, py - 6), fill="white")
d.text((cx + 22, py), loc, font=lf, fill=INK, anchor="mm")
d.text((cx, 490), "คาเฟ่ริมบึงบัว · มีตู้เค้ก", font=F("Prompt-Medium.ttf", 48), fill=INK, anchor="mm")
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

n = round(CARD * 30)
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

# ---------- เวลาซับ = จุดเปลี่ยนท่อน ----------
subs = json.load(open(os.path.join(HERE, "subs.json")))
seg = [SHOTS[0][3], SHOTS[1][3], SHOTS[2][3], SHOTS[3][3], SHOTS[4][3] + SHOTS[5][3], SHOTS[6][3], SHOTS[7][3]]
t = 0.0
starts = []
for s, dd in zip(subs, seg):
    s["start"], s["end"] = round(t, 3), round(t + dd, 3)
    starts.append(round(t, 2))
    t += dd
total = round(t + CARD, 2)
# ซับบน (หลบหน้า/ป้าย): ท่อน 1 ซับล่างทับคางเจ้าของช่อง, ท่อน 2 ทับหลังเพื่อน (บนเป็นท้องฟ้าโล่ง),
# ท่อน 6 ซับล่างทับตัวหนังสือบนป้ายกาดบ้านควาย
for i in (0, 1, 5):
    subs[i]["pos"] = "top"
json.dump(subs, open("subs-v1.json", "w"), ensure_ascii=False, indent=1)

# ต่อการ์ดท้าย (ไม่มีแสงฟุ้ง/วิ้ง ตามที่เจ้าของช่องสั่ง)
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", "base.mp4", "-i", "card.mp4",
    "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[v]",
    "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "base-card.mp4")

# ดนตรีแต่งเอง แบบน่ารัก (cute) ไม่มีเสียงป๊อป — เจ้าของช่องขอ 2026-11-17 (v2)
run("python3", os.path.join(ED, "make_music.py"), "--mood", "cute", "--seed", "7", "--duration", total,
    "--out", "music.wav")

run("python3", os.path.join(ED, "burn_subs.py"), "--video", "base-card.mp4", "--subs", "subs-v1.json",
    "--out", os.path.join(OUT, "dubua-ep2-preview.mp4"), "--audio", "music.wav")

# ---------- หน้าปก: เฟรมเซลฟี่ยิ้ม ----------
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", 3.3, "-i", U + "4e6a7915-IMG_2737.mov",
    "-vf", TM, "-frames:v", "1", "cover-src.png")
run("python3", os.path.join(ED, "make_cover.py"), "--photo", "cover-src.png",
    "--out", os.path.join(OUT, "dubua-ep2-cover.jpg"), "--kicker", "พามารีวิว · EP.2",
    "--title", "Lotus Pond Café", "--pill", "คาเฟ่ริมบึงบัว นครปฐม", "--yc", 0.5, "--raw")
print("starts", starts, "total", total)
