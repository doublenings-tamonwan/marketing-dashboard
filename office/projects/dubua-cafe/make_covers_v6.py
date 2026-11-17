"""หน้าปกใหม่ EP.2 ดูบัว (เจ้าของช่องขอแบบดึงดูด 2026-11-17) — 3 ตัวเลือก
A: รูปกระจกแก๊ง 3 คน · B: คอลลาจ 4 ช่อง (บึง/ขนม/อาหาร/แก๊ง) · C: ป้าย Dubua บนกำแพง
"""
import io, os, subprocess, sys
from PIL import Image, ImageCms
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ED = os.path.join(REPO, "office", "editor")
U = "/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/"
OUT = "/tmp/claude-0/-home-user-marketing-dashboard/3fe5eb85-c984-5962-ae79-e39ba747511b/scratchpad/cafe2/out/covers"
os.makedirs(OUT, exist_ok=True)
TM = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
SRGB = ImageCms.createProfile("sRGB")

def photo(f):
    im = Image.open(U + f); icc = im.info.get("icc_profile"); im = im.convert("RGB")
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), SRGB, outputMode="RGB")
    return im

def frame(f, t):
    p = os.path.join(OUT, f"f_{f[:8]}_{t}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", U + f, "-vf", TM, "-frames:v", "1", p], check=True)
    return Image.open(p).convert("RGB")

def fill(im, w, h, cx=0.5, cy=0.5):
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int((im.width - w) * cx); y = int((im.height - h) * cy)
    return im.crop((x, y, x + w, y + h))

def cover(src, out, title, pill, thai=True, yc=0.5):
    cmd = ["python3", os.path.join(ED, "make_cover.py"), "--photo", src, "--out", out, "--kicker", "พามารีวิว · EP.2",
           "--title", title, "--pill", pill, "--yc", str(yc), "--raw"]
    if thai: cmd.append("--thai-title")
    subprocess.run(cmd, check=True)

mirror = photo("e0180ad4-image.jpg").crop((882 - 330, 1720 - 586, 882 + 330, 1720 + 586))
# ปก A: ครอปกว้างขึ้นให้ผนังดำอยู่ด้านบน (ตัวหนังสือบนผนัง ไม่บังหน้า)
photo("e0180ad4-image.jpg").crop((488, 710, 1276, 2110)).resize((1080, 1920), Image.LANCZOS).save(os.path.join(OUT, "srcA.png"))
cover(os.path.join(OUT, "srcA.png"), os.path.join(OUT, "cover-A-mirror.jpg"), "ที่เดียวเที่ยว\nครบทั้งวัน!", "คาเฟ่ริมบึงบัว นครปฐม", yc=0.5)

tiles = [frame("3a4d493b-IMG_2747.mov", 8.2), frame("c9c98111-IMG_2752.mov", 2.6),
         photo("48d80f69-image.jpg"), mirror]
col = Image.new("RGB", (1080, 1920), "white")
for i, (im, cy) in enumerate(zip(tiles, (0.45, 0.4, 0.6, 0.3))):
    col.paste(fill(im, 536, 956, 0.5, cy), ((i % 2) * 544, (i // 2) * 964))
col.save(os.path.join(OUT, "srcB.png"))
cover(os.path.join(OUT, "srcB.png"), os.path.join(OUT, "cover-B-collage.jpg"), "ใกล้กรุงเทพฯ\nเที่ยวครบทั้งวัน!", "ดูบัว คาเฟ่ · นครปฐม", yc=0.5)

wall = photo("b8f6d7b8-image.jpg")
fill(wall, 1080, 1920, 0.5, 0.5).save(os.path.join(OUT, "srcC.png"))
cover(os.path.join(OUT, "srcC.png"), os.path.join(OUT, "cover-C-sign.jpg"), "ที่เดียวเที่ยว\nครบทั้งวัน!", "ใกล้กรุงเทพฯ แค่ 1 ชม.", yc=0.3)
print("ok")
