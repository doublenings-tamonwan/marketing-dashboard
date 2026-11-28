"""Izakaya v5: retime 15.9s cut to owner's 28s voiceover + zooms, big head, warm faces."""
import sys, subprocess, numpy as np
sys.path.insert(0, sys.path[0]); from fx import warm_face, big_head
from PIL import Image
S = sys.argv[1]; OUT = sys.argv[2]; FPS = 30; W, H = 1080, 1920
N = 477
# (out_start, out_end, src_start, src_end)
SEG = [(0.0, 2.6, 0.0, 1.5), (2.6, 6.8, 1.5, 2.5), (6.8, 10.4, 2.5, 3.5), (10.4, 12.3, 3.5, 4.5),
       (12.3, 17.4, 4.5, 6.5), (17.4, 20.5, 6.5, 7.7), (20.5, 22.4, 7.7, 9.1), (22.4, 24.4, 9.1, 11.9),
       (24.4, 25.6, 11.9, 12.9), (25.6, 28.6, 12.9, 15.9)]
DUR = 28.6
def src_t(t):
    for a, b, s0, s1 in SEG:
        if t < b: return s0 + (t - a) / (b - a) * (s1 - s0), (a, b)
    return 15.89, SEG[-1][:2]
cache = {}
def frame(i):
    i = int(min(max(i, 0), N - 1))
    if i not in cache:
        if len(cache) > 40: cache.pop(next(iter(cache)))
        cache[i] = np.asarray(Image.open(f"{S}/src/{i+1:04d}.jpg").convert("RGB")).astype(np.float32)
    return cache[i]
def get(ts):
    x = ts * FPS - 0.5; i = np.floor(x); f = x - i
    return Image.fromarray((frame(i) * (1 - f) + frame(i + 1) * f).astype(np.uint8))
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def punch(t, at, amt, up=0.15, down=0.6):  # quick zoom in then ease back
    if t < at: return 0
    if t < at + up: return amt * ease((t - at) / up)
    return amt * (1 - ease((t - at - up) / down))
def zoom(img, z, c):
    if z <= 1.001: return img
    cw, ch = W / z, H / z; x = min(max(c[0] - cw / 2, 0), W - cw); y = min(max(c[1] - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x, y, x + cw, y + ch))
HEAD = [(6.5, (396, 396)), (6.7, (450, 396)), (6.9, (370, 380)), (7.1, (428, 396)), (7.3, (424, 390)), (7.5, (439, 390)), (7.7, (439, 380))]
def head_c(s):
    for (a, p), (b, q) in zip(HEAD, HEAD[1:]):
        if s <= b: u = (s - a) / (b - a); return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    return HEAD[-1][1]
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
for k in range(int(DUR * FPS)):
    t = k / FPS; s, (a, b) = src_t(t); u = (t - a) / (b - a); img = get(s); z = 1.0; c = (W / 2, H / 2)
    if a == 0.0:   z = 1 + punch(t, 0.8, 0.14, down=1.2) + 0.04 * ease(t / 2.6); c = (540, 950)       # yolk punch
    elif a == 2.6: z = 1.12 - 0.12 * ease(u / 0.06) + 0.10 * ease(u); c = (540, 900)                  # bounce in, slow push
    elif a == 6.8: z = 1.15 - 0.15 * ease(u)                                                          # zoom out
    elif a == 10.4: z = 1.0 + 0.12 * ease(u); c = (540, 1000)                                         # push in
    elif a == 12.3: z = 1.0 + 0.08 * ease(u) + punch(t, 14.95, 0.10); c = (540, 820)                 # yukke push + punch on "ไข่แดง"
    elif a == 17.4:                                                                                   # reaction
        img = warm_face(img, (430, 420), 300, 400)
        g = 0.6 * ease((t - 19.2) / 0.2) if t < 20.05 else 0.6 * (1 - ease((t - 20.05) / 0.2))
        if g > 0.01:
            hc = head_c(s); sh = 10 * np.sin((t - 19.2) * 40) * (1 if 19.2 < t < 19.9 else 0)
            img = big_head(img, (hc[0] + sh, hc[1] - 40), 450, 1 + g)
        z = 1.0 + 0.06 * ease(u); c = (430, 700)
    elif a == 20.5: z = 1.18 - 0.18 * ease(u / 0.8)                                                   # sashimi zoom out
    elif a == 22.4:
        if s < 10.5: z = 1.0 + punch(t, 22.4, 0.12, down=0.8)                                         # salad punch
        else: z = 1.16 - 0.16 * ease((s - 10.5) / 1.4)                                                # wagyu zoom out
    elif a == 24.4: img = warm_face(img, (560, 760), 280, 360); z = 1.0 + 0.08 * ease(u); c = (560, 800)
    elif a == 25.6: z = 1.05 - 0.05 * ease(u / 0.5)
    ff.stdin.write(np.asarray(zoom(img, z, c)).tobytes())
ff.stdin.close(); ff.wait()
