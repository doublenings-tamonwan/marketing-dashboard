# แฟ้มสถิติ TikTok @doublenings4

```
office/stats/
├── README.md              ← ไฟล์นี้ (อธิบายว่าอะไรอยู่ตรงไหน)
├── tracker.md             ← สมุดสถิติหลัก: ความคืบหน้าเป้า 1,000 · ผู้ติดตาม · ภาพรวมรายวัน · ยอดรายคลิป
├── import_export.py       ← สคริปต์นำไฟล์ export จาก TikTok Studio เข้าแฟ้ม
├── data/                  ← ตัวเลขดิบแบบตาราง (CSV เปิดใน Excel/Google Sheets ได้)
│   ├── daily-overview.csv ← ภาพรวมช่องรายวัน (วิว เข้าโปรไฟล์ ไลก์ คอมเมนต์ แชร์) วันละ 1 แถว
│   └── followers.csv      ← บันทึกผู้ติดตามทุกครั้งที่ได้ภาพหน้าโปรไฟล์
├── weekly/                ← สรุปรายสัปดาห์ (ให้ performance-analyst อ่าน)
│   └── 2026-W46.md
├── raw/                   ← ไฟล์ต้นฉบับ ห้ามแก้
│   └── tiktok-studio/     ← ไฟล์ export (.zip/.xlsx) ตั้งชื่อ <วันนำเข้า>_<ชนิด>_<ช่วงวัน>
└── screenshots/           ← ภาพแคปสถิติ/หน้าโปรไฟล์ ตั้งชื่อ <วันที่>_<เรื่อง>.png
```

## เจ้าของช่องส่งอะไรมาได้บ้าง
| ส่งมา | ทีมเก็บที่ | แล้วอัปเดต |
|---|---|---|
| ไฟล์ export จาก TikTok Studio (.zip/.xlsx) | `raw/tiktok-studio/` + `data/*.csv` | `tracker.md` + `weekly/` |
| ภาพหน้าโปรไฟล์ | `screenshots/` | `data/followers.csv` + `tracker.md` |
| ภาพสถิติรายคลิป | `screenshots/` | ตารางคลิปใน `tracker.md` |

## วิธีนำไฟล์ export เข้า (หัวหน้าทีม)
```bash
python3 office/stats/import_export.py <ไฟล์.zip>
```
- เก็บต้นฉบับไว้ที่ `raw/tiktok-studio/` ให้เอง
- รวมตัวเลขเข้า `data/daily-overview.csv` ถ้าวันไหนซ้ำ ใช้ตัวเลขจากไฟล์ใหม่ เพราะ TikTok อัปเดตยอดย้อนหลังได้
- ชีตชนิดอื่น เช่น Followers หรือ Content จะได้ไฟล์ `data/<ชื่อชีต>.csv` แยก
- จากนั้นส่งสรุปให้ `stats-tracker` อัปเดต `tracker.md` และส่งให้ `performance-analyst` ในรอบสัปดาห์

## กติกา
- ห้ามเดาตัวเลข ถ้าไม่มีข้อมูลให้เขียน "–" หรือ "ยังไม่ยืนยัน"
- ไฟล์ใน `raw/` และ `screenshots/` ห้ามแก้หรือลบ ใช้เป็นหลักฐานย้อนหลัง
