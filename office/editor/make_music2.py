"""ดนตรีประกอบแบบนุ่ม ลากยาว (ไม่ใช่เสียงดีดตึ่ง ๆ) แต่งด้วยโค้ด ไม่ติดลิขสิทธิ์

    python3 office/editor/make_music2.py --mood lofi --duration 21.5 --out music.wav

--mood
  lofi  : อิเล็กทริกเปียโนนุ่ม ๆ + เบสอุ่น + กลองเบา ๆ แบบโลไฟ + เสียงแผ่นเสียงจาง ๆ (80 bpm)
  piano : เปียโนไล่โน้ตช้า ๆ ลอย ๆ + แพดนุ่ม ไม่มีกลอง (70 bpm)
  jazz  : คาเฟ่แจ๊ส อิเล็กทริกเปียโน + ดับเบิลเบสเดิน + แปรงกลองสวิง (96 bpm)
"""
import argparse
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(3)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a, d_tau, rel=0.08):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-t / d_tau)
    r = int(rel * SR)
    if r and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def smooth(x, k):
    if k <= 1:
        return x
    return np.convolve(x, np.ones(k) / k, mode="same")


def epiano(m, dur, vel=0.5):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    body = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.4))
    bell = 0.15 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t / 0.25)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    return vel * (body + bell) * env(n, 0.012, 1.6, 0.25) * trem


def piano(m, dur, vel=0.5):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    x = sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (0.7 + 0.9 * h))
            for h, a in ((1, 1), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)))
    return vel * x * env(n, 0.006, 3.0, 0.3)


def pad(ms, dur, vel=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * mtof(m) * t * d) for m in ms for d in (0.997, 1.003))
    a = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    return vel * x / (2 * len(ms)) * np.clip(a, 0, 1)


def bass(m, dur, vel=0.4):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return vel * x * env(n, 0.02, 0.9, 0.06)


def kick(vel=0.5):
    n = int(0.3 * SR); t = np.arange(n) / SR
    f = 50 + 70 * np.exp(-t / 0.04)
    return vel * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)


def brush(dur=0.18, vel=0.08, k=3):
    n = int(dur * SR)
    return vel * smooth(rng.standard_normal(n), k) * env(n, 0.004, dur / 3, 0.02)


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


def build(mood, total):
    L = np.zeros((int((total + 4) * SR),)); R = L.copy()
    def add(x, t, pan=0.0):
        place(L, x * (1 - max(pan, 0)), t); place(R, x * (1 + min(pan, 0)), t)

    if mood == "lofi":
        bpm = 80; beat = 60 / bpm
        prog = [(65, [65, 69, 72, 76]), (64, [64, 67, 71, 74]), (62, [62, 65, 69, 72]), (60, [60, 64, 67, 71])]
        bar = 0; t = 0.0
        while t < total:
            root, ch = prog[bar % 4]
            for k, m in enumerate(ch):
                add(epiano(m, beat * 4, 0.16), t + k * 0.03 + 0.0, pan=(k - 1.5) * 0.15)
            add(epiano(ch[1] + 12, beat * 1.5, 0.08), t + beat * 2.5, 0.2)
            add(bass(root - 24, beat * 1.8), t); add(bass(root - 24, beat * 1.2, 0.3), t + beat * 2.5)
            for b in range(4):
                if b in (0, 2): add(kick(0.35), t + b * beat + (0.04 if b == 2 else 0))
                if b in (1, 3): add(brush(0.25, 0.12, 6), t + b * beat)
                add(brush(0.06, 0.03, 2), t + b * beat + beat / 2, 0.3)
            bar += 1; t += beat * 4
        crackle = np.zeros_like(L); idx = rng.integers(0, len(L), int(total * 25))
        crackle[idx] = rng.uniform(-0.05, 0.05, len(idx))
        hiss = 0.004 * smooth(rng.standard_normal(len(L)), 8)
        L += crackle + hiss; R += crackle + hiss
    elif mood == "piano":
        bpm = 70; beat = 60 / bpm
        prog = [[60, 67, 72, 76], [57, 64, 69, 72], [53, 60, 65, 69], [55, 62, 67, 71]]
        bar = 0; t = 0.0
        while t < total:
            ch = prog[bar % 4]
            add(pad([n + 12 for n in ch[1:]], beat * 4 + 0.6), t)
            add(piano(ch[0] - 12, beat * 4, 0.22), t)
            for k, m in enumerate(ch[1:] + [ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12][:5]):
                add(piano(m, beat * 3, 0.13), t + k * beat * 0.5, pan=0.25 * np.sin(k))
            bar += 1; t += beat * 4
    else:  # jazz
        bpm = 96; beat = 60 / bpm; sw = beat * 2 / 3
        prog = [(62, [65, 69, 72, 76]), (55, [65, 69, 71, 74]), (60, [64, 67, 71, 74]), (57, [64, 67, 69, 73])]
        walk = [[0, 3, 5, 7], [0, 4, 5, 6], [0, 2, 4, 7], [0, 3, 4, 1]]
        bar = 0; t = 0.0
        while t < total:
            root, ch = prog[bar % 4]
            for k, m in enumerate(ch):
                add(epiano(m - 12, beat * 1.6, 0.12), t + beat * 1 + sw + k * 0.02, pan=-0.2)
                add(epiano(m - 12, beat * 2.4, 0.10), t + beat * 3 + k * 0.02, pan=-0.2)
            for b, st in enumerate(walk[bar % 4]):
                add(bass(root - 24 + st, beat * 0.95, 0.42), t + b * beat, 0.15)
            for b in range(4):
                add(brush(0.3, 0.06, 4), t + b * beat, 0.35)
                add(brush(0.1, 0.035, 2), t + b * beat + sw, 0.35)
            bar += 1; t += beat * 4

    n = int(total * SR)
    x = np.stack([L[:n], R[:n]], 1)
    x = smooth(x[:, 0], 3)[:, None] * [1, 0] + smooth(x[:, 1], 3)[:, None] * [0, 1]
    fi, fo = int(0.4 * SR), int(1.5 * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]; x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    x = np.tanh(x * 1.2)
    return x / (np.abs(x).max() + 1e-9) * 0.82


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mood", choices=["lofi", "piano", "jazz"], default="lofi")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    x = (build(a.mood, a.duration) * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())


if __name__ == "__main__":
    main()
