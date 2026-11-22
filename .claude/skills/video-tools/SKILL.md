---
name: video-tools
description: เครื่องมือทำวิดีโอของทีม — rembg (ลบพื้นหลัง ไดคัตคน ทำสติกเกอร์หัวคน), ffmpeg (ตัด/แปลง/รวมวิดีโอ, มี libass x264 x265), Remotion และ HyperFrames (ทำการ์ด/ไตเติล/สติกเกอร์เคลื่อนไหวด้วยโค้ด), Whisper (ถอดเสียงพูดเป็นข้อความพร้อมเวลา), yt-dlp (โหลดคลิป TikTok ของช่อง) วิธีติดตั้ง เช็กว่าพร้อมใช้ คำสั่ง และข้อห้าม ใช้เมื่อเจ้าของช่องพิมพ์ /video-tools ขอถอดเสียง ขอโหลดคลิปจากลิงก์ TikTok หรือเมื่อ video-editor ต้องทำกราฟิกเคลื่อนไหว
---

คุณคือ **หัวหน้าทีม** คุยกับเจ้าของช่องเป็นภาษาไทย ภาษาง่าย ๆ ไม่ใช้ศัพท์เทคนิค

## ขั้นแรกทุกครั้ง: เช็กว่าเครื่องมือพร้อม
```bash
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
cd office/motion && [ -d node_modules ] || npm ci --no-audit --no-fund
python3 -c "import faster_whisper, rembg" 2>/dev/null && command -v yt-dlp >/dev/null || pip install --break-system-packages -q yt-dlp faster-whisper "rembg[cpu,cli]"
```
(ปกติ setup script ของ environment "marketing-dashboard" ติดตั้งให้แล้วตอนเปิด session ใหม่)

## เลือกเครื่องมือตามงาน
| เจ้าของช่องขอ | ใช้ | ผลลัพธ์ |
|---|---|---|
| "ถอดเสียงคลิปนี้" / หาท่อนพูดก่อนตัด | Whisper → `office/editor/transcribe.py` | `words.json` (ประโยค + เวลาแต่ละคำ) — **เป็นร่าง** ต้องให้เจ้าของช่องเช็กคำก่อนทำซับ |
| ส่งลิงก์ TikTok ของช่อง ให้เอามาตัดใหม่ | yt-dlp | ไฟล์ mp4 ใน scratchpad → ส่งต่อ `video-editor` |
| ส่งลิงก์คลิปคนอื่นให้ดูเทคนิค | yt-dlp → ดูเฟรม → `/edit-tips` | เพิ่มเทคนิคลงคู่มือ **ห้ามเอาคลิปเขาไปลงช่อง** |
| การ์ด/ไตเติล/สติกเกอร์เด้ง/เทมเพลตใช้ซ้ำ | Remotion (React) หรือ HyperFrames (HTML+GSAP) | mp4/mov (โปร่งใสได้) → ซ้อนในคลิปด้วย ffmpeg |
| ตัด/ย่อ/แปลงไฟล์/รวมคลิป/ดึงเฟรม/วัดเสียง | ffmpeg / ffprobe 6.1.1 (ติดตั้งจาก apt) | ใส่ `-nostdin` เมื่อเรียกในลูป · ห้ามใช้ฟิลเตอร์ `ass`/`subtitles` กับภาษาไทย (วรรณยุกต์หาย) |
| ลบพื้นหลัง / ไดคัตคน / ทำสติกเกอร์หัวคน (สไตล์ D) | rembg → `office/editor/cutout.py` | PNG โปร่งใส · `--box x,y,w,h` เลือกคน/หัว · `--main` เก็บคนกลางกรอบ · `--sticker` ขอบขาว+เงา · `--model birefnet-portrait` (สวยสุด ~30 วิ/ภาพ) หรือ `u2net_human_seg` (~5 วิ) หรือ `isnet-general-use` (สินค้า/ของ) |
| ซับภาษาไทย | **`office/editor/burn_subs.py` เท่านั้น** (กติกาเดิม) | |

## กติกา
- ไฟล์วิดีโอ/เสียงที่โหลดหรือเรนเดอร์ เก็บใน scratchpad ไม่ commit
- ปิดการส่งข้อมูลการใช้งานเสมอ (`DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1`)
- ถ้าเว็บถูกบล็อก (403 จาก proxy) → อ่าน `read_documentation` หัวข้อ environment.network แล้วขอเพิ่มเฉพาะเว็บนั้น ไม่ขอเปิดทั้งหมด
- **ไดคัตเฉพาะเจ้าของช่องหรือคนที่อนุญาตแล้ว** · ห้ามไดคัตดารา/คนดัง/คนแปลกหน้า · ถ้าคนในรูปกอด/ชูมือทับกัน ตัวเพื่อนจะติดมาด้วย → ใช้รูปที่เจ้าของช่องอยู่คนเดียว
- เครื่องมือที่ต้องจ่ายเงิน (เช่น ไลเซนส์ Remotion ถ้าเกิน 3 คน) → ถามเจ้าของช่องก่อน

---

# เครื่องมือทำวิดีโอด้วยโค้ด (ติดตั้ง 22 พ.ย. 2026)

