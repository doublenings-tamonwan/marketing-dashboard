"""Food-review v2 shots (storefront + menu photos, logo/bottle blur). usage: python3 frbuild.py OUTDIR [--only=name]"""
import sys, os
out = sys.argv[1]
only = [a.split("=")[1] for a in sys.argv if a.startswith("--only=")]
sys.argv = ["build.py", out]
import build as B
from PIL import Image

def store():  # 39d60647, crop x>=330 (no "Secret drink" TV, no open/close sign), slow zoom 5%
    src = B.photo("39d60647")
    return [B.view(src, (330, 0, 1152), 1.0 + 0.05 * i / 30, (917, 1150)) for i in range(30)]

def menu():  # 8f70e529, blur wine-bottle rack + shirt logo, slow zoom 4%
    src = B.blur_ellipses(B.photo("8f70e529"), [(612, 378, 110, 70), (698, 1062, 60, 30)], r=24)
    return [B.view(src, (40, 0, 1152), 1.0 + 0.04 * i / 36, (600, 1100)) for i in range(36)]

def react():  # full frame, stranger faces + shirt logo
    man = [(0, (745, 375)), (7, (748, 373)), (14, (743, 370)), (21, (738, 357)), (28, (733, 342)), (35, (728, 326))]
    bun = [(0, (864, 375)), (7, (827, 375)), (14, (822, 375)), (21, (833, 359)), (28, (828, 343)), (35, (807, 343))]
    su = [(0, (600, 976)), (7, (599, 967)), (14, (602, 949)), (21, (591, 963)), (28, (597, 940)), (35, (595, 931))]
    res = []
    for i, f in enumerate(B.vframes(B.DRIVE, 24.0, 36, 1.0)):
        m, b, s = B.lerp_keys(man, i), B.lerp_keys(bun, i), B.lerp_keys(su, i)
        f = B.blur_ellipses(f, [(m[0], m[1], 64, 92), (b[0], b[1], 80, 95)], r=30)
        res.append(B.blur_ellipses(f, [(s[0], s[1], 78, 34)], r=14))
    return res

def sashimi():
    return B.still_shot("c7db42e2", 42, (164, 0, 1134), (1008, 1300), 1.0, 0.054)

def yum():
    src = B.photo("854b721a")
    return [B.view(src, (150 + 3 * i, 0, 1134), 1.04, (756 + 3 * i, 1058)) for i in range(42)]

def wagyu():
    src = B.photo("ceae1e7c")
    return [B.view(src, (184 + i * 0.6, 280, 976), 1.0, (0, 0)) for i in range(42)]

def storev():  # 7377 0.0-1.0, crop below MONA CLINIC
    return [B.view(f, (0, 600, 742), 1.0, (0, 0)) for f in B.video_frames("a623496b-IMG_7377", 0.0, 30)]

def chef():  # 7383 0.0-1.0, crop below sake lanterns / right of bottle shelf, blur chef faces
    fr = B.video_frames("e2074a94-IMG_7383", 0.0, 30)
    res = []
    for i, f in enumerate(fr):
        t = i / B.FPS
        c1 = B.lerp_keys([(0, (648, 985)), (0.75, (593, 962)), (1.45, (435, 985))], t)
        c2 = B.lerp_keys([(0, (1035, 1022)), (0.75, (983, 1000)), (1.45, (788, 1007))], t)
        f = B.blur_ellipses(f, [(c1[0], c1[1], 62, 74), (c2[0], c2[1], 62, 74)])
        x0 = B.lerp_keys([(0, (390,)), (0.75, (320,)), (1.45, (160,))], t)[0]
        res.append(B.view(f, (x0, 390, 520), 1.0, (0, 0)))
    return res

def top():
    src = B.photo("7fa7d651")
    return [B.view(src, (120 + 5 * i, 0, 1449), 1.0, (0, 0)) for i in range(24)]

def lantern():
    fr = B.video_frames("0718ff68-IMG_7392", 0.0, 30)
    return [B.view(f, (40, 0, 1000), 1.0 + 0.04 * i / 30, (540, 700)) for i, f in enumerate(fr)]

def friend():
    fr = B.video_frames("75cb1a17-IMG_7381", 6.0, 30)
    res = []
    for i, f in enumerate(fr):
        t = i / B.FPS
        c = B.lerp_keys([(0, (288, 540)), (0.5, (242, 712)), (1.0, (194, 745)), (1.6, (162, 712))], t)
        f = B.blur_ellipses(f, [(c[0], c[1] - 10, 105, 125)])
        res.append(B.view(f, (27, 0, 1026), 1.0, (540, 960)))
    return res

S = [("yolk", lambda: B.vframes(B.DRIVE, 4.6, 45, 2.0)), ("store", storev), ("chef", chef), ("lantern", lantern),
     ("mix", lambda: B.vframes(B.DRIVE, 15.3, 36, 1.5)), ("lift", lambda: B.vframes(B.DRIVE, 19.9, 24, 1.0)),
     ("react", react), ("sashimi", sashimi), ("yum", yum), ("wagyu", wagyu), ("friend", friend),
     ("card", lambda: [Image.new("RGB", (B.W, B.H), (0, 0, 0))] * 90)]
os.makedirs(out, exist_ok=True)
paths = []
for k, (name, fn) in enumerate(S):
    p = os.path.abspath(f"{out}/{k:02d}-{name}.mp4"); paths.append(p)
    if only and name not in only:
        continue
    B.encode(p, fn(), "")
    print("ok", p, flush=True)
open(f"{out}/list.txt", "w").writelines(f"file '{p}'\n" for p in paths)
