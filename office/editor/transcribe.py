"""ถอดเสียงพูดในคลิปด้วย Whisper (faster-whisper) → JSON ช่วงเวลา + คำ ใช้ทำซับ/หาท่อนพูด
ใช้: python3 -I office/editor/transcribe.py <วิดีโอหรือเสียง> --out words.json [--model small|medium|large-v3] [--lang th]
- ถอดเสียงจากไฟล์ด้วย ffmpeg เอง (เลี่ยงปัญหาเวอร์ชัน av ของ faster-whisper)
- โมเดลโหลดจาก Hugging Face ครั้งแรก (ต้องตั้ง HF_HUB_DISABLE_XET=1 บนเครื่องนี้) แล้วเก็บไว้ใน ~/.cache/huggingface
- ผลถอดเสียงเป็นร่าง: คำไทยผิดได้ ต้องให้เจ้าของช่องเช็กก่อนใช้เป็นซับ
"""
import argparse, json, os, subprocess, sys
import numpy as np
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('--out', required=True)
ap.add_argument('--model', default='small'); ap.add_argument('--lang', default='th')
a = ap.parse_args()
raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', a.src, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
m = WhisperModel(a.model, device='cpu', compute_type='int8')
segs, info = m.transcribe(audio, language=a.lang, vad_filter=True, word_timestamps=True)
out = []
for s in segs:
    out.append({'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip(),
                'words': [{'start': round(w.start, 2), 'end': round(w.end, 2), 'word': w.word} for w in (s.words or [])]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text.strip()}")
json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved', a.out, 'segments', len(out), file=sys.stderr)
