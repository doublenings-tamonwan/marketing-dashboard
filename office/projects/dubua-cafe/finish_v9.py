"""EP.2 ดูบัว v9: สติกเกอร์ (เวลาขยับตามช็อตใหม่) + เสียงพากย์เจ้าของช่อง ปรับโทนตื่นเต้น + เพลง lofi ลดเสียงตอนพูด"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stickers_v8 as st

O = "/tmp/claude-0/-home-user-marketing-dashboard/3fe5eb85-c984-5962-ae79-e39ba747511b/scratchpad/cafe2/out"
VO = "/root/.claude/uploads/3fe5eb85-c984-5962-ae79-e39ba747511b/5632d452-Soi_Muban_Rewat_Niwet_2_14.m4a"
ED = os.path.join(st.REPO, "office", "editor")
OLD = [0, 2, 4, 7, 10, 13, 15.5, 17, 19, 21.5]
NEW = [0, 2.7, 5.8, 9.5, 12.5, 16.6, 19.1, 20.9, 23.3, 25.8]
def remap(t):
    for i in range(len(OLD) - 1):
        if t <= OLD[i + 1]:
            return NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i])
    return NEW[-1]
st.CUTS = [remap(c) for c in st.CUTS]
st.S = [(remap(a), remap(b), *rest) for a, b, *rest in st.S]
st.main(os.path.join(O, "dubua-ep2-preview-v9-nostk.mp4"), os.path.join(O, "dubua-ep2-preview-v9-silent.mp4"))

# วลีในไฟล์เสียง (จับจากช่วงเงียบ) → วางต้นฉากที่ตรงกัน
PHRASES = [(5.55, 8.33), (8.63, 11.84), (12.15, 16.04), (16.20, 19.21), (19.40, 23.72), (23.79, 26.15), (27.26, 31.67)]
SCENE = [0.1, 2.85, 5.95, 9.65, 12.65, 16.75, 19.25]
TEMPO, PITCH = 1.12, 1.0595          # เร็วขึ้น 12% + เสียงสูงขึ้นครึ่งเสียง = ฟังตื่นเต้นขึ้น
total = NEW[-1]
fc, labels = [], []
for i, ((a, b), at) in enumerate(zip(PHRASES, SCENE)):
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=channel_layouts=mono,"
              f"asetrate=48000*{PITCH},aresample=48000,atempo={TEMPO / PITCH:.4f},"
              f"afade=t=in:d=0.03,afade=t=out:st={(b - a) / TEMPO - 0.06:.3f}:d=0.06,adelay={int(at * 1000)}[p{i}]")
    labels.append(f"[p{i}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,highpass=f=90,equalizer=f=250:t=q:w=1:g=-2,"
          "equalizer=f=3500:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
          f"loudnorm=I=-15:TP=-1.5,apad,atrim=0:{total},asplit[vo][key]")
fc.append(f"[1:a]volume=0.55,atrim=0:{total}[mu]")
fc.append("[mu][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck]")
fc.append("[duck][vo]amix=inputs=2:normalize=0,alimiter=limit=0.9[aout]")
subprocess.run(["python3", os.path.join(ED, "make_music2.py"), "--mood", "lofi", "--duration", str(total),
                "--out", os.path.join(O, "lofi-v9.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VO, "-i", os.path.join(O, "lofi-v9.wav"),
                "-i", os.path.join(O, "dubua-ep2-preview-v9-silent.mp4"), "-filter_complex", ";".join(fc),
                "-map", "2:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                os.path.join(O, "dubua-ep2-preview-v9.mp4")], check=True)
print("ok")
