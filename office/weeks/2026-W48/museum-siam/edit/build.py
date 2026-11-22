"""Build 3 Museum Siam clips (W48). Usage: python3 build.py [clip1|clip2|clip3|cover|all]"""
import json, os, subprocess, sys, glob
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

U = "/root/.claude/uploads/4c923d2c-8f5d-5971-8899-b8d14570e947"
OUT = "/tmp/claude-0/-home-user-marketing-dashboard/4c923d2c-8f5d-5971-8899-b8d14570e947/scratchpad/museum/edit"
ED = "/home/user/marketing-dashboard/office/editor"
FONTS = "/home/user/marketing-dashboard/office/assets/fonts"
W, H, FPS = 1080, 1920, 30
VF = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1"
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-an"]


def run(cmd):
    subprocess.run(cmd, check=True)


def mov(n):
    return glob.glob(f"{U}/*IMG_{n}.mov")[0]


def vshot(out, n, ss, dur_out, speed=1.0, extra=""):
    """cut from source n at ss; speed<1 = slow motion; dur_out = output seconds"""
    vf = (f"setpts={1/speed:.5f}*PTS," if speed != 1 else "") + VF + (("," + extra) if extra else "")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(ss), "-i", mov(n), "-vf", vf,
         "-frames:v", str(round(dur_out * FPS))] + ENC + [out])


def frames_to_mp4(out, frames_iter, nframes):
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf", "format=yuv420p,setsar=1",
                          "-frames:v", str(nframes)] + ENC + [out], stdin=subprocess.PIPE)
    for im in frames_iter:
        p.stdin.write(im.tobytes())
    p.stdin.close()
    assert p.wait() == 0


def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def crop_rect(im, xc, yc, aspect):
    """largest rect of given w/h aspect centred near (xc,yc) (0-1)"""
    iw, ih = im.size
    ch = ih; cw = ch * aspect
    if cw > iw:
        cw = iw; ch = cw / aspect
    x0 = min(max(xc * iw - cw / 2, 0), iw - cw)
    y0 = min(max(yc * ih - ch / 2, 0), ih - ch)
    return (x0, y0, cw, ch)


def zoom_rect(rect, z, fx, fy, im):
    """shrink rect by factor z toward focus (fx,fy in image px), keep inside rect"""
    x0, y0, cw, ch = rect
    nw, nh = cw / z, ch / z
    nx = min(max(fx - nw / 2, x0), x0 + cw - nw)
    ny = min(max(fy - nh / 2, y0), y0 + ch - nh)
    return (nx, ny, nx + nw, ny + nh)


def ease(p):
    return p * p * (3 - 2 * p)


def zcurve(i, n, zoom, punch):
    if punch:  # ซูมกระแทก: เข้าเต็มใน 0.15 วิ แล้วค้าง
        return 1 + (zoom - 1) * ease(min(1.0, i / (0.15 * FPS)))
    return 1 + (zoom - 1) * ease(i / max(1, n - 1))


def flash(im, i, nflash=5):
    if i >= nflash:
        return im
    a = 0.85 * (1 - i / nflash)
    return Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), a)


def still_full(out, path, dur, xc, yc, zoom, fx, fy, do_flash=True, punch=False):
    """9:16 crop + slow zoom toward (fx,fy) (0-1 of image) + white flash first 5 frames"""
    im = load(path)
    iw, ih = im.size
    rect = crop_rect(im, xc, yc, 9 / 16)
    n = round(dur * FPS)

    def gen():
        for i in range(n):
            z = zcurve(i, n, zoom, punch)
            box = zoom_rect(rect, z, fx * iw, fy * ih, im)
            fr = im.resize((W, H), Image.LANCZOS, box=box)
            yield flash(fr, i) if do_flash else fr
    frames_to_mp4(out, gen(), n)


def selfie_layout(band_top, band_h, xc=0.46):
    """landscape selfie -> band (full width, all 3 people) on blurred fill"""
    im = load(f"{U}/08f4ef5d-image.jpg")
    iw, ih = im.size
    rect = crop_rect(im, xc, 0.5, W / band_h)
    r = crop_rect(im, 0.44, 0.5, 9 / 16)
    bg = im.resize((W, H), Image.LANCZOS, box=(r[0], r[1], r[0] + r[2], r[1] + r[3]))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (40, 30, 30)), 0.25)
    return im, rect, bg


