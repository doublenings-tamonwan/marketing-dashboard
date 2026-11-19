"""Storyboard: ทำไมในซีรีส์เกาหลี วันเกิดต้องกินซุปสาหร่าย? (มาสคอต น้องนางางิ)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../editor"))
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from character import draw_nagaji

F = os.path.join(os.path.dirname(__file__), "../../assets/fonts/")
KO = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
def font(n, s): return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)
def ko(s): return ImageFont.truetype(KO, s)

PW, PH = 420, 747          # panel 9:16
GAP, M = 40, 60
COLS, ROWS = 5, 2
CAP = 330
W = M*2 + COLS*PW + (COLS-1)*GAP
H = 230 + ROWS*(PH+CAP) + (ROWS-1)*GAP + 40
INK = (30, 26, 40)
NAVY = (22, 30, 66); NAVY2 = (34, 46, 96)
PINK = (255, 209, 102); DPINK = (22, 30, 66)   # pill = butter yellow + navy text
CORAL = (255, 99, 99); CREAM = (255, 246, 230); STEAM = (190, 205, 240)

def bowl(d, cx, cy, s=1.0):
    w = int(150*s)
    d.ellipse([cx-w, cy-30*s, cx+w, cy+30*s], fill=(250,245,235), outline=INK, width=5)
    d.pieslice([cx-w, cy-w*0.9, cx+w, cy+w*0.9], 0, 180, fill=(255,255,255), outline=INK, width=5)
    d.ellipse([cx-w+12, cy-24*s, cx+w-12, cy+24*s], fill=(120,95,60))
    for i in range(-2, 3):  # seaweed strands
        x = cx + i*40*s
        d.line([(x, cy-10*s), (x+15*s, cy+8*s)], fill=(40,80,40), width=8)
    for i in (-1, 0, 1):  # steam
        x = cx + i*55*s
        d.arc([x-20, cy-150*s, x+20, cy-90*s], 90, 270, fill=STEAM, width=6)
        d.arc([x-20, cy-100*s, x+20, cy-40*s], 270, 90, fill=STEAM, width=6)

def heart(d, cx, cy, r, col=CORAL):
    d.ellipse([cx-r, cy-r, cx, cy], fill=col); d.ellipse([cx, cy-r, cx+r, cy], fill=col)
    d.polygon([(cx-r+2, cy-r/2+8), (cx+r-2, cy-r/2+8), (cx, cy+r)], fill=col)

def qmark(d, x, y, s=120):
    d.text((x, y), "?", font=font("Prompt-SemiBold.ttf", s), fill=PINK, stroke_width=6, stroke_fill=NAVY)

def baby(d, cx, cy):
    d.rounded_rectangle([cx-110, cy-40, cx+110, cy+70], 50, fill=(255,240,200), outline=INK, width=5)
    d.ellipse([cx-150, cy-80, cx-40, cy+30], fill=(255,225,200), outline=INK, width=5)
    d.arc([cx-125, cy-40, cx-105, cy-25], 200, 340, fill=INK, width=4)
    d.arc([cx-90, cy-40, cx-70, cy-25], 200, 340, fill=INK, width=4)
    d.ellipse([cx-135, cy-20, cx-115, cy-8], fill=(255,170,180))

def whale(d, cx, cy):
    col=(120,170,220)
    d.polygon([(cx+110, cy+10), (cx+175, cy-60), (cx+150, cy+5), (cx+185, cy+60)], fill=col, outline=INK)
    d.ellipse([cx-170, cy-75, cx+140, cy+80], fill=col, outline=INK, width=6)
    d.chord([cx-160, cy-5, cx+130, cy+80], 0, 180, fill=(215,232,250))
    d.ellipse([cx-115, cy-25, cx-97, cy-7], fill=INK)
    d.arc([cx-150, cy-5, cx-90, cy+25], 20, 160, fill=INK, width=4)
    for i in range(4):
        x = cx - 70 + i*50
        d.line([(x, cy+35), (x+12, cy+68)], fill=(40,110,60), width=9)
    for dx in (-25, 0, 25):
        d.line([(cx-40, cy-78), (cx-40+dx, cy-130)], fill=(150,200,240), width=8)
    d.ellipse([cx+150, cy+40, cx+195, cy+85], fill=(255,225,200), outline=INK, width=4)

def paper(d, cx, cy):
    d.rounded_rectangle([cx-85, cy-110, cx+85, cy+110], 12, fill="white", outline=INK, width=5)
    for i in range(5):
        d.line([(cx-70, cy-80+i*35), (cx+40, cy-80+i*35)], fill=(200,200,210), width=6)
    d.line([(cx-60, cy-60), (cx+60, cy+80)], fill=(230,50,70), width=16)
    d.line([(cx+60, cy-60), (cx-60, cy+80)], fill=(230,50,70), width=16)

def follow_btn(d, cx, cy):
    d.rounded_rectangle([cx-150, cy-45, cx+150, cy+45], 45, fill=CORAL)
    t = "+ กดติดตาม"; f = font("Prompt-SemiBold.ttf", 44)
    w = d.textlength(t, font=f); d.text((cx-w/2, cy-32), t, font=f, fill="white")

def onscreen(img, text, y, size=44, korean=None, kofirst=False):
    d = ImageDraw.Draw(img)
    f = font("Prompt-SemiBold.ttf", size)
    rows = [[(t, f)] for t in text.split("\n")]
    if korean:
        k = (korean, ko(size))
        if kofirst: rows.insert(0, [k])
        else: rows[-1].append(("  " + korean, ko(size)))
    lh = size + 22
    tw = max(sum(d.textlength(t, font=ff) for t, ff in r) for r in rows)
    x0 = (PW - tw)/2
    d.rounded_rectangle([x0-22, y-10, x0+tw+22, y+lh*len(rows)+8], 22, fill=PINK, outline=DPINK, width=4)
    for i, r in enumerate(rows):
        rw = sum(d.textlength(t, font=ff) for t, ff in r); x = (PW-rw)/2
        for t, ff in r:
            d.text((x, y+i*lh), t, font=ff, fill=DPINK); x += d.textlength(t, font=ff)
    return y + lh*len(rows) + 8

PANELS = [
  dict(t="0–3 วิ", pose="stand", face="surprised", text="วันเกิดในซีรีส์เกาหลี\nต้องมีซุปนี้ทุกที!", prop="hook",
       vo="สังเกตไหม ซีรีส์เกาหลี วันเกิดทีไร ต้องมีซุปนี้ทุกที", note="ฮุก: ชามซุปซูมเข้าแรง + เสียงตึ้ง"),
  dict(t="3–6 วิ", pose="wave", face="wink", text="แต่ถ้ากินวันสอบ…\nสอบตก!?", prop="paper",
       vo="แต่ถ้ากินวันสอบ… คนเกาหลีบอกว่าสอบตก! เดี๋ยวเล่าให้ฟัง", note="เปิดปมไว้ คนดูต้องดูถึงท้าย"),
  dict(t="6–11 วิ", pose="point", face="talk", text="มิยอกกุก", ko="미역국", prop="bowl",
       vo="เมนูนี้ชื่อ \"มิยอกกุก\" ซุปสาหร่ายของเกาหลี", note="ชื่อเมนู ไทย + เกาหลี"),
  dict(t="11–18 วิ", pose="stand", face="smile", text="อาหารแม่หลังคลอด", prop="baby",
       vo="ตอนแม่คลอดลูกใหม่ ๆ จะกินซุปนี้ต่อกันหลายอาทิตย์ เชื่อกันว่าช่วยบำรุงแม่", note="! ต้องพูดว่า \"เชื่อกันว่า\""),
  dict(t="18–25 วิ", pose="cheer", face="happy", text="วันเกิด = ระลึกถึงแม่", prop="heart",
       vo="พอถึงวันเกิด ก็กินเพื่อนึกถึงวันที่แม่คลอดเรา… ซึ้งปะล่ะ", note="จุดอารมณ์ของคลิป"),
  dict(t="25–33 วิ", pose="stand", face="surprised", text="เรื่องเล่าสมัยโชซอน", prop="whale",
       vo="มีเรื่องเล่าสมัยโชซอนด้วยนะ ว่าเคยเห็นวาฬที่เพิ่งคลอดลูก ท้องเต็มไปด้วยสาหร่าย", note="! เล่าเป็น \"เรื่องเล่า\" เท่านั้น"),
  dict(t="33–40 วิ", pose="point", face="talk", text="ลื่น = สอบตก", prop="slip",
       vo="ส่วนวันสอบห้ามกินเด็ดขาด เพราะสาหร่ายมันลื่น… ความรู้ลื่นหลุดไปด้วย", note="เฉลยปมจากฉาก 2"),
  dict(t="40–47 วิ", pose="point", face="talk", text="= สอบตก", ko="미역국을 먹다", kofirst=True, prop="ko",
       vo="ขนาดคำว่า \"กินซุปสาหร่าย\" ยังแปลว่าสอบตกเลย", note="สำนวนเกาหลี (ไม่เล่าที่มา)"),
  dict(t="47–55 วิ", pose="wave", face="smile", text="ซีรีส์ไหนมีฉากนี้?", prop="follow",
       vo="ซีรีส์เรื่องไหนมีฉากกินซุปนี้ เมนต์บอกหน่อย ตอนหน้าเล่าเรื่องโซจูต่อ กดติดตามไว้นะ", note="ชวนเมนต์ + บอก EP หน้า"),
]

def panel(p, i):
    img = Image.new("RGB", (PW, PH), NAVY)
    d = ImageDraw.Draw(img)
    for y in range(PH):  # vertical gradient
        t = y / PH
        d.line([(0, y), (PW, y)], fill=tuple(int(NAVY[k]*(1-t) + NAVY2[k]*t) for k in range(3)))
    import random; rnd = random.Random(i)
    for _ in range(26):  # tiny stars
        x, y, r = rnd.randint(0, PW), rnd.randint(0, PH), rnd.choice([2, 2, 3])
        d.ellipse([x-r, y-r, x+r, y+r], fill=(120, 140, 200))
    # series tag
    ft = font("Prompt-SemiBold.ttf", 22); tag = "ซีรีส์ไม่ได้บอก · EP.1"
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle([PW/2-tw/2-14, 14, PW/2+tw/2+14, 50], 18, fill=CORAL)
    d.text((PW/2-tw/2, 16), tag, font=ft, fill="white")
    # progress bar
    d.rounded_rectangle([0, PH-8, PW, PH], 0, fill=(60, 72, 120))
    d.rectangle([0, PH-8, PW*(i+1)/len(PANELS), PH], fill=PINK)
    # prop area (upper half)
    pr = p["prop"]; cx, cy = PW//2, 300
    if pr == "hook": bowl(d, cx-40, cy+30, 0.65); qmark(d, 300, 175, 100)
    elif pr == "bowl": bowl(d, cx, cy+20, 0.8)
    elif pr == "baby": baby(d, cx+30, cy); heart(d, 330, 200, 30)
    elif pr == "heart": heart(d, cx, cy, 90); heart(d, 90, 220, 28); heart(d, 340, 330, 22)
    elif pr == "whale": whale(d, cx-15, cy)
    elif pr == "paper": paper(d, cx, cy+30)
    elif pr == "ko": bowl(d, cx, cy+50, 0.6)
    elif pr == "follow": follow_btn(d, cx, cy)
    elif pr == "slip":
        bowl(d, cx-80, cy+50, 0.5); paper(d, cx+80, cy+20)
    onscreen(img, p["text"], 66, 40 if p.get("ko") else 42, p.get("ko"), p.get("kofirst", False))
    # mascot bottom
    m = draw_nagaji(pose=p["pose"], face=p["face"], height=350)
    img.paste(m, ((PW - m.width)//2, PH - m.height + 10), m)
    # number badge
    d.ellipse([14, PH-80, 74, PH-20], fill=CORAL)
    n = str(i+1); f = font("Prompt-SemiBold.ttf", 36)
    d.text((44 - d.textlength(n, font=f)/2, PH-76), n, font=f, fill="white")
    return img

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def main(out):
    W_, H_ = W, H
    can = Image.new("RGB", (W_, H_), CREAM)
    d = ImageDraw.Draw(can)
    d.text((M, 50), "Storyboard v2 · น้องนางางิเล่าเรื่อง EP.1", font=font("Prompt-SemiBold.ttf", 64), fill=NAVY)
    d.text((M, 140), "ทำไมในซีรีส์เกาหลี วันเกิดต้องกินซุปสาหร่าย?   ·   ยาว ~55 วิ   ·   โทนกรมท่า-เหลือง-ปะการัง   ·   เสียงพากย์: เจ้าของช่องอัดเอง (บทเป็นแนวทาง พูดตามสบาย)",
           font=font("Prompt-Medium.ttf", 32), fill=INK)
    fb = font("Prompt-SemiBold.ttf", 30); fv = font("Prompt-Medium.ttf", 27); fn = font("Prompt-Medium.ttf", 24)
    for i, p in enumerate(PANELS):
        r, c = divmod(i, COLS)
        x = M + c*(PW+GAP); y = 230 + r*(PH+CAP+GAP)
        sh = Image.new("RGBA", (PW+40, PH+40), (0,0,0,0))
        ImageDraw.Draw(sh).rounded_rectangle([20, 26, PW+20, PH+26], 28, fill=(20,25,60,90))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); can.paste(sh, (x-20, y-20), sh)
        pi = panel(p, i); mask = Image.new("L", pi.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, PW, PH], 28, fill=255)
        can.paste(pi, (x, y), mask)
        ty = y + PH + 18
        d.text((x, ty), p["t"], font=fb, fill=CORAL)
        ty += 46
        for ln in wrap(d, "🎙 " .replace("🎙 ", "พูด: ") + p["vo"], fv, PW):
            d.text((x, ty), ln, font=fv, fill=INK); ty += 40
        d.text((x, ty + 6), p["note"], font=fn, fill=(110, 110, 140))
    # legend in the 10th slot
    x = M + 4*(PW+GAP); y = 230 + (PH+CAP+GAP)
    d.rounded_rectangle([x, y, x+PW, y+PH], 28, fill="white", outline=(225, 220, 210), width=3)
    fh = font("Prompt-SemiBold.ttf", 32); fl = font("Prompt-Medium.ttf", 25)
    d.text((x+28, y+28), "โทนสีใหม่", font=fh, fill=NAVY)
    for k, (c, n) in enumerate([(NAVY, "กรมท่า (พื้น)"), (PINK, "เหลืองเนย (ป้าย)"), (CORAL, "แดงปะการัง (เน้น)")]):
        yy = y + 90 + k*58
        d.rounded_rectangle([x+28, yy, x+78, yy+42], 10, fill=c, outline=(200, 200, 200))
        d.text((x+94, yy+4), n, font=fl, fill=INK)
    d.text((x+28, y+290), "ทำให้แมสขึ้น", font=fh, fill=NAVY)
    tips = ["2 วิแรกเปิดปม \"กินวันสอบ = สอบตก?\"", "เปลี่ยนภาพทุก 2–3 วิ", "ป้ายชื่อซีรีส์ \"ซีรีส์ไม่ได้บอก\"",
            "แถบความคืบหน้าล่างจอ", "ปิดด้วยคำถาม + บอก EP หน้า"]
    yy = y + 345
    for t in tips:
        for ln in wrap(d, "• " + t, fl, PW-56):
            d.text((x+28, yy), ln, font=fl, fill=INK); yy += 38
        yy += 6
    can.save(out); print(out, can.size)

if __name__ == "__main__":
    main(sys.argv[1])
