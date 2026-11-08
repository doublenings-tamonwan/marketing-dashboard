"""ทำภาพหน้าปกคลิป 1080x1920 สไตล์ช่อง (หัวข้อ serif ตัวเอียง + แถบป้ายชมพู)

ตัวอย่าง:
    python3 office/editor/make_cover.py --photo me.jpg --out cover.png \
        --kicker "พามารีวิว · EP.1" --title "Moo Yoo\nRose House" \
        --pill "คาเฟ่ริมทะเลสาบ นครปฐม" --footer "a slow day by the lake" --xc 0.47

- รูปจะถูกครอปเป็น 9:16 รอบจุด --xc/--yc (0–1) และปรับโทนอุ่นนิด ๆ
- ข้อความวางช่วงกลาง เพราะกริดโปรไฟล์ TikTok โชว์แค่ช่วงกลาง 3:4
- หัวข้อ (--title) ใช้ Playfair Display ตัวเอียง = เหมาะกับภาษาอังกฤษ;
  ถ้าหัวข้อเป็นภาษาไทย ใส่ --thai-title จะใช้ Prompt SemiBold แทน
- รองรับ .heic (ต้องมี pillow-heif)
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

FONTS = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
W, H = 1080, 1920
PILL_BG = (255, 214, 231)
PILL_FG = (122, 14, 59)


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def load(path):
    if path.lower().endswith(".heic"):
        from pillow_heif import register_heif_opener
        register_heif_opener()
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def crop916(im, xc, yc):
    iw, ih = im.size
    ch, cw = ih, int(ih * 9 / 16)
    if cw > iw:
        cw, ch = iw, int(iw * 16 / 9)
    x0 = min(max(int(xc * iw - cw / 2), 0), iw - cw)
    y0 = min(max(int(yc * ih - ch / 2), 0), ih - ch)
    im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.95)
    r, g, b = im.split()
    return Image.merge("RGB", (r.point(lambda v: min(255, v + 6)), g,
                               b.point(lambda v: max(0, v - 6))))


def scrim():
    """ไล่เงาเข้มด้านบน-กลาง ให้ตัวหนังสือขาวอ่านออก"""
    stops = [(0.0, 0.05), (0.14, 0.45), (0.40, 0.30), (0.58, 0.0), (1.0, 0.0)]
    col = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        for (t0, a0), (t1, a1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                a = a0 + (a1 - a0) * (t - t0) / (t1 - t0)
                break
        col.putpixel((0, y), int(a * 255))
    layer = Image.new("RGBA", (W, H), (30, 20, 28, 0))
    layer.putalpha(col.resize((W, H)))
    return layer


def shadowed(base, xy, text, f, fill, anchor, blur=18, alpha=95, spacing=0):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).multiline_text((xy[0], xy[1] + 6), text, font=f, fill=(0, 0, 0, alpha),
                                      anchor=anchor, align="center", spacing=spacing)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(base).multiline_text(xy, text, font=f, fill=fill, anchor=anchor,
                                        align="center", spacing=spacing)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--kicker", default="")
    ap.add_argument("--title", required=True, help="ขึ้นบรรทัดใหม่ด้วย \\n")
    ap.add_argument("--pill", default="")
    ap.add_argument("--footer", default="")
    ap.add_argument("--xc", type=float, default=0.5)
    ap.add_argument("--yc", type=float, default=0.5)
    ap.add_argument("--thai-title", action="store_true")
    a = ap.parse_args()

    img = crop916(load(a.photo), a.xc, a.yc).convert("RGBA")
    img.alpha_composite(scrim())
    d = ImageDraw.Draw(img)
    cx, y = W // 2, 288

    if a.kicker:
        shadowed(img, (cx, y), a.kicker, font("Prompt-Medium.ttf", 39), "white", "mt")
        y += 39 + 30

    title = a.title.replace("\\n", "\n")
    tf = font("Prompt-SemiBold.ttf", 120) if a.thai_title else font("PlayfairDisplay-Italic.ttf", 144, 500)
    while d.multiline_textbbox((0, 0), title, font=tf, spacing=4)[2] > W - 120:
        tf = font(os.path.basename(tf.path), tf.size - 6, None if a.thai_title else 500)
    shadowed(img, (cx, y), title, tf, "white", "ma", blur=24, alpha=110, spacing=4)
    y = d.multiline_textbbox((cx, y), title, font=tf, anchor="ma", spacing=4)[3] + 36

    if a.pill:
        pf = font("Prompt-Medium.ttf", 45)
        tw = d.textlength(a.pill, font=pf)
        asc, desc = pf.getmetrics()
        h = asc + desc + 24
        d.rounded_rectangle((cx - tw / 2 - 48, y, cx + tw / 2 + 48, y + h), radius=h // 2, fill=PILL_BG)
        d.text((cx, y + h / 2), a.pill, font=pf, fill=PILL_FG, anchor="mm")

    if a.footer:
        shadowed(img, (cx, H - 276), a.footer, font("PlayfairDisplay-Italic.ttf", 45, 500),
                 "white", "md", blur=10, alpha=140)

    img.convert("RGB").save(a.out, quality=95)


if __name__ == "__main__":
    main()