def selfie_shot(out, dur, band_top=110, band_h=880, zoom=1.08, punch=False):
    im, rect, bg = selfie_layout(band_top, band_h)
    iw, ih = im.size
    n = round(dur * FPS)
    fx, fy = 0.44 * iw, 0.45 * ih  # owner's face

    def gen():
        for i in range(n):
            z = zcurve(i, n, zoom, punch)
            box = zoom_rect(rect, z, fx, fy, im)
            band = im.resize((W, band_h), Image.LANCZOS, box=box)
            fr = bg.copy()
            fr.paste(band, (0, band_top))
            yield fr
    frames_to_mp4(out, gen(), n)


def selfie_punch(out, dur, band_top=110, band_h=880, zoom=1.15):
    """ซูมกระแทกแบบไม่ตัดเพื่อน: แถบภาพเริ่มเล็ก (1/zoom) แล้วขยายเต็มกว้างใน 0.15 วิ แล้วค้าง
    จุดหน้าเจ้าของช่องอยู่ที่เดิมบนจอ"""
    im, rect, bg = selfie_layout(band_top, band_h)
    x0, y0, cw, ch = rect
    band = im.resize((W, band_h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    iw, ih = im.size
    ax = (0.44 * iw - x0) / cw * W          # owner face on screen (final)
    ay = band_top + (0.45 * ih - y0) / ch * band_h
    n = round(dur * FPS)
    # ขอบแถบนุ่มด้วยเงา
    def gen():
        for i in range(n):
            sc = (1 / zoom) * zcurve(i, n, zoom, True)
            bw, bh = round(W * sc), round(band_h * sc)
            b = band.resize((bw, bh), Image.LANCZOS) if sc < 0.999 else band
            px = round(ax - (ax / W) * bw); py = round(ay - (ay - band_top) / band_h * bh)
            fr = bg.copy(); fr.paste(b, (px, py))
            yield fr
    frames_to_mp4(out, gen(), n)


def concat(parts, out):
    lst = out + ".txt"
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])


def audio(d, dur, mood, pops, sfx_cues):
    run(["python3", f"{ED}/make_music.py", "--mood", mood, "--duration", str(dur), "--out", f"{d}/music.wav",
         "--pops", ",".join(str(p) for p in pops)])
    run(["python3", f"{ED}/sfx.py", "--duration", str(dur), "--cues", sfx_cues, "--out", f"{d}/sfx.wav"])
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{d}/music.wav", "-i", f"{d}/sfx.wav", "-filter_complex",
         "[1:a]volume=0.5,aformat=channel_layouts=stereo[s];[0:a]aformat=channel_layouts=stereo[m];"
         f"[m][s]amix=inputs=2:normalize=0:duration=first,afade=t=out:st={dur-0.6}:d=0.6,"
         "alimiter=limit=0.8:level=false[a]", "-map", "[a]", "-ar", "44100", "-t", str(dur), f"{d}/mix.wav"])


def glow(d, src, dst, s):
    run(["bash", f"{ED}/glow.sh", f"{d}/{src}", f"{d}/{dst}", str(s)])


def burn(d, video, name, extra=()):
    run(["python3", f"{ED}/burn_subs.py", "--video", f"{d}/{video}", "--subs", f"{d}/subs.json",
         "--out", f"{OUT}/{name}-preview.mp4", "--audio", f"{d}/mix.wav", *extra])


