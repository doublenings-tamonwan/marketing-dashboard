"""Mock frames: real AI backgrounds + mascot + labels, to preview the look before building the clip."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../editor"))
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from character import draw_nagaji
HERE = os.path.dirname(os.path.abspath(__file__))
F = HERE + "/../../assets/fonts/"; KO = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
def font(n, s): return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)
W, H = 1080, 1920
NAVY = (22, 30, 66); YEL = (255, 209, 102); CORAL = (255, 99, 99)

SCENES = [  # bg, crop zoom, focus y, pose, face, label, korean, kofirst, subtitle
  ("bg1", 1.15, 0.45, "stand", "surprised", "วันเกิดในซีรีส์เกาหลี\nต้องมีซุปนี้ทุกที!", None, False, "สังเกตไหม ซีรีส์เกาหลี\nวันเกิดทีไร ต้องมี[ซุปนี้]"),
  ("bg2", 1.0, 0.4, "wave", "wink", "แต่ถ้ากินวันสอบ…\nสอบตก!?", None, False, "คนเกาหลีบอกว่า[สอบตก]!"),
  ("bg3", 1.0, 0.4, "point", "talk", "มิยอกกุก", "미역국", False, "เมนูนี้ชื่อ [มิยอกกุก]"),
  ("bg4", 1.0, 0.4, "stand", "smile", "อาหารแม่หลังคลอด", None, False, "เชื่อกันว่า[ช่วยบำรุงแม่]"),
  ("bg5", 1.0, 0.4, "cheer", "happy", "วันเกิด = ระลึกถึงแม่", None, False, "กินเพื่อนึกถึง\nวันที่[แม่คลอดเรา]"),
  ("bg6", 1.0, 0.4, "stand", "surprised", "เรื่องเล่าสมัยโชซอน", None, False, "ท้องวาฬ[เต็มไปด้วยสาหร่าย]"),
  ("bg7", 1.0, 0.35, "point", "talk", "ลื่น = สอบตก", None, False, "สาหร่ายมัน[ลื่น]…"),
  ("bg3", 1.6, 0.42, "point", "talk", "= สอบตก", "미역국을 먹다", True, "ยังแปลว่า[สอบตก]เลย"),
  ("bg1", 1.0, 0.4, "wave", "smile", "ซีรีส์ไหนมีฉากนี้?", None, False, "เมนต์บอกหน่อย!"),
]

def cover(path, zoom, fy):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height) * zoom
    im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    x = (im.width - W)//2; y = int((im.height - H) * fy / 0.5 * 0.5) if zoom > 1 else (im.height - H)//2
    y = max(0, min(im.height - H, int((im.height - H) * fy * 2 * 0.5 + 0)))
    return im.crop((x, y, x+W, y+H))

def grad(img, top=True, h=380, a=170):
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    for i in range(h):
        al = int(a * (1 - i/h) ** 1.6)
        y = i if top else H-1-i
        d.line([(0, y), (W, y)], fill=NAVY + (al,))
    img.alpha_composite(ov)

def pill(d, text, y, ko=None, kofirst=False, size=74):
    f = font("Prompt-SemiBold.ttf", size); kf = ImageFont.truetype(KO, size)
    rows = [[(t, f)] for t in text.split("\n")]
    if ko:
        if kofirst: rows.insert(0, [(ko, kf)])
        else: rows[-1].append(("  " + ko, kf))
    lh = int(size * 1.45)
    tw = max(sum(d.textlength(t, font=ff) for t, ff in r) for r in rows)
    x0 = (W - tw)/2
    d.rounded_rectangle([x0-40, y-14, x0+tw+40, y+lh*len(rows)+14], 40, fill=YEL)
    for i, r in enumerate(rows):
        rw = sum(d.textlength(t, font=ff) for t, ff in r); x = (W-rw)/2
        for t, ff in r:
            d.text((x, y + i*lh), t, font=ff, fill=NAVY); x += d.textlength(t, font=ff)

def subtitle(d, text, ybot):
    f = font("Prompt-Medium.ttf", 64); lh = int(64*1.32*1.2)
    lines = text.split("\n"); y = ybot - lh*len(lines)
    for ln in lines:
        parts = []; buf = ""; hl = False
        for ch in ln:
            if ch in "[]":
                if buf: parts.append((buf, hl)); buf = ""
                hl = ch == "["
            else: buf += ch
        if buf: parts.append((buf, hl))
        tw = sum(d.textlength(t, font=f) + (36 if h else 0) for t, h in parts); x = (W - tw)/2
        for t, h in parts:
            w = d.textlength(t, font=f)
            if h:
                x += 18
                d.rounded_rectangle([x-12, y-4, x+w+12, y+lh-14], 18, fill=CORAL)
                d.text((x, y), t, font=f, fill="white")
            else:
                d.text((x, y), t, font=f, fill="white", stroke_width=6, stroke_fill=(20, 20, 30))
            x += w + (18 if h else 0)
        y += lh

def frame(i, sc):
    bg, zoom, fy, pose, face, label, ko, kofirst, sub = sc
    if bg and not os.path.exists(f"{HERE}/story1-bg/{bg}.jpg"):
        bg = {"bg1": "bg3"}.get(bg)   # fallback until the file arrives
    if bg:
        img = cover(f"{HERE}/story1-bg/{bg}.jpg", zoom, fy).convert("RGBA")
    else:
        img = Image.new("RGBA", (W, H), NAVY + (255,))
    grad(img, True, 420, 190); grad(img, False, 760, 235)
    d = ImageDraw.Draw(img)
    if not bg:
        f = font("Prompt-Medium.ttf", 54); t = "(รอภาพ bg4)"
        d.text(((W - d.textlength(t, font=f))/2, 700), t, font=f, fill=(150, 160, 210))
    # series tag
    ft = font("Prompt-SemiBold.ttf", 40); tag = "ซีรีส์ไม่ได้บอก · EP.1"; tw = d.textlength(tag, font=ft)
    d.rounded_rectangle([W/2-tw/2-28, 110, W/2+tw/2+28, 180], 35, fill=CORAL)
    d.text((W/2-tw/2, 116), tag, font=ft, fill="white")
    pill(d, label, 225, ko, kofirst)
    # mascot bottom-left (keeps clear of TikTok buttons on the right and caption at bottom)
    m = draw_nagaji(pose=pose, face=face, height=520)
    img.alpha_composite(m, (30, H - 230 - m.height))
    subtitle(d, sub, 1150)
    d.rectangle([0, H-10, W, H], fill=(60, 72, 120)); d.rectangle([0, H-10, W*(i+1)/len(SCENES), H], fill=YEL)
    return img.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]
    frames = [frame(i, s) for i, s in enumerate(SCENES)]
    tw, th = 360, 640; g = 24
    sheet = Image.new("RGB", (5*tw + 6*g, 2*th + 3*g), (245, 240, 232))
    for i, fr in enumerate(frames):
        r, c = divmod(i, 5)
        sheet.paste(fr.resize((tw, th), Image.LANCZOS), (g + c*(tw+g), g + r*(th+g)))
    sheet.save(out); frames[0].save(out.replace(".png", "-f1.png")); frames[5].save(out.replace(".png", "-f6.png"))
    print(out)
