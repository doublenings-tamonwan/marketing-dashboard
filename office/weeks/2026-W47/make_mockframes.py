"""Mock frames: real AI backgrounds + mascot + labels, to preview the look before building the clip."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../editor"))
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from character import draw_nagaji
HERE = os.path.dirname(os.path.abspath(__file__))
F = HERE + "/../../assets/fonts/"; KO = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
def font(n, s): return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)
W, H = 1080, 1920
SHIFT = 230
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


import math
CREAMD = (255, 246, 225)
def _sticker(layer):
    """white rim + soft shadow so doodles pop on photos"""
    a = layer.split()[3]
    rim = Image.new("RGBA", layer.size, (255, 255, 255, 0)); rim.putalpha(a.filter(ImageFilter.MaxFilter(9)))
    sh = Image.new("RGBA", layer.size, (10, 15, 40, 0)); sh.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(8)).point(lambda v: v * 0.5))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (4, 6)); out.alpha_composite(rim); out.alpha_composite(layer)
    return out

def cloud(d, x, y, r, col):
    """Korean-style puffy cloud with swirl lines"""
    for dx, dy, rr in [(-r*1.2, r*0.25, r*0.75), (0, 0, r), (r*1.2, r*0.25, r*0.75)]:
        d.ellipse([x+dx-rr, y+dy-rr, x+dx+rr, y+dy+rr], fill=col)
    d.rounded_rectangle([x-r*2, y+r*0.1, x+r*2, y+r*0.95], r*0.42, fill=col)
    ln = (90, 110, 160)
    for dx, rr in [(-r*1.2, r*0.42), (0, r*0.55), (r*1.2, r*0.42)]:
        d.arc([x+dx-rr, y-rr*0.6, x+dx+rr, y+rr*1.4], 200, 340, fill=ln, width=5)
        d.arc([x+dx-rr*0.45, y+rr*0.1, x+dx+rr*0.45, y+rr*1.0], 180, 360, fill=ln, width=4)

def sparkle(d, x, y, r, col):
    pts = []
    for k in range(8):
        ang = math.pi/4*k; rr = r if k % 2 == 0 else r*0.28
        pts.append((x + rr*math.sin(ang), y - rr*math.cos(ang)))
    d.polygon(pts, fill=col)

def seaweed(d, x, y, h, col, w=34):
    left, right, mid = [], [], []
    for t in range(0, h, 6):
        cx = x + 26*math.sin(t/38); ww = w*(1 - t/h*0.75)/2
        left.append((cx-ww, y-t)); right.append((cx+ww, y-t)); mid.append((cx, y-t))
    d.polygon(left + right[::-1], fill=col)
    d.line(mid, fill=tuple(int(c*0.7) for c in col), width=4)

def party_hat(d, cx, top):
    d.polygon([(cx-62, top+150), (cx+62, top+150), (cx+8, top)], fill=(120, 190, 255))
    for k in range(3):
        yy = top + 45 + k*35
        d.line([(cx-25-k*14, yy+6), (cx+25+k*12, yy-6)], fill="white", width=12)
    d.ellipse([cx-10, top-26, cx+26, top+10], fill=YEL)

def doodles(i):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    cloud(d, 105, 520, 40, CREAMD); cloud(d, 985, 470, 34, CREAMD)
    sparkle(d, 930, 560, 34, YEL); sparkle(d, 990, 640, 18, YEL); sparkle(d, 160, 640, 22, YEL)
    seaweed(d, 930, 1730, 260, (70, 160, 90)); seaweed(d, 1005, 1730, 330, (95, 190, 110)); seaweed(d, 860, 1730, 170, (60, 140, 80), 28)
    if i in (0, 4, 8):
        party_hat(d, 340, 880)
    if i in (0, 1):
        d.text((470, 1000), "?" if i == 0 else "!?", font=font("Prompt-SemiBold.ttf", 150), fill=YEL)
    if i in (5,):
        d.text((470, 1010), "!", font=font("Prompt-SemiBold.ttf", 150), fill=YEL)
    return _sticker(L)

def frame(i, sc):
    bg, zoom, fy, pose, face, label, ko, kofirst, sub = sc
    if bg and not os.path.exists(f"{HERE}/story1-bg/{bg}.jpg"):
        bg = {"bg1": "bg3"}.get(bg)   # fallback until the file arrives
    if bg:
        src = cover(f"{HERE}/story1-bg/{bg}.jpg", zoom, fy)
        img = Image.new("RGBA", (W, H), NAVY + (255,))
        img.paste(src.crop((0, SHIFT, W, H)), (0, 0))   # lift subject above the mascot
        fill = src.crop((0, H - 300, W, H)).resize((W, SHIFT + 120)).filter(ImageFilter.GaussianBlur(30))
        fm = Image.linear_gradient("L").resize((W, SHIFT + 120)).point(lambda v: min(255, v * 3))
        img.paste(fill, (0, H - SHIFT - 120), fm)
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
    m = draw_nagaji(pose=pose, face=face, height=780, outfit="school")
    img.alpha_composite(m, (10, H - 190 - m.height))
    img.alpha_composite(doodles(i))
    subtitle(d, sub, 870)
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
