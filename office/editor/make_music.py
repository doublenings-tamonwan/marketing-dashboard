"""สร้างดนตรีประกอบไม่ติดลิขสิทธิ์ (แต่งด้วยโค้ด) สำหรับคลิปสั้น

ตัวอย่าง:
    python3 office/editor/make_music.py --duration 15.5 --out music.wav \
        --pops 2,4,6,9,11,13

- เสียงดีดแบบอูคูเลเล่ (Karplus-Strong) + เบส + เชคเกอร์เบา ๆ คอร์ด C-G-Am-F
- --pops: เวลา (วินาที) ที่ใส่เสียง "ป๊อป" น่ารัก ๆ ตอนซับเปลี่ยน
- --mood: cute (ค่าเริ่มต้น, 112 bpm) | chill (88 bpm, นุ่มกว่า)
"""
import argparse
import wave

import numpy as np

SR = 44100
CHORDS = {  # MIDI notes (ukulele-ish voicings)
    "C": [60, 64, 67, 72],
    "G": [59, 62, 67, 71],
    "Am": [60, 64, 69, 72],
    "F": [60, 65, 69, 72],
}
BASS = {"C": 36, "G": 43, "Am": 45, "F": 41}
PROGRESSION = ["C", "G", "Am", "F"]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(freq, dur, decay=0.996, bright=0.5, rng=None):
    """Karplus-Strong plucked string, vectorised per period."""
    n = int(SR * dur)
    p = max(2, int(SR / freq))
    rng = rng or np.random.default_rng()
    buf = rng.uniform(-1, 1, p)
    # soften the attack a little
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, "same")
    out = np.empty(n)
    out[:p] = buf[: min(p, n)] if n >= p else buf[:n]
    i = p
    prev = buf
    while i < n:
        nxt = decay * 0.5 * (prev + np.roll(prev, -1))
        k = min(p, n - i)
        out[i : i + k] = nxt[:k]
        prev = nxt
        i += p
    return out


def add(track, sig, start, gain=1.0):
    s = int(start * SR)
    if s >= len(track):
        return
    e = min(len(track), s + len(sig))
    track[s:e] += gain * sig[: e - s]


def pop_sfx(rng):
    t = np.arange(int(0.12 * SR)) / SR
    f = 900 + 900 * np.exp(-t * 40)  # quick upward-sounding blip
    env = np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mood", choices=["cute", "chill"], default="cute")
    ap.add_argument("--pops", default="", help="comma-separated seconds")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    bpm = 112 if a.mood == "cute" else 88
    beat = 60 / bpm
    total = a.duration + 1.0
    L = np.zeros(int(total * SR))
    R = np.zeros_like(L)

    # strum pattern per bar (in beats): D . D U . U D U
    pattern = [0, 1, 1.5, 2.5, 3, 3.5] if a.mood == "cute" else [0, 1.5, 2, 3]
    bar = 4 * beat
    t0, bar_i = 0.0, 0
    while t0 < total:
        ch = PROGRESSION[bar_i % len(PROGRESSION)]
        for k, b in enumerate(pattern):
            st = t0 + b * beat
            up = k % 2 == 1
            notes = CHORDS[ch][::-1] if up else CHORDS[ch]
            for j, m in enumerate(notes):
                g = (0.16 if not up else 0.11) * (1 - 0.08 * j)
                sig = pluck(hz(m), 1.2, decay=0.995, rng=rng)
                pan = 0.35 + 0.1 * j
                add(L, sig, st + j * 0.012, g * (1 - pan))
                add(R, sig, st + j * 0.012, g * pan)
        # bass on beats 1 and 3
        for b in (0, 2):
            sig = pluck(hz(BASS[ch]), 1.4, decay=0.998, bright=0.2, rng=rng)
            add(L, sig, t0 + b * beat, 0.32)
            add(R, sig, t0 + b * beat, 0.32)
        # soft shaker on 8ths
        if a.mood == "cute":
            for e in range(8):
                n = rng.normal(0, 1, int(0.05 * SR))
                n = np.diff(n, prepend=0) * np.exp(-np.linspace(0, 8, len(n)))
                g = 0.035 if e % 2 else 0.02
                add(L, n, t0 + e * beat / 2, g * 0.6)
                add(R, n, t0 + e * beat / 2, g)
        t0 += bar
        bar_i += 1

    for p in filter(None, a.pops.split(",")):
        s = pop_sfx(rng)
        add(L, s, float(p), 0.22)
        add(R, s, float(p), 0.22)

    n = int(a.duration * SR)
    L, R = L[:n], R[:n]
    fade = np.ones(n)
    fi, fo = int(0.05 * SR), int(1.2 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    st = np.stack([L * fade, R * fade], axis=1)
    st = st / (np.abs(st).max() + 1e-9) * 0.8
    pcm = (st * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
