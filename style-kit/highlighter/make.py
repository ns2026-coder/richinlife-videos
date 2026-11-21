import os, sys, math, subprocess, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = "."
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
SERIF = os.path.join(FONTS, "FreeSerif.ttf")
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
SANS = os.path.join(FONTS, "DejaVuSans.ttf")
INK = (28, 26, 22)
HL = (214, 214, 52)
rng = np.random.default_rng(7)

def vignette(strength, base=0.0):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.5)) ** 2)
    return np.clip(1 - strength * d ** 2.2, base, 1)[..., None]

def paper(seed):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (H // 3, W // 3))
    img = Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    img = np.asarray(img.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    fine = r.normal(0, 0.035, (H, W))
    lum = 0.66 + (img - 0.5) * 0.10 + fine
    rgb = np.stack([lum * 1.0, lum * 0.975, lum * 0.93], -1)
    return np.clip(rgb * vignette(0.85, 0.12), 0, 1)

PAPERS = [paper(s) for s in range(3)]
GRAINS = [rng.normal(0, 0.015, (H, W, 1)).astype(np.float32) for _ in range(4)]

def bg_paper(i):
    return Image.fromarray((np.clip(PAPERS[(i // 6) % 3], 0, 1) * 255).astype(np.uint8))

def add_grain(img, i):
    a = np.asarray(img, np.float32) / 255 + GRAINS[(i // 6) % 4]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def highlight_text(img, lines, t, size=78, start=0.15, per_word=0.32, cy=None):
    """Words appear one by one; a yellow marker wipes behind each line."""
    d = ImageDraw.Draw(img, "RGBA")
    f = ImageFont.truetype(SERIF, size)
    lh = int(size * 1.32)
    cy = H // 2 if cy is None else cy
    y0 = cy - lh * len(lines) // 2
    k = 0
    for li, line in enumerate(lines):
        words = line.split(" ")
        full_w = d.textlength(line, font=f)
        x0 = (W - full_w) / 2
        y = y0 + li * lh
        # marker: full-line width, grows with the words shown
        shown_w = 0
        x = x0
        for wi, w in enumerate(words):
            wt = start + (k + wi) * per_word
            p = ease((t - wt) / 0.18)
            ww = d.textlength(w + (" " if wi < len(words) - 1 else ""), font=f)
            if p > 0:
                shown_w = (x - x0) + ww * p
            x += ww
        if shown_w > 0:
            pad = size * 0.14
            d.rectangle([x0 - pad, y + size * 0.12, x0 + shown_w + pad * 0.4, y + size * 1.14], fill=HL + (205,))
        x = x0
        for wi, w in enumerate(words):
            wt = start + (k + wi) * per_word
            p = ease((t - wt) / 0.12)
            if p > 0:
                d.text((x, y + (1 - p) * 8), w, font=f, fill=INK + (int(255 * p),))
            x += d.textlength(w + " ", font=f)
        k += len(words)
    return img

def scene_paper(lines, dur, **kw):
    def draw(i, t):
        img = bg_paper(i)
        return highlight_text(img, lines, t, **kw)
    return draw, dur

def scene_punch(text, dur):
    """Bright white spotlight with a bold statement that punches in."""
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.42)) ** 2)
    base = np.clip(1.02 - 0.75 * d ** 2.4, 0.08, 1)[..., None] * np.array([1, 1, 1])
    base_img = Image.fromarray((base * 255).astype(np.uint8))
    f = ImageFont.truetype(ANTON, 150)
    def draw(i, t):
        img = base_img.copy()
        dr = ImageDraw.Draw(img)
        s = 1.18 - 0.18 * ease(t / 0.25)
        lines = text.split("\n")
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        lh = 170
        for li, ln in enumerate(lines):
            tw = ld.textlength(ln, font=f)
            ld.text(((W - tw) / 2, H / 2 - lh * len(lines) / 2 + li * lh - 20), ln, font=f, fill=(12, 12, 12, 255))
        if abs(s - 1) > 1e-3:
            nw, nh = int(W * s), int(H * s)
            layer = layer.resize((nw, nh), Image.BICUBIC).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
        img.paste(layer, (0, 0), layer)
        return img
    return draw, dur

def toggle(d, x, y, on_p, label, f):
    d.text((x - 380, y - 34), label, font=f, fill=(190, 190, 190))
    w, h = 150, 78
    col = tuple(int(a + (b - a) * on_p) for a, b in zip((90, 90, 94), (52, 199, 89)))
    d.rounded_rectangle([x, y - h // 2, x + w, y + h // 2], radius=h // 2, fill=col)
    kx = x + 6 + (w - h) * on_p
    d.ellipse([kx, y - h // 2 + 6, kx + h - 12, y + h // 2 - 6], fill=(245, 245, 245))

def scene_toggles(dur, off="Spending", on="Saving"):
    f = ImageFont.truetype(SANS, 60)
    def draw(i, t):
        img = Image.new("RGB", (W, H), (8, 8, 8))
        d = ImageDraw.Draw(img)
        toggle(d, 640, H // 2 - 80, 1 - ease((t - 0.35) / 0.35), off, f)
        toggle(d, 640, H // 2 + 80, ease((t - 0.85) / 0.35), on, f)
        return img
    return draw, dur

def scene_clock(dur, txt="If not now, when?"):
    f = ImageFont.truetype(SERIF, 70)
    def draw(i, t):
        img = Image.new("RGB", (W, H), (8, 8, 8))
        d = ImageDraw.Draw(img)
        d.text(((W - d.textlength(txt, font=f)) / 2, H / 2 - 230), txt, font=f, fill=(235, 235, 230))
        cx, cy, r = W / 2, H / 2 + 60, 120
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(240, 240, 240), width=9)
        for k in range(12):
            a = k * math.pi / 6
            d.line([cx + math.sin(a) * (r - 22), cy - math.cos(a) * (r - 22), cx + math.sin(a) * (r - 12), cy - math.cos(a) * (r - 12)], fill=(240, 240, 240), width=4)
        am = t * 2 * math.pi * 0.9
        ah = am / 12 + 1.2
        d.line([cx, cy, cx + math.sin(ah) * 60, cy - math.cos(ah) * 60], fill=(240, 240, 240), width=8)
        d.line([cx, cy, cx + math.sin(am) * 92, cy - math.cos(am) * 92], fill=(240, 240, 240), width=5)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(240, 240, 240))
        return img
    return draw, dur

def scene_outro(dur):
    f2 = ImageFont.truetype(SANS, 40)
    def draw(i, t):
        img = bg_paper(i)
        highlight_text(img, ["Lessons every day."], t, start=0.1, per_word=0.25, cy=H // 2 - 40)
        p = ease((t - 1.0) / 0.4)
        if p > 0:
            d = ImageDraw.Draw(img, "RGBA")
            s = "RICH IN LIFE"
            d.text(((W - d.textlength(s, font=f2)) / 2, H // 2 + 60), s, font=f2, fill=INK + (int(220 * p),))
        return img
    return draw, dur

DISCLAIMER = "For education only. Not financial advice."

def load_scenes(path):
    spec = json.load(open(path))
    out = []
    for s in spec["scenes"]:
        k = s["type"]
        if k == "paper":
            out.append(scene_paper(s["lines"], s["seconds"], per_word=s.get("per_word", 0.32), size=s.get("size", 78)))
        elif k == "punch":
            out.append(scene_punch(s["text"], s["seconds"]))
        elif k == "toggles":
            out.append(scene_toggles(s["seconds"], s.get("off", "Spending"), s.get("on", "Saving")))
        elif k == "clock":
            out.append(scene_clock(s["seconds"], s.get("text", "If not now, when?")))
        elif k == "outro":
            out.append(scene_outro(s["seconds"]))
        else:
            raise ValueError(k)
    return out

SCENES = []

def disclaim(img):
    d = ImageDraw.Draw(img, "RGBA")
    f = ImageFont.truetype(SANS, 26)
    d.text(((W - d.textlength(DISCLAIMER, font=f)) / 2, H - 150), DISCLAIMER, font=f, fill=(200, 200, 200, 150))

def render(idx):
    draw, dur = SCENES[idx]
    n = int(round(dur * FPS))
    tmp = os.path.join(OUT, f"tmp_s{idx}.mp4")
    final = os.path.join(OUT, f"s{idx}.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "24", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(n):
        img = draw(i, i / FPS).convert("RGB")
        img = add_grain(img, i)
        disclaim(img)
        p.stdin.write(img.tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, final)

def still(idx, t, name):
    draw, _ = SCENES[idx]
    add_grain(draw(int(t * FPS), t).convert("RGB"), 0).save(os.path.join(OUT, name), quality=90)

if __name__ == "__main__":
    # usage: python3 make.py script.json out_dir   (writes out_dir/final.mp4 silent and out_dir/final_music.mp4 with the music bed)
    SCENES[:] = load_scenes(sys.argv[1])
    OUT = sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    for idx in range(len(SCENES)):
        render(idx)
    with open(os.path.join(OUT, "list.txt"), "w") as fh:
        fh.writelines(f"file 's{i}.mp4'\n" for i in range(len(SCENES)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "list.txt"), "-c", "copy", os.path.join(OUT, "final.mp4")], check=True)
    music = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highlighter_bed.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(OUT, "final.mp4"), "-stream_loop", "-1", "-i", music,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    os.path.join(OUT, "final_music.mp4")], check=True)
    print(os.path.join(OUT, "final_music.mp4"))
