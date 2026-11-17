"""EP.2 ดูบัว v14: แทรกเสียง "นอกจากนี้ยังมีโซนมินิซูด้วย" (ไฟล์ _17) ต้นฉากน้องแพะ · ฐาน v13: ซีน 1 ใช้เสียงอัดใหม่ (Soi_..._16.m4a) ต่อด้วยเสียงเดิมตั้งแต่ประโยค 2 · เสียงพากย์ต่อเนื่องทั้งไฟล์ (ไม่ตัดเป็นท่อน กันเสียงสะดุด/ซ้อน)
- ตัดแค่ช่วงเงียบหัวไฟล์ + ย่อช่วงหยุดยาว 26.15–27.2 เหลือ 0.3 วิ
- เร็วขึ้น 8% (atempo ไม่เปลี่ยนระดับเสียง) + EQ ให้เสียงสดใส + คอมเพรส
- เพลง lofi เบา ๆ ลดเสียงตอนพูด · ภาพ/สติกเกอร์ขยับตามฉากใหม่ (build_v8)
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stickers_v8 as st

O = "/tmp/claude-0/-home-user-marketing-dashboard/3fe5eb85-c984-5962-ae79-e39ba747511b/scratchpad/cafe2/out"
VO = "/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/5632d452-Soi_Muban_Rewat_Niwet_2_14.m4a"
VO1 = "/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/2172fb55-Soi_Muban_Rewat_Niwet_2_16.m4a"
VO2 = "/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/5e87c0b8-Soi_Muban_Rewat_Niwet_2_17.m4a"
ED = os.path.join(st.REPO, "office", "editor")
OLD = [0, 2, 4, 7, 10, 13, 15.5, 17, 19, 21.5]
NEW = [0, 4.0, 7.25, 11.0, 13.95, 18.05, 22.82, 24.42, 26.42, 28.92]
def remap(t):
    for i in range(len(OLD) - 1):
        if t <= OLD[i + 1]:
            return NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i])
    return NEW[-1]
st.CUTS = [remap(c) for c in st.CUTS]
st.S = [(remap(a), remap(b), *rest) for a, b, *rest in st.S]
silent = os.path.join(O, "dubua-ep2-preview-v14-silent.mp4")
st.main(os.path.join(O, "dubua-ep2-preview-v14-nostk.mp4"), silent)

total = NEW[-1]
fc = [
    "[0:a]pan=mono|c0=0.5*c0+0.5*c1,asplit=3[a1][a2][a3]",
    "[4:a]pan=mono|c0=0.5*c0+0.5*c1,atrim=0.8:3.4,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=2.5:d=0.1[sg]",
    "[3:a]pan=mono|c0=0.5*c0+0.5*c1,atrim=0.85:5.15,asetpts=PTS-STARTPTS,afade=t=out:st=4.2:d=0.1[s0]",
    "[a1]atrim=8.50:23.9,asetpts=PTS-STARTPTS,afade=t=in:d=0.05[s1]",
    "[a3]atrim=24.05:26.15,asetpts=PTS-STARTPTS[s1b]",
    "[a2]atrim=26.9:31.8,asetpts=PTS-STARTPTS[s2]",
    "[s0][s1][sg][s1b][s2]concat=n=5:v=0:a=1,atempo=1.08,highpass=f=90,equalizer=f=250:t=q:w=1:g=-2,"
    "equalizer=f=3500:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
    f"loudnorm=I=-15:TP=-1.5,aresample=48000,apad,atrim=0:{total},pan=stereo|c0=c0|c1=c0,asplit[vo][key]",
    f"[1:a]aresample=48000,volume=0.28,atrim=0:{total}[mu]",
    "[mu][key]sidechaincompress=threshold=0.01:ratio=10:attack=15:release=350[duck]",
    "[duck][vo]amix=inputs=2:normalize=0,alimiter=limit=0.9[aout]",
]
subprocess.run(["python3", os.path.join(ED, "make_music2.py"), "--mood", "lofi", "--duration", str(total),
                "--out", os.path.join(O, "lofi-v14.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VO, "-i", os.path.join(O, "lofi-v14.wav"), "-i", silent, "-i", VO1, "-i", VO2,
                "-filter_complex", ";".join(fc), "-map", "2:v", "-map", "[aout]", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", os.path.join(O, "dubua-ep2-preview-v14.mp4")], check=True)
print("ok")
