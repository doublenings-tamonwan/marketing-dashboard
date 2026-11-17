"""เสียงประกอบสังเคราะห์เอง (ไม่ติดลิขสิทธิ์) — ทำแทร็กเสียงประกอบทั้งคลิปทีเดียว
python3 sfx.py --duration 59.1 --out sfx.wav --cues "whoosh@0.3,hit@8.5,chime@25,tale@32.8,slip@41.5,fail@48,bell@54.6"
เสียงที่มี: whoosh (วู้บ), hit (ตึ่ง! ตกใจ), chime (ระฆังอบอุ่น), tale (ฟิ้ว~ เปิดนิทาน+คลื่น), slip (ซื้ด~ ลื่น),
          fail (ป๊าบ ป๊าบ ป๊าบ~ เกมแพ้), bell (คลิก+กระดิ่งกดติดตาม),
          pop (ป๊อป อีโมจิเด้ง), boing (ดึ๋ง), sparkle (วิ้ง ๆ), yay (เย้! คนเชียร์ + แตร + พลุกระดาษ)
"""
import argparse, wave
import numpy as np
SR = 48000
rng = np.random.default_rng(3)

def _t(d): return np.arange(int(SR * d)) / SR
def _env(t, a=0.005, dec=4.0): return np.minimum(1, t / a) * np.exp(-dec * t)
def _norm(y, amp): return amp * y / (np.abs(y).max() + 1e-9)

def _bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)

def whoosh():
    t = _t(0.55); n = len(t)
    y = np.zeros(n)
    for k, (lo, hi) in enumerate([(300, 900), (900, 2500), (2500, 6000)]):
        y += _bandnoise(n, lo, hi) * np.exp(-((t - 0.22 - 0.03 * k) / 0.12) ** 2)
    return _norm(y, 0.5)

def hit():
    t = _t(1.2)
    f = 55 + 70 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(t, 0.002, 3.5)
    tone = sum(a * np.sin(2 * np.pi * fr * t) for fr, a in [(220, 1), (277, .7), (330, .6)]) * _env(t, 0.004, 2.5)
    crack = _bandnoise(len(t), 1500, 7000) * _env(t, 0.001, 40)
    return _norm(body * 1.0 + tone * 0.35 + crack * 0.4, 0.6)

def chime():
    t = _t(2.2); y = np.zeros(len(t))
    for i, f0 in enumerate([1047, 1319, 1568]):
        s = int(SR * 0.12 * i); tt = t[:len(t) - s]
        y[s:] += sum(a * np.sin(2 * np.pi * f0 * r * tt) for r, a in [(1, 1), (2, .3), (3, .1)]) * _env(tt, 0.004, 2.2)
    return _norm(y, 0.35)

def tale():
    t = _t(2.0)
    f = 600 + 1400 * (t / 2.0) ** 0.6
    harp = np.zeros(len(t))
    for i, f0 in enumerate([523, 659, 784, 988, 1175, 1319]):
        s = int(SR * 0.07 * i); tt = t[:len(t) - s]
        harp[s:] += np.sin(2 * np.pi * f0 * tt) * _env(tt, 0.003, 3.0)
    wave_ = _bandnoise(len(t), 200, 1200) * (0.5 - 0.5 * np.cos(2 * np.pi * t / 2.0))
    return _norm(harp + 0.6 * wave_ + 0.0 * f, 0.4)

def slip():
    t = _t(0.7)
    f = 400 + 1600 * (t / 0.7) ** 1.5
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.7) ** 0.5
    y += 0.3 * _bandnoise(len(t), 2000, 6000) * np.sin(np.pi * t / 0.7)
    return _norm(y, 0.4)

def fail():
    out = []
    for i, (f0, d) in enumerate([(392, .28), (370, .28), (349, .28), (330, .9)]):
        t = _t(d)
        vib = 1 + (0.02 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0)
        f = f0 * vib * (1 - (0.06 * t / d if i == 3 else 0))
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = (np.sign(np.sin(ph)) * 0.3 + np.sin(ph)) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05)
        out.append(y)
    return _norm(np.concatenate(out), 0.3)

