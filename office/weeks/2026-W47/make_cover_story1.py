"""หน้าปก ซีรีส์ไม่ได้บอก EP.1 (1080x1920; ตรวจกรอบ 3:4 กลางจอสำหรับกริดโปรไฟล์)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_mockframes as M
from PIL import Image, ImageDraw, ImageFont
from character import draw_nagaji
W, H = M.W, M.H
src = M.cover(f"{M.HERE}/story1-bg/bg3.jpg", 1.25, 0.45).convert("RGBA")
M.grad(src, True, 760, 230); M.grad(src, False, 900, 245)
d = ImageDraw.Draw(src)
ft = M.font("Prompt-SemiBold.ttf", 46); tag = "ซีรีส์ไม่ได้บอก · EP.1"; tw = d.textlength(tag, font=ft)
d.rounded_rectangle([W/2-tw/2-32, 290, W/2+tw/2+32, 370], 40, fill=M.CORAL); d.text((W/2-tw/2, 297), tag, font=ft, fill="white")
f1 = M.font("Prompt-SemiBold.ttf", 118); f2 = M.font("Prompt-SemiBold.ttf", 132)
def center(t, y, f, fill, stroke=10):
    w = d.textlength(t, font=f); d.text(((W-w)/2, y), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=M.NAVY)
center("ทำไมวันเกิด", 400, f1, "white")
center("ต้องกินซุปนี้?", 560, f2, M.YEL)
ko = ImageFont.truetype(M.KO, 64); kt = "미역국"; kw = d.textlength(kt, font=ko)
d.rounded_rectangle([W/2-kw/2-30, 760, W/2+kw/2+30, 850], 30, fill=M.YEL); d.text((W/2-kw/2, 770), kt, font=ko, fill=M.NAVY)
m = draw_nagaji(pose="point", face="surprised", height=760, outfit="school")
src.alpha_composite(m, (20, 1680 - m.height))
src.alpha_composite(M.doodles(0))
src.convert("RGB").save(sys.argv[1], quality=95)
src.crop((0, 240, W, 1680)).convert("RGB").resize((540, 720)).save(sys.argv[1].replace(".jpg", "-grid.jpg"))
