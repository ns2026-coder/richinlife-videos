"""Voiced highlighter video (Rich in Life motivational, 61-70 s).

Same look as make.py (grainy paper, yellow marker, punch cards, toggles), timed to a voiceover,
with the spoken sign-off appended and the music bed underneath, optionally sped up (spec "speed", default 1.0).

usage: python3 voiced.py spec.json voice.mp3 signoff.mp3 out_dir
spec: {"scenes": [{"type": "paper"|"punch"|"toggles"|"clock"|"picture" (pic: arms|summit|stairs|road, text: "LINE\\nLINE"), "say": "...", <make.py fields>}, ...],
       "disclaimer": ""   (optional; "" hides the bottom line for life/motivation videos),
       "music": 0.16      (optional; music volume under the voice)}
Each scene's "say" is the voice text for it; scene lengths come from pauses in the voice.
The sign-off scene (paper card with the sign-off lines) is added automatically at the end.
Writes out_dir/final.mp4 (post this) and out_dir/thumb.jpg.
"""
import os, sys, re, json, subprocess
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make  # noqa: E402

SIGN_LINES = ["Follow for lessons", "every day.", "Keep learning.", "Stay smarter.", "Act accordingly."]
SPEED = 1.0  # spec "speed" overrides; Dan already talks fast


# ---- pictures: original silhouettes drawn in code (no stock images, no logos) ----
from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np

def _spot():
    W, H = make.W, make.H
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.8)) ** 2 + ((y - H * 0.45) / (H * 0.5)) ** 2)
    base = np.clip(1.02 - 0.8 * d ** 2.3, 0.06, 1)[..., None] * np.array([1, 1, 1])
    return Image.fromarray((base * 255).astype(np.uint8))

def _limb(d, a, b, w, c):
    d.line([a, b], fill=c, width=int(w))
    for p in (a, b):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=c)

def person(d, x, y, h, pose="arms", c=(10, 10, 10), step=0.0):
    """Feet at (x, y), height h. pose: arms (arms raised), stand, walk, climb."""
    hr = h * 0.075; neck = (x, y - h * 0.80); hip = (x, y - h * 0.47)
    d.ellipse([x - hr, y - h * 0.80 - 2.1 * hr, x + hr, y - h * 0.80 - 0.1 * hr], fill=c)
    sw, hw = h * 0.13, h * 0.08
    d.polygon([(x - sw, y - h * 0.77), (x + sw, y - h * 0.77), (x + hw, y - h * 0.47), (x - hw, y - h * 0.47)], fill=c)
    lw = h * 0.075; aw = h * 0.055
    sh_l, sh_r = (x - sw * 0.9, y - h * 0.75), (x + sw * 0.9, y - h * 0.75)
    if pose == "arms":
        _limb(d, sh_l, (x - h * 0.36, y - h * 1.08), aw, c); _limb(d, sh_r, (x + h * 0.36, y - h * 1.08), aw, c)
        _limb(d, (x - hw * .6, hip[1]), (x - h * 0.16, y), lw, c); _limb(d, (x + hw * .6, hip[1]), (x + h * 0.16, y), lw, c)
    elif pose == "stand":
        _limb(d, sh_l, (x - h * 0.2, y - h * 0.45), aw, c); _limb(d, sh_r, (x + h * 0.2, y - h * 0.45), aw, c)
        _limb(d, (x - hw * .6, hip[1]), (x - h * 0.08, y), lw, c); _limb(d, (x + hw * .6, hip[1]), (x + h * 0.08, y), lw, c)
    else:  # walk / climb
        s = math.sin(step * math.pi * 2) * (0.22 if pose == "walk" else 0.12)
        lift = h * 0.12 if pose == "climb" else 0
        _limb(d, sh_l, (x - h * 0.22 - h * s, y - h * 0.5), aw, c); _limb(d, sh_r, (x + h * 0.22 + h * s, y - h * 0.5), aw, c)
        _limb(d, (x, hip[1]), (x + h * s * 1.2, y - (lift if s > 0 else 0)), lw, c)
        _limb(d, (x, hip[1]), (x - h * s * 1.2, y - (lift if s <= 0 else 0)), lw, c)

def scene_picture(pic, text, dur):
    """White spotlight, black silhouette, bold text. pic: arms | summit | stairs | road."""
    W, H = make.W, make.H
    base = _spot()
    f = ImageFont.truetype(make.ANTON, 120)
    lines = text.split("\n") if text else []
    def draw(i, t):
        S = 2
        img = base.resize((W * S, H * S))
        d = ImageDraw.Draw(img)
        K = (10, 10, 10)
        e = make.ease(t / 0.5)
        if pic == "arms":
            person(d, W * S / 2, H * S * 0.86, H * S * 0.30 * (0.94 + 0.06 * e), "arms", K)
        elif pic == "summit":
            d.polygon([(-50, H * S), (W * S * 0.55, H * S * 0.62), (W * S + 50, H * S)], fill=K)
            d.polygon([(W * S * 0.2, H * S), (W * S * 0.8, H * S * 0.74), (W * S + 50, H * S)], fill=(40, 40, 40))
            person(d, W * S * 0.55, H * S * 0.622, H * S * 0.09, "arms", K)
        elif pic == "stairs":
            n = 7; sw_, shh = W * S / n, H * S * 0.05
            for k in range(n):
                d.rectangle([k * sw_, H * S - (k + 1) * shh - H * S * 0.08, W * S, H * S], fill=K)
            pos = min(n - 1.0, 1 + t / max(dur, 0.1) * (n - 3))
            k = int(pos)
            person(d, (k + 0.5) * sw_, H * S - (k + 1) * shh - H * S * 0.08, H * S * 0.14, "climb", K, step=t * 1.2)
        elif pic == "road":
            hz = H * S * 0.6
            d.polygon([(W * S * 0.47, hz), (W * S * 0.53, hz), (W * S * 0.95, H * S), (W * S * 0.05, H * S)], fill=K)
            d.rectangle([0, hz, W * S, hz + 6], fill=K)
            person(d, W * S / 2, H * S * 0.80 - t * 40, H * S * 0.12, "walk", (235, 235, 230), step=t * 1.4)
        img = img.resize((W, H), Image.LANCZOS)
        if lines:
            dr = ImageDraw.Draw(img)
            p = make.ease((t - 0.15) / 0.3)
            for li, ln in enumerate(lines if p > 0.02 else []):
                tw = dr.textlength(ln, font=f)
                dr.text(((W - tw) / 2, 260 + li * 140 - (1 - p) * 30), ln, font=f, fill=(12, 12, 12))
        return img
    return draw, dur


