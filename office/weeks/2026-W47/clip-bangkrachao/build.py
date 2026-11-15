#!/usr/bin/env python3
"""Build พามารีวิว EP.2 · บางกะเจ้า preview (ไม่มีเสียงพากย์ · ข้อความบนจอ + เพลง make_music cute)
ใช้: python3 office/weeks/2026-W47/clip-bangkrachao/build.py
"""
import json, os, subprocess

REPO = "/home/user/marketing-dashboard"
SRC = "/root/.claude/uploads/d151a6a9-7df2-5f3b-8b43-ea4e410e4670"
W = "/tmp/claude-0/-home-user-marketing-dashboard/d151a6a9-7df2-5f3b-8b43-ea4e410e4670/scratchpad/bangkrachao"
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(W, exist_ok=True)

VF = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1"

# (ไฟล์, เริ่ม, ความยาวในต้นฉบับ, ความยาวในคลิป, ฟิลเตอร์ก่อน VF)
SHOTS = [
    ("6d9bfc01-IMG_4334", 4.0, 2.0, 2.0, ""),     # 1 เซลฟี่ยิ้มบนจักรยาน (ไม่มีเพื่อนในเฟรม)
    ("270fd557-IMG_4333", 1.0, 2.0, 2.0, ""),     # 2 ถนนต้นไม้
    ("293088b3-IMG_4370", 10.0, 2.0, 2.0, ""),    # 3 บึง + ศาลาริมน้ำ
    ("c0ea6a86-IMG_4338", 2.2, 2.0, 2.0, ""),     # 4 ป้ายราคา
    ("8d571341-IMG_4345", 9.0, 2.5, 2.5, ""),     # 5 หัวคายัค คลองต้นจาก
    # 6 เซลฟี่ในคายัค: ช่วงเดียวที่ไม่เห็นเพื่อนคือ 2.62-3.52 วิ -> ยืด ~2.2 เท่า (slow-mo) + ครอปเข้าหน้า 15% ฝั่งขวา
    ("d494221f-IMG_4358", 2.62, 0.9, 2.0,
     "setpts=2.23*PTS,crop=iw*0.85:ih*0.85:iw*0.15:ih*0.15,"),
    ("bf8552fd-IMG_4332", 0.5, 2.0, 2.0, ""),     # 7 ห่านเดินแถว
    ("de32490a-IMG_4359", 0.0, 5.0, 5.0, ""),     # 8 คลองต้นจาก + การ์ดข้อมูล (ยืดเป็น 5 วิ)
    ("6d9bfc01-IMG_4334", 10.0, 2.0, 2.0, ""),    # 9 เซลฟี่แลบลิ้น ปิดท้าย CTA
]


def run(cmd):
    print(" ".join(cmd)[:200])
    subprocess.run(cmd, check=True)


def main():
    parts, t = [], 0.0
    cuts = []
    for i, (f, ss, sd, od, pre) in enumerate(SHOTS, 1):
        out = f"{W}/shot{i:02d}.mp4"
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(ss), "-t", str(sd + 0.05),
             "-i", f"{SRC}/{f}.MOV", "-vf", pre + VF, "-t", str(od), "-an",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", out])
        parts.append(out)
        cuts.append(round(t, 2))
        t += od
    total = round(t, 2)
    with open(f"{W}/list.txt", "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", f"{W}/list.txt", "-c", "copy", f"{W}/base.mp4"])

    # subs: เลื่อนตามเวลาช็อตใหม่ (การ์ดข้อมูล 5 วิ)
    subs = json.load(open(f"{HERE}/subs.json"))
    for s, st, (_, _, _, od, _) in zip(subs, cuts, SHOTS):
        s["start"], s["end"] = st, round(st + od, 2)
    subs[-1]["end"] = total
    # ซับท่อน 6: หน้าเต็มจอ -> ยกซับขึ้นไปแถบฟ้าเหนือหมวก ไม่ให้ทับหน้า
    subs[5]["y"] = 250
    # การ์ดข้อมูล: ข้อความเดิมครบทุกตัว แค่ตัดบรรทัดยาวเป็น 7 บรรทัด ให้ตัวไม่ถูกย่อจนอ่านไม่ทัน (เดิมย่อเหลือ ~50px)
    subs[7]["text"] = ("บางกะเจ้า\nพระประแดง สมุทรปราการ\nคายัค 100 บาท/คน\nเรือไม้ 500 บาท/5 คน\n"
                       "วาดภาพ 150 บาท/เฟรม\nราคาตามป้าย ณ พ.ค. 2026\n[เซฟไว้] ไปวันหยุด")
    subs[7]["size"] = 68
    json.dump(subs, open(f"{W}/subs-timed.json", "w"), ensure_ascii=False, indent=1)

    pops = ",".join(str(c) for c in cuts[1:])
    run(["bash", f"{REPO}/office/editor/glow.sh", f"{W}/base.mp4", f"{W}/base-glow.mp4"])
    run(["python3", f"{REPO}/office/editor/sparkles.py", "--video", f"{W}/base-glow.mp4",
         "--out", f"{W}/base-fx.mp4", "--bursts", ",".join(str(c) for c in cuts)])
    run(["python3", f"{REPO}/office/editor/make_music.py", "--mood", "cute", "--duration", str(total),
         "--out", f"{W}/music.wav", "--pops", pops])
    run(["python3", f"{REPO}/office/editor/burn_subs.py", "--video", f"{W}/base-fx.mp4",
         "--subs", f"{W}/subs-timed.json", "--out", f"{W}/bangkrachao-ep2-preview.mp4",
         "--audio", f"{W}/music.wav"])
    print("total", total, "cuts", cuts)


if __name__ == "__main__":
    main()
