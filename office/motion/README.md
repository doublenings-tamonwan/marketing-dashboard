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
