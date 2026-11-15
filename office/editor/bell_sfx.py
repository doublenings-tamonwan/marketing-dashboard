"""เสียงกดติดตาม: คลิก + กระดิ่ง "ติ๊ง-ติ๊ง" (สังเคราะห์เอง ไม่ติดลิขสิทธิ์)
python3 bell_sfx.py out.wav"""
import sys, wave
import numpy as np
SR = 48000

def ding(f0, dur=1.2, amp=0.5):
    t = np.arange(int(SR * dur)) / SR
    y = np.zeros_like(t)
    for ratio, a, dec in [(1.0, 1.0, 3.2), (2.0, 0.45, 4.5), (2.76, 0.3, 5.5), (5.4, 0.12, 9.0)]:
        y += a * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-dec * t)
    y *= np.minimum(1, t / 0.003)
    return amp * y / np.abs(y).max()

def click():
    t = np.arange(int(SR * 0.04)) / SR
    return 0.35 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 180)

def make():
    out = np.zeros(int(SR * 1.6))
    c = click(); out[:len(c)] += c
    a = ding(1568, 1.3, 0.45); s = int(SR * 0.08); out[s:s + len(a)] += a[:len(out) - s]
    b = ding(2093, 1.2, 0.38); s = int(SR * 0.22); out[s:s + len(b)] += b[:len(out) - s]
    return np.clip(out, -1, 1)

if __name__ == "__main__":
    y = make()
    with wave.open(sys.argv[1], "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