def write_subs(d, subs):
    json.dump(subs, open(f"{d}/subs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------- clip 1 ----------------
def clip1():
    d = f"{OUT}/clip1"; os.makedirs(d, exist_ok=True)
    vshot(f"{d}/s1.mp4", "0745", 0.0, 1.2)
    vshot(f"{d}/s2.mp4", "0745", 2.5, 1.0)
    # IMG_0744: crop around flower-shirt mannequin, slow zoom toward water gun
    still_full(f"{d}/s3.mp4", f"{U}/e428de5b-image.jpg", 6.8, xc=0.62, yc=0.5, zoom=1.22, fx=0.66, fy=0.52)
    concat([f"{d}/s{i}.mp4" for i in (1, 2, 3)], f"{d}/base.mp4")
    glow(d, "base.mp4", "base-glow.mp4", 0.12)
    write_subs(d, [
        {"start": 0.0, "end": 1.2, "text": "เมื่อแม่บอกให้\n[ใส่ชุดไทย]ไปงาน"},
        {"start": 1.2, "end": 2.2, "text": "แม่หมายถึง\nลุค[ทางการ]แบบนี้"},
        {"start": 2.2, "end": 5.2, "text": "ใส่แล้วค่ะแม่\nชุดไทยฉบับ[สงกรานต์]"},
        {"start": 5.2, "end": 9.0, "text": "ส่งให้เพื่อนที่\n[ใส่ลุคนี้]ทุกเมษา"},
    ])
    audio(d, 9.0, "cute", [0.0, 1.2, 2.5, 5.2], "whoosh@2.0")
    burn(d, "base-glow.mp4", "clip1-thai-dress")


# ---------------- clip 2 ----------------
def clip2():
    d = f"{OUT}/clip2"; os.makedirs(d, exist_ok=True)
    vshot(f"{d}/s1.mp4", "0766", 4.7, 2.0)
    vshot(f"{d}/s2.mp4", "0765", 1.0, 2.5)
    vshot(f"{d}/s3.mp4", "0765", 5.0, 2.5)
    vshot(f"{d}/s4.mp4", "0765", 7.5, 2.0)
    # 3 names: source 12.0-14.8 at 0.8x -> 3.5s (source only has 2.0s in script's ranges)
    vshot(f"{d}/s5.mp4", "0765", 12.0, 1.0, speed=0.8)
    vshot(f"{d}/s6.mp4", "0765", 12.8, 1.0, speed=0.8)
    vshot(f"{d}/s7.mp4", "0765", 13.6, 1.5, speed=0.8)
    vshot(f"{d}/s8.mp4", "0766", 5.0, 2.0, speed=0.85)
    concat([f"{d}/s{i}.mp4" for i in range(1, 9)], f"{d}/base.mp4")
    glow(d, "base.mp4", "base-glow.mp4", 0.12)
    T = "top"
    write_subs(d, [
        {"start": 0.0, "end": 2.0, "text": "มิวเซียมเขียนไว้เลย\nส้มตำ[ไม่รู้ของใคร]", "pos": T},
        {"start": 2.0, "end": 4.5, "text": "ตัวเอกของจานนี้\nคือ[มะละกอ]", "pos": T},
        {"start": 4.5, "end": 7.0, "text": "มาจากทวีป[อเมริกา]\nถึงไทยสมัยอยุธยา", "pos": T},
        {"start": 7.0, "end": 9.0, "text": "แต่ยังไม่มีหลักฐาน\nว่าคนอยุธยา[กินส้มตำ]", "pos": T},
        {"start": 9.0, "end": 10.0, "text": "ลาวเรียก\n[ตำส้ม]", "pos": T},
        {"start": 10.0, "end": 11.0, "text": "ไทยเรียก\n[ส้มตำ]", "pos": T},
        {"start": 11.0, "end": 12.5, "text": "ชาวโลกเรียกเล่น ๆ\n[ปาปาย่า ป๊อก ป๊อก]", "pos": T},
        {"start": 12.5, "end": 14.5, "text": "เรียกอะไรก็อร่อย\nสั่ง[พริก]กี่เม็ด เมนต์มา", "pos": T},
    ])
    audio(d, 14.5, "cute", [0.0, 3.9, 4.5, 7.0, 9.0, 10.0, 11.0, 12.5], "whoosh@1.8,whoosh@8.8,pop@11.0")
    burn(d, "base-glow.mp4", "clip2-somtam")


# ---------------- clip 3 ----------------
def pill(d, xy, text, f, bg, fg, padx=22, pady=10):
    l, t, r, b = d.textbbox((0, 0), text, font=f, anchor="ls")
    asc, desc = f.getmetrics()
    w = r - l
    x, y = xy
    d.rounded_rectangle((x, y, x + w + 2 * padx, y + asc + desc + 2 * pady), radius=(asc + desc) // 2 + pady, fill=bg)
    d.text((x + padx, y + pady + asc), text, font=f, fill=fg, anchor="ls")
    return w + 2 * padx, asc + desc + 2 * pady


def F(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}", size, layout_engine=ImageFont.Layout.RAQM)


PINK_BG, PINK_FG = (255, 214, 231, 255), (122, 14, 59, 255)


def make_badge(path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = F("Prompt-Medium.ttf", 34)
    w, h = pill(ImageDraw.Draw(im), (48, 200), "พามารีวิว · EP.2", f, (255, 246, 240, 235), PINK_FG)
    ImageDraw.Draw(sh).rounded_rectangle((48, 204, 48 + w, 204 + h), radius=h // 2, fill=(0, 0, 0, 90))
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), im)
    out.save(path)


def make_card(path):
    """info card 1080x1920 transparent; card body y≈290..~1100"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    X0, X1, Y0 = 56, W - 56, 285
    PAD = 36
    title_f = F("Prompt-SemiBold.ttf", 68)
    lab_f = F("Prompt-SemiBold.ttf", 36)
    val_size = 40
    rows = [("ที่ตั้ง", ["ถ.สนามไชย เขตพระนคร", "(ใกล้วัดโพธิ์)"]),
            ("เดินทาง", ["MRT สนามไชย ทางออก 1"]),
            ("เปิด", ["อังคาร–อาทิตย์ 10:00–18:00", "(ปิดวันจันทร์)"]),
            ("ค่าเข้า", ["ผู้ใหญ่ 100 · นักเรียน/นักศึกษา 50", "เด็กต่ำกว่า 15 ปี / ผู้สูงอายุ 60+ เข้าฟรี"])]
    note = ["ไปมาเมื่อ ธ.ค. 68 · ราคา/นิทรรศการอาจเปลี่ยน", "เช็กเพจก่อนไป"]
    LABW = 176  # label pill column
    valw = X1 - X0 - 2 * PAD - LABW - 18
    while True:
        val_f = F("Prompt-Medium.ttf", val_size)
        if max(val_f.getlength(t) for _, v in rows for t in v) <= valw:
            break
        val_size -= 1
    note_f = F("Prompt-Medium.ttf", 31)
    asc, desc = val_f.getmetrics(); LH = int((asc + desc) * 1.05)
    nasc, ndesc = note_f.getmetrics(); NLH = int((nasc + ndesc) * 1.1)
    # layout height
    y = Y0 + PAD
    ta, td = title_f.getmetrics()
    title_h = ta + td
    body_h = sum(LH * len(v) for _, v in rows) + 16 * (len(rows) - 1)
    total = PAD + title_h + 18 + 3 + 22 + body_h + 34 + NLH * len(note) + PAD
    Y1 = Y0 + total
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((X0, Y0 + 10, X1, Y1 + 10), radius=44, fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((X0, Y0, X1, Y1), radius=44, fill=(255, 250, 246, 246))
    d.text((W // 2, y + ta), "มิวเซียมสยาม", font=title_f, fill=PINK_FG, anchor="ms")
    y += title_h + 18
    d.rounded_rectangle((W // 2 - 60, y, W // 2 + 60, y + 6), radius=3, fill=(255, 150, 190, 255))
    y += 3 + 22
    for lab, vals in rows:
        # label pill vertically aligned with first value line
        la, ld = lab_f.getmetrics()
        lw = lab_f.getlength(lab)
        ph = la + ld + 12
        py = y + (LH - ph) // 2
        d.rounded_rectangle((X0 + PAD, py, X0 + PAD + LABW, py + ph), radius=ph // 2, fill=PINK_BG)
        d.text((X0 + PAD + LABW // 2, py + 6 + la), lab, font=lab_f, fill=PINK_FG, anchor="ms")
        vx = X0 + PAD + LABW + 18
        for k, v in enumerate(vals):
            d.text((vx, y + k * LH + (LH - asc - desc) // 2 + asc), v, font=val_f, fill=(45, 35, 40, 255), anchor="ls")
        y += LH * len(vals) + 16
    y += 34 - 16
    d.line((X0 + PAD, y - 14, X1 - PAD, y - 14), fill=(235, 215, 222, 255), width=2)
    for k, t in enumerate(note):
        d.text((W // 2, y + k * NLH + nasc), t, font=note_f, fill=(120, 95, 105, 255), anchor="ms")
    im.save(path)
    return Y0, Y1, val_size


def clip3():
    """v2 (22 พ.ย.): เปิดรัว 1 วิ -> เซลฟี่ซูมกระแทก -> ... ทุกช็อต <= 2 วิ ยกเว้นการ์ด 5 วิ"""
    d = f"{OUT}/clip3"; os.makedirs(d, exist_ok=True)
    m = 5 / FPS  # 5 เฟรม = 0.167 วิ ต่อภาพ
    vshot(f"{d}/m1.mp4", "0736", 1.0, m)
    still_full(f"{d}/m2.mp4", f"{U}/b0c09462-image.jpg", m, xc=0.52, yc=0.5, zoom=1.0, fx=0.53, fy=0.33, do_flash=False)
    vshot(f"{d}/m3.mp4", "0751", 0.5, m)
    vshot(f"{d}/m4.mp4", "0765", 3.5, m)
    vshot(f"{d}/m5.mp4", "0726", 0.5, m)
    vshot(f"{d}/m6.mp4", "0757", 10.5, m)
    selfie_punch(f"{d}/s1.mp4", 2.0, zoom=1.15)
    vshot(f"{d}/s2.mp4", "0736", 0.0, 1.5)
    still_full(f"{d}/s3.mp4", f"{U}/b0c09462-image.jpg", 1.5, xc=0.52, yc=0.5, zoom=1.2, fx=0.53, fy=0.30,
               do_flash=False, punch=True)
    vshot(f"{d}/s4.mp4", "0729", 0.0, 1.5)
    vshot(f"{d}/s5.mp4", "0751", 0.0, 1.5)
    vshot(f"{d}/s6.mp4", "0765", 1.8, 1.5)
    vshot(f"{d}/s7.mp4", "0757", 8.0, 5.0, extra="gblur=sigma=26,eq=brightness=-0.06:saturation=0.9")
    parts = [f"{d}/m{i}.mp4" for i in range(1, 7)] + [f"{d}/s{i}.mp4" for i in range(1, 8)]
    concat(parts, f"{d}/base.mp4")
    glow(d, "base.mp4", "base-glow.mp4", 0.2)
    O = 1.0  # เลื่อนทุกอย่างหลังช่วงรัว
    CARD = 10.5
    bursts = ",".join(str(round(t + O, 2)) for t in (0, 2.0, 3.5, 5.0, 6.5, 8.0, 9.5))
    run(["python3", f"{ED}/sparkles.py", "--video", f"{d}/base-glow.mp4", "--out", f"{d}/base-fx.mp4",
         "--bursts", bursts])
    make_badge(f"{d}/badge.png")
    y0, y1, vs = make_card(f"{d}/card.png")
    print("card", y0, y1, "value font", vs)
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{d}/base-fx.mp4", "-loop", "1", "-i", f"{d}/badge.png",
         "-loop", "1", "-t", "5.0", "-i", f"{d}/card.png", "-filter_complex",
         f"[2:v]format=rgba,fade=in:st=0:d=0.25:alpha=1,setpts=PTS+{CARD}/TB[c];"
         "[0:v][1:v]overlay=0:0:shortest=1[b];"
         f"[b][c]overlay=x=0:y='max(0\\,({CARD + 0.25}-t)*160)':eof_action=pass:eval=frame,format=yuv420p[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", f"{d}/base-card.mp4"])
    write_subs(d, [
        {"start": 1.0, "end": 3.0, "text": "พามารีวิว… [ว้าวทุกห้อง]!\nมิวเซียมสยาม"},
        {"start": 3.0, "end": 4.5, "text": "งาน[ทอง]\nผนังลายไทยแดงทั้งห้อง"},
        {"start": 4.5, "end": 6.0, "text": "นางกวัก[ไซซ์ยักษ์]\nกวักให้มาเที่ยว", "y": 1120},
        {"start": 6.0, "end": 7.5, "text": "เข้าโซน\n[ไทยแปลไทย]"},
        {"start": 7.5, "end": 9.0, "text": "ตุ๊กตา[ชุดไทย]\nครบทุกสี"},
        {"start": 9.0, "end": 10.5, "text": "โต๊ะที่[ส้มตำ]\nโผล่ขึ้นมาเอง"},
        {"start": 10.5, "end": 15.5, "text": "[เซฟ]ไว้ไปวันหยุด"},
    ])
    audio(d, 15.5, "chill", [1.0, 4.5, 10.0, 10.5], "whoosh@0.8,whoosh@2.8,whoosh@4.3")
    burn(d, "base-card.mp4", "clip3-museum-ep2")


def cover():
    d = f"{OUT}/clip3"; os.makedirs(d, exist_ok=True)
    band_top, band_h = 830, 860
    im, rect, bg = selfie_layout(band_top, band_h)
    x0, y0, cw, ch = rect
    band = im.resize((W, band_h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    fr = bg.copy(); fr.paste(band, (0, band_top))
    fr.save(f"{d}/cover-src.jpg", quality=95)
    run(["python3", f"{ED}/make_cover.py", "--photo", f"{d}/cover-src.jpg", "--out", f"{OUT}/clip3-cover.png",
         "--kicker", "พามารีวิว · EP.2", "--title", "Museum\\nSiam", "--pill", "มิวเซียมสยาม ใกล้วัดโพธิ์"])


if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    for name, fn in [("clip1", clip1), ("clip2", clip2), ("clip3", clip3), ("cover", cover)]:
        if "all" in which or name in which:
            fn()
