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