def probe(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())


def audio(spec, voice, signoff, out):
    tr = os.path.join(out, "voice_trim.wav")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-af",
                           "areverse,silenceremove=start_periods=1:start_threshold=-40dB,areverse,apad=pad_dur=0.25", tr])
    full = os.path.join(out, "voice_full.wav")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", tr, "-i", signoff, "-filter_complex",
                           "[0:a]aresample=44100,aformat=channel_layouts=mono[a];[1:a]aresample=44100,aformat=channel_layouts=mono[b];"
                           "[a][b]concat=n=2:v=0:a=1[o]", "-map", "[o]", full])
    L, total = probe(tr), probe(full)
    log = subprocess.run(["ffmpeg", "-i", tr, "-af", "silencedetect=noise=-35dB:d=0.18", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    mids = [(a + b) / 2 for a, b in zip(st, en)]
    says = [s["say"] for s in spec["scenes"]]
    tot = sum(map(len, says)); cum = 0; cuts = [0.0]
    for s in says[:-1]:
        cum += len(s); g = cum / tot * L
        m = min(mids, key=lambda x: abs(x - g)) if mids else g
        cuts.append(round(max(m if abs(m - g) < 2.0 else g, cuts[-1] + 1.0), 2))
    cuts += [round(L, 2), round(total, 2)]
    return full, cuts


def build(spec, cuts):
    scenes = []
    for i, s in enumerate(spec["scenes"]):
        dur = cuts[i + 1] - cuts[i]
        k = s["type"]
        if k == "paper":
            nw = sum(len(l.split()) for l in s["lines"])
            pw = s.get("per_word", min(0.32, max(0.12, dur * 0.6 / max(nw, 1))))
            scenes.append(make.scene_paper(s["lines"], dur, per_word=pw, size=s.get("size", 78)))
        elif k == "punch":
            scenes.append(make.scene_punch(s["text"], dur))
        elif k == "toggles":
            scenes.append(make.scene_toggles(dur, s.get("off", "Motivation"), s.get("on", "Discipline")))
        elif k == "clock":
            scenes.append(make.scene_clock(dur, s.get("text", "If not now, when?")))
        elif k == "picture":
            scenes.append(scene_picture(s.get("pic", "arms"), s.get("text", ""), dur))
        else:
            raise ValueError(k)
    sd = cuts[-1] - cuts[-2] + 0.3
    scenes.append(make.scene_paper(SIGN_LINES, sd, per_word=min(0.5, sd * 0.75 / 11), size=72))
    return scenes


def render_one(i):
    make.render(i)


if __name__ == "__main__":
    spec_path, voice, signoff, out = sys.argv[1:5]
    spec = json.load(open(spec_path))
    os.makedirs(out, exist_ok=True)
    make.OUT = out
    make.DISCLAIMER = spec.get("disclaimer", "")
    SPEED = spec.get("speed", SPEED)
    full, cuts = audio(spec, voice, signoff, out)
    make.SCENES[:] = build(spec, cuts)
    with Pool(min(6, os.cpu_count() or 2)) as p:
        p.map(render_one, range(len(make.SCENES)))
    with open(os.path.join(out, "list.txt"), "w") as fh:
        fh.writelines(f"file 's{i}.mp4'\n" for i in range(len(make.SCENES)))
    silent = os.path.join(out, "silent.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(out, "list.txt"), "-c", "copy", silent], check=True)
    music = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highlighter_bed.mp3")
    vol = spec.get("music", 0.16)
    # keep the file under ~9.5 MB so it can go through the GitHub web upload (10 MB limit per upload call)
    vb = int(9.3 * 8192 / (cuts[-1] / SPEED + 0.5) - 170)
    final = os.path.join(out, "final.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", full, "-stream_loop", "-1", "-i", music, "-filter_complex",
                    f"[2:a]volume={vol}[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a];"
                    f"[0:v]setpts=PTS/{SPEED}[v];[a]atempo={SPEED}[a2]",
                    "-map", "[v]", "-map", "[a2]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-b:v", f"{vb}k", "-maxrate", f"{int(vb*1.4)}k", "-bufsize", f"{vb*2}k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", final], check=True)
    th = os.path.join(out, "thumb.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(spec.get("thumb_at", 1.2)), "-i", final, "-frames:v", "1", "-q:v", "3", th], check=True)
    print(final, round(probe(final), 1), "cuts", cuts)