def bell():
    def ding(f0, dur, amp):
        t = _t(dur)
        y = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-dc * t) for r, a, dc in [(1, 1, 3.2), (2, .45, 4.5), (2.76, .3, 5.5), (5.4, .12, 9)])
        return _norm(y * np.minimum(1, t / 0.003), amp)
    out = np.zeros(int(SR * 1.6)); t = _t(0.04)
    out[:len(t)] += 0.35 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 180)
    for f0, st, amp in [(1568, .08, .45), (2093, .22, .38)]:
        a = ding(f0, 1.3, amp); s = int(SR * st); out[s:s + len(a)] += a[:len(out) - s]
    return out

def pop():
    t = _t(0.12)
    f = 900 * np.exp(-t * 18) + 300
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(t, 0.001, 35), 0.35)

def boing():
    t = _t(0.6)
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4) + 80 * np.exp(-t * 6)
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(t, 0.003, 4.5), 0.4)

def sparkle():
    t = _t(0.9); y = np.zeros(len(t))
    for i, f0 in enumerate([1760, 2349, 2637, 3136]):
        s = int(SR * 0.06 * i); tt = t[:len(t) - s]
        y[s:] += np.sin(2 * np.pi * f0 * tt) * _env(tt, 0.002, 6)
    return _norm(y, 0.28)

def yay():
    """เสียงคนเชียร์ "เย้!" (สังเคราะห์ formant หลายเสียง) + แตรปาร์ตี้ + พลุกระดาษ"""
    dur = 1.4; t = _t(dur); y = np.zeros(len(t))
    r = np.random.default_rng(11)
    for v in range(7):
        st = r.uniform(0, 0.08); f0 = r.uniform(210, 340); d = r.uniform(0.75, 1.05)
        tt = t - st; m = (tt > 0) & (tt < d)
        p = f0 * (1 + 0.25 * np.clip(tt / 0.15, 0, 1) - 0.12 * np.clip((tt - 0.4) / 0.6, 0, 1))  # เสียงขึ้นแล้วลง
        ph = 2 * np.pi * np.cumsum(np.where(m, p, 0)) / SR
        F1 = 380 + 300 * np.clip(tt / 0.12, 0, 1); F2 = 2300 - 450 * np.clip(tt / 0.12, 0, 1)  # ย → เ
        src = np.zeros(len(t))
        for h in range(1, 16):
            fh = p * h
            amp = np.exp(-((fh - F1) / 160) ** 2) + 0.6 * np.exp(-((fh - F2) / 220) ** 2) + 0.15 * np.exp(-((fh - 3000) / 300) ** 2)
            src += amp * np.sin(h * ph)
        env = np.where(m, np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.25), 0)
        y += src * env * (1 + 0.05 * np.sin(2 * np.pi * 5.5 * tt))
    y = _norm(y, 1.0)
    horn_t = _t(0.55); hf = 520 + 160 * (horn_t / 0.55)
    horn = np.sign(np.sin(2 * np.pi * np.cumsum(hf) / SR)) * np.minimum(1, horn_t / 0.02) * np.minimum(1, (0.55 - horn_t) / 0.1)
    y[:len(horn)] += 0.18 * horn
    for k in range(10):
        s0 = int(SR * r.uniform(0.05, 0.9)); c = _bandnoise(int(SR * 0.03), 2000, 8000) * np.exp(-_t(0.03) * 120)
        y[s0:s0 + len(c)] += 0.25 * c / (np.abs(c).max() + 1e-9)
    return _norm(y, 0.55)

SOUNDS = dict(pop=pop, boing=boing, sparkle=sparkle, yay=yay, whoosh=whoosh, hit=hit, chime=chime, tale=tale, slip=slip, fail=fail, bell=bell)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--cues", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    track = np.zeros(int(SR * (a.duration + 3)))
    for cue in a.cues.split(","):
        name, at = cue.split("@"); y = SOUNDS[name.strip()](); s = int(float(at) * SR)
        track[s:s + len(y)] += y[:len(track) - s]
    track = np.clip(track[:int(SR * a.duration)], -1, 1)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((track * 32767).astype(np.int16).tobytes())
