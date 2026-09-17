"""Generate naive (brute-force) alignment demo GIF for cathedral.jpg.

Shows cathedral's red channel searching over its fixed blue channel.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CATH_JPG = ROOT / "uncolorized" / "cathedral.jpg"
OUT_GIF = ROOT / "naive_search.gif"

PANEL_W = 320
PAD = 18
BANNER = 36
TITLE_H = 28
SEARCH = 10  # ±SEARCH pixels
STEP = 2  # animate every STEP displacement (still scores all for best)


def cosine_score(im1, im2):
    img1 = im1.reshape(-1).astype(np.float64).copy()
    img2 = im2.reshape(-1).astype(np.float64).copy()
    if img1.size < 16 or img2.size < 16:
        return -1.0
    img1 -= img1.mean()
    img2 -= img2.mean()
    s1, s2 = img1.std(), img2.std()
    if s1 < 1e-8 or s2 < 1e-8:
        return -1.0
    img1 /= s1
    img2 /= s2
    denom = np.dot(img2, img2)
    if denom < 1e-8:
        return -1.0
    return float(np.dot(img1, img2) / denom)


def load_channels(path, work_w):
    raw = Image.open(path)
    arr = np.array(raw)
    if arr.dtype == np.uint16:
        im_full = arr.astype(np.float32) / 65535.0
    else:
        im_full = arr.astype(np.float32) / 255.0

    strip = Image.fromarray((np.clip(im_full, 0, 1) * 255).astype(np.uint8), mode="L")
    sh = max(1, int(strip.height * (work_w / strip.width)))
    strip = strip.resize((work_w, sh), Image.Resampling.LANCZOS)
    im = np.asarray(strip).astype(np.float32) / 255.0

    height = int(np.floor(im.shape[0] / 3.0))
    b = im[:height]
    g = im[height : 2 * height]
    r = im[2 * height : 3 * height]
    h = min(b.shape[0], g.shape[0], r.shape[0])
    return b[:h].copy(), g[:h].copy(), r[:h].copy()


def to_u8(a):
    return np.clip(a * 255.0, 0, 255).astype(np.uint8)


def tint_rgb(g, which):
    u = to_u8(g)
    z = np.zeros_like(u)
    if which == "b":
        return np.stack([z, z, u], axis=-1)
    if which == "g":
        return np.stack([z, u, z], axis=-1)
    return np.stack([u, z, z], axis=-1)


def overlay_rb(b, r, dx, dy, alpha_r=0.55):
    """Blue fixed + red shifted; additive-style overlay for misalignment visibility."""
    shifted = np.roll(np.roll(r, dy, 0), dx, 1)
    base = tint_rgb(b, "b").astype(np.float32)
    move = tint_rgb(shifted, "r").astype(np.float32)
    out = np.clip(base * (1.0 - alpha_r * 0.35) + move * alpha_r, 0, 255)
    return out.astype(np.uint8)


def score_at(b, r, dx, dy, crop):
    e1 = np.roll(np.roll(r, dy, 0), dx, 1)
    if crop * 2 >= min(e1.shape[0], e1.shape[1], b.shape[0], b.shape[1]):
        return -1.0
    return cosine_score(e1[crop:-crop, crop:-crop], b[crop:-crop, crop:-crop])


def find_best(b, r, start, end):
    best_x = best_y = 0
    best = -1e9
    crop = max(2, end - start)
    for x in range(start, end + 1):
        for y in range(start, end + 1):
            s = score_at(b, r, x, y, crop)
            if s > best:
                best, best_x, best_y = s, x, y
    return best_x, best_y, best


def make_canvas(w, h, bg=(245, 248, 252)):
    return np.full((h, w, 3), bg, dtype=np.uint8)


def paste(canvas, rgb, x, y):
    ch, cw = rgb.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.shape[1], x + cw), min(canvas.shape[0], y + ch)
    if x1 <= x0 or y1 <= y0:
        return
    sx0, sy0 = x0 - x, y0 - y
    canvas[y0:y1, x0:x1] = rgb[sy0 : sy0 + (y1 - y0), sx0 : sx0 + (x1 - x0)]


def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def label_frame(frame, text):
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, img.height - BANNER, img.width, img.height], fill=(26, 58, 92))
    font = get_font(13)
    draw.text((8, img.height - 24), text, fill=(232, 242, 255), font=font)
    return np.asarray(img)


def resize_to_width(rgb, width):
    img = Image.fromarray(rgb)
    h = max(1, int(img.height * (width / img.width)))
    return np.asarray(img.resize((width, h), Image.Resampling.LANCZOS))


def main():
    print("loading cathedral channels...")
    b, _g, r = load_channels(CATH_JPG, PANEL_W)

    print("finding best offset (full window)...")
    best_x, best_y, best_score = find_best(b, r, -SEARCH, SEARCH)
    print(f"cathedral R->B best: ({best_x}, {best_y}) score={best_score:.4f}")

    crop = max(2, 2 * SEARCH)
    panel = resize_to_width(overlay_rb(b, r, 0, 0), PANEL_W)
    panel_h, panel_w = panel.shape[0], panel.shape[1]

    page_w = PAD * 2 + panel_w
    content_top = PAD + TITLE_H
    page_h = content_top + panel_h + PAD + BANNER

    frames = []
    durations = []

    def add(frame, ms, caption):
        frames.append(label_frame(frame, caption))
        durations.append(ms)

    def compose(dx, dy, score, highlight=False):
        canvas = make_canvas(page_w, page_h)
        img = Image.fromarray(canvas)
        draw = ImageDraw.Draw(img)
        font = get_font(12)
        draw.rectangle([PAD, PAD, PAD + panel_w, PAD + TITLE_H - 4], fill=(26, 58, 92))
        draw.text((PAD + 8, PAD + 6), "cathedral — red on blue", fill=(232, 242, 255), font=font)
        canvas = np.asarray(img).copy()

        overlay = resize_to_width(overlay_rb(b, r, dx, dy), PANEL_W)
        paste(canvas, overlay, PAD, content_top)

        hud = Image.fromarray(canvas)
        d = ImageDraw.Draw(hud)
        font_s = get_font(11)
        ly = content_top + panel_h - 18
        d.rectangle([PAD, ly - 2, PAD + panel_w, ly + 16], fill=(26, 58, 92))
        d.text(
            (PAD + 4, ly),
            f"dx={dx:+d} dy={dy:+d}  NCC={score:.3f}",
            fill=(232, 242, 255),
            font=font_s,
        )
        if highlight:
            d.rectangle(
                [PAD - 2, content_top - 2, PAD + panel_w + 1, content_top + panel_h + 1],
                outline=(255, 200, 80),
                width=3,
            )
        return np.asarray(hud)

    # Intro: show the two channels side by side
    half_w = (panel_w - 10) // 2
    red_img = resize_to_width(tint_rgb(r, "r"), half_w)
    blue_img = resize_to_width(tint_rgb(b, "b"), half_w)
    intro = make_canvas(page_w, page_h)
    img = Image.fromarray(intro)
    draw = ImageDraw.Draw(img)
    font = get_font(12)
    draw.rectangle([PAD, PAD, PAD + panel_w, PAD + TITLE_H - 4], fill=(26, 58, 92))
    draw.text((PAD + 8, PAD + 6), "cathedral — split channels", fill=(232, 242, 255), font=font)
    intro = np.asarray(img).copy()
    y_mid = content_top + (panel_h - red_img.shape[0]) // 2
    paste(intro, blue_img, PAD, y_mid)
    paste(intro, red_img, PAD + half_w + 10, y_mid)
    add(intro, 2000, "cathedral: blue (fixed) and red (to align)")

    # Unaligned overlay at (0, 0)
    s0 = score_at(b, r, 0, 0, crop)
    add(compose(0, 0, s0), 1600, "Start at (0, 0) — try every offset in the window")

    # Brute-force raster
    running_best = -1e9
    offsets = [
        (x, y)
        for x in range(-SEARCH, SEARCH + 1, STEP)
        for y in range(-SEARCH, SEARCH + 1, STEP)
    ]

    for i, (dx, dy) in enumerate(offsets):
        score = score_at(b, r, dx, dy, crop)
        highlight = False
        hold = 50
        if score > running_best:
            running_best = score
            highlight = True
            hold = 180
        if i == len(offsets) - 1:
            hold = 500
        add(compose(dx, dy, score, highlight=highlight), hold, f"Brute-force scan  dx={dx:+d}  dy={dy:+d}")

    # Settle on best — hold 4s.
    # Many GIF players skip the *last* frame's delay when looping, and Pillow
    # merges identical consecutive frames — so add a 1px-different trailer.
    final = compose(best_x, best_y, best_score)
    add(final, 4000, f"Best offset: dx={best_x:+d}  dy={best_y:+d}  NCC={best_score:.3f}")
    trailer = final.copy()
    trailer[0, 0] = trailer[0, 0] ^ 1  # differ by 1 so Pillow won't merge frames
    add(trailer, 100, f"Best offset: dx={best_x:+d}  dy={best_y:+d}  NCC={best_score:.3f}")

    max_h = max(f.shape[0] for f in frames)
    max_w = max(f.shape[1] for f in frames)
    norm = []
    for f in frames:
        canvas = np.full((max_h, max_w, 3), 245, dtype=np.uint8)
        y = (max_h - f.shape[0]) // 2
        x = (max_w - f.shape[1]) // 2
        canvas[y : y + f.shape[0], x : x + f.shape[1]] = f
        norm.append(canvas)

    # Save with Pillow using millisecond durations (more reliable than imageio floats)
    print(f"writing {len(norm)} frames to {OUT_GIF}")
    pil_frames = [Image.fromarray(f) for f in norm]
    pil_frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=pil_frames[1:],
        duration=durations,  # milliseconds per frame
        loop=0,
        optimize=False,
        disposal=2,
    )
    print("saved", OUT_GIF, "size_mb", round(OUT_GIF.stat().st_size / 1e6, 2))


if __name__ == "__main__":
    main()