| เครื่องมือ | เวอร์ชัน | เหมาะกับ |
|---|---|---|
| **Remotion** (`remotion`, `@remotion/cli`) | 4.0.545 | คลิปที่เขียนด้วย React — การ์ด/กราฟิกเคลื่อนไหว ซับเด้ง สติกเกอร์ เทมเพลตที่ใช้ซ้ำทุกสัปดาห์ |
| **HyperFrames** (`hyperframes`, HeyGen) | 0.9.81 | คลิปที่เขียนเป็น HTML/CSS + GSAP — ไตเติล ข้อความวิ่ง โมชันกราฟิกเร็ว ๆ |

ทั้งคู่ฟรี · **Remotion ฟรีสำหรับบุคคลและบริษัทไม่เกิน 3 คน** (เจ้าของช่องทำคนเดียว = ใช้ฟรีได้) ถ้าวันหน้าเป็นบริษัทใหญ่กว่านั้นต้องซื้อไลเซนส์ → ต้องถามเจ้าของช่องก่อน (กติกาเรื่องเงิน)

## ติดตั้งใหม่ (เครื่องคลาวด์ถูกลบ node_modules หาย)
```bash
cd office/motion && npm ci
```

## ใช้งานบนเครื่องนี้ (ต้องชี้ไปที่ Chrome ที่มีในเครื่อง — ห้ามให้มันโหลด Chrome เอง)
```bash
CHS=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
export DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_SKIP_SKILLS=1   # ปิดการส่งข้อมูลการใช้งาน

# Remotion
npx remotion render <entry.tsx> <CompositionId> out/x.mp4 --browser-executable=$CHS

# HyperFrames (สร้างโปรเจกต์แนวตั้ง แล้วเรนเดอร์)
npx hyperframes init <ชื่อ> --example blank --resolution portrait --non-interactive --skip-skills
PRODUCER_HEADLESS_SHELL_PATH=$CHS npx hyperframes render <ชื่อ> -o out/x.mp4
```
- ทดสอบแล้ว 22 พ.ย.: เรนเดอร์ได้ทั้งคู่ ภาษาไทยแสดงได้ (ตอนทดสอบใช้ฟอนต์ระบบ — งานจริงให้ใส่ `@font-face` ชี้ไปที่ `office/assets/fonts/` เช่น Kanit/Prompt)
- `hyperframes init` สร้างไฟล์ `CLAUDE.md`/`AGENTS.md` ในโฟลเดอร์โปรเจกต์ → **ลบทิ้ง** หรือสร้างโปรเจกต์ใน scratchpad (ไม่ให้ปนกับคำสั่งของออฟฟิศ)
- HyperFrames โหลด GSAP จาก cdn.jsdelivr.net และฟอนต์จาก Google Fonts ตอนเรนเดอร์
- ไฟล์วิดีโอที่เรนเดอร์ (`out/`) ไม่ต้อง commit

---

# Whisper (ถอดเสียง) และ yt-dlp (โหลดคลิป) — ติดตั้ง 22 พ.ย. 2026

ติดตั้งด้วย pip (ระบบ) · setup script ของ environment "marketing-dashboard" ติดตั้งให้อัตโนมัติทุก session ใหม่ (พร้อม `npm ci` ของโฟลเดอร์นี้)

## Whisper → `faster-whisper` 1.2.1
- ใช้ **faster-whisper** (โมเดล Whisper ตัวเดียวกับของ OpenAI แต่เร็วกว่าบน CPU และไม่ต้องลง PyTorch)
- ใช้ผ่าน `python3 -I office/editor/transcribe.py <คลิป> --out words.json [--model small|medium]` → ได้ช่วงเวลา + เวลาของแต่ละคำ (ใช้หาท่อนพูด/ทำซับ)
- ทดสอบแล้ว: โมเดล small ถอดคลิปไทย 22 วิได้ แต่ **คำไทยผิดบ้าง** (เช่น "ตัดส่วนเกิน" → "จำค้าตาส่วนเกิน") → ใช้เป็นร่าง/หาจังหวะเท่านั้น ซับจริงยังต้องมาจากสคริปต์ หรือให้เจ้าของช่องเช็ก · ถ้าอยากแม่นขึ้นลอง `--model medium` (ช้ากว่า)
- โมเดลโหลดจาก Hugging Face ครั้งแรก → ต้องมี `HF_HUB_DISABLE_XET=1` (ตั้งไว้ใน environment แล้ว และสคริปต์ตั้งให้เอง)

## yt-dlp 2026.10.26
- `yt-dlp -o "%(id)s.%(ext)s" <ลิงก์ TikTok>` (เก็บใน scratchpad ไม่ commit)
- ใช้กับ **คลิปของช่องเราเอง** (เอามาตัดใหม่/ทำเวอร์ชันสั้น) หรือ **คลิปตัวอย่างเพื่อศึกษาเทคนิค** เท่านั้น — **ห้ามเอาคลิปคนอื่นไปโพสต์/ตัดลงช่อง** (ลิขสิทธิ์)
- เครื่องนี้อนุญาตไฟล์วิดีโอ TikTok ผ่าน `v19-webapp-prime.us.tiktok.com` เท่านั้น — ถ้าบางคลิปโหลดไม่ได้เพราะไปเซิร์ฟเวอร์อื่น ต้องขอเพิ่มเว็บนั้นในการตั้งค่าเครือข่าย
