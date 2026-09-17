"""Generate process demo GIF for self_portrait — vertical cut/spread/stack."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TIF = ROOT / "uncolorized" / "self_portrait.tif"
OUT_GIF = ROOT / "process_self_portrait.gif"
FINAL_PNG = ROOT / "out" / "strong_self_portrait.png"

WORK_W = 280
DISP_W = 280
PAD = 28
GAP = 20  # vertical gap between split pieces
BANNER = 34


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


def align_bruteforce(im1, im2, start=-12, end=12):
    best_x = best_y = 0
    best = -1e9
    crop = max(2, (end - start))
    for x in range(start, end + 1):
        for y in range(start, end + 1):
            e1 = np.roll(np.roll(im1, y, 0), x, 1)
            if crop * 2 >= min(e1.shape[0], e1.shape[1], im2.shape[0], im2.shape[1]):
                continue
            score = cosine_score(e1[crop:-crop, crop:-crop], im2[crop:-crop, crop:-crop])
            if score > best:
                best, best_x, best_y = score, x, y
    return best_x, best_y


def align_pyramid(im1, im2, max_size=120, cut=2, window=12):
    if max(im2.shape) > max_size:

        def down(a):
            img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
            nw, nh = max(1, a.shape[1] // cut), max(1, a.shape[0] // cut)
            return np.asarray(img.resize((nw, nh), Image.Resampling.LANCZOS)).astype(np.float32) / 255.0

        x, y = align_pyramid(down(im1), down(im2), max_size, cut, window)
        absx, absy = (abs(x) + 1) * 2, (abs(y) + 1) * 2
        crop_x, crop_y = absx * cut, absy * cut
        edited = np.roll(np.roll(im1, y * cut, 0), x * cut, 1)
        if crop_y * 2 >= edited.shape[0] or crop_x * 2 >= edited.shape[1]:
            return x * cut, y * cut
        fx, fy = align_bruteforce(
            edited[crop_y:-crop_y, crop_x:-crop_x],
            im2[crop_y:-crop_y, crop_x:-crop_x],
            -window,
            window,
        )
        return x * cut + fx, y * cut + fy
    return align_bruteforce(im1, im2, -window, window)


def to_u8(a):
    return np.clip(a * 255.0, 0, 255).astype(np.uint8)


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


def gray_rgb(g):
    u = to_u8(g)
    return np.stack([u, u, u], axis=-1)


def tint_rgb(g, which):
    u = to_u8(g)
    z = np.zeros_like(u)
    if which == "b":
        return np.stack([z, z, u], axis=-1)
    if which == "g":
        return np.stack([z, u, z], axis=-1)
    return np.stack([u, z, z], axis=-1)


def compose_rgb(b, g=None, r=None, g_align=(0, 0), r_align=(0, 0)):
    """True channel stack like np.dstack([r, g, b])."""
    rgb = np.zeros(b.shape + (3,), dtype=np.float32)
    rgb[:, :, 2] = b
    if g is not None:
        gx, gy = g_align
        rgb[:, :, 1] = np.roll(np.roll(g, gy, 0), gx, 1)
    if r is not None:
        rx, ry = r_align
        rgb[:, :, 0] = np.roll(np.roll(r, ry, 0), rx, 1)
    return to_u8(np.clip(rgb, 0, 1))


def label_frame(frame, text):
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, img.height - BANNER, img.width, img.height], fill=(26, 58, 92))
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    draw.text((8, img.height - 24), text, fill=(232, 242, 255), font=font)
    return np.asarray(img)


def ease(t):
    return t * t * (3 - 2 * t)


def main():
    raw = Image.open(TIF)
    im_full = np.array(raw).astype(np.float32) / 65535.0

    strip_img = Image.fromarray(to_u8(im_full), mode="L")
    sh = max(1, int(strip_img.height * (WORK_W / strip_img.width)))
    strip_img = strip_img.resize((WORK_W, sh), Image.Resampling.LANCZOS)
    im = np.asarray(strip_img).astype(np.float32) / 255.0

    height = int(np.floor(im.shape[0] / 3.0))
    b = im[:height]
    g = im[height : 2 * height]
    r = im[2 * height : 3 * height]
    h = min(b.shape[0], g.shape[0], r.shape[0])
    b, g, r = b[:h].copy(), g[:h].copy(), r[:h].copy()
    print("channels", b.shape)

    print("aligning...")
    gx, gy = align_pyramid(g, b)
    rx, ry = align_pyramid(r, b)
    print("offsets G", gx, gy, "R", rx, ry)

    ch_h, ch_w = b.shape
    strip_u8 = to_u8(im)

    # Page layout: strip centered horizontally
    page_w = max(ch_w + PAD * 2, DISP_W + PAD * 2)
    x0 = (page_w - ch_w) // 2

    # Y positions for contiguous strip (no gaps) — B, G, R top to bottom
    y_b0 = PAD
    y_g0 = PAD + ch_h
    y_r0 = PAD + 2 * ch_h

    # Y positions after vertical spread
    y_b1 = PAD
    y_g1 = PAD + ch_h + GAP
    y_r1 = PAD + 2 * (ch_h + GAP)

    spread_h = y_r1 + ch_h + PAD + BANNER
    strip_h = y_r0 + ch_h + PAD + BANNER

    frames = []
    durations = []

    def add(frame, ms, caption):
        frames.append(label_frame(frame, caption))
        durations.append(ms)

    def place_three(y_b, y_g, y_r, img_b, img_g, img_r, canvas_h=None):
        hgt = canvas_h or max(y_b, y_g, y_r) + ch_h + PAD + BANNER
        canvas = make_canvas(page_w, hgt)
        paste(canvas, img_b, x0, y_b)
        paste(canvas, img_g, x0, y_g)
        paste(canvas, img_r, x0, y_r)
        return canvas

    # ---- Step 1: strip cuts into 3 (still touching) ----
    strip_frame = make_canvas(page_w, strip_h)
    paste(strip_frame, np.stack([strip_u8] * 3, axis=-1), x0, PAD)
    add(strip_frame, 1800, "1. Glass-plate strip (B / G / R stacked)")

    cut_frame = place_three(
        y_b0, y_g0, y_r0, gray_rgb(b), gray_rgb(g), gray_rgb(r), canvas_h=strip_h
    )
    # Draw cut lines
    cut_img = Image.fromarray(cut_frame)
    draw = ImageDraw.Draw(cut_img)
    for y in (y_g0, y_r0):
        draw.line([(x0, y), (x0 + ch_w, y)], fill=(26, 58, 92), width=2)
    cut_frame = np.asarray(cut_img)

    # Translate: strip → cut pieces (brief hold on cuts)
    n_cut = 8
    for i in range(1, n_cut + 1):
        t = ease(i / n_cut)
        # Cross-dissolve only for revealing cut lines on same layout
        blend = np.clip(
            strip_frame.astype(np.float32) * (1 - t) + cut_frame.astype(np.float32) * t, 0, 255
        ).astype(np.uint8)
        add(blend, 80 if i < n_cut else 700, "1. Cut into three channel plates")

    # ---- Step 2: pieces spread vertically ~20px ----
    n_spread = 18
    for i in range(n_spread + 1):
        t = ease(i / n_spread)
        yb = int(round(y_b0 + (y_b1 - y_b0) * t))
        yg = int(round(y_g0 + (y_g1 - y_g0) * t))
        yr = int(round(y_r0 + (y_r1 - y_r0) * t))
        frame = place_three(yb, yg, yr, gray_rgb(b), gray_rgb(g), gray_rgb(r), canvas_h=spread_h)
        add(frame, 90 if i < n_spread else 1600, "2. Separate the three exposures")

    # ---- Step 3: color the pieces (tint in place) ----
    gray_spread = place_three(y_b1, y_g1, y_r1, gray_rgb(b), gray_rgb(g), gray_rgb(r), canvas_h=spread_h)
    tint_spread = place_three(
        y_b1, y_g1, y_r1, tint_rgb(b, "b"), tint_rgb(g, "g"), tint_rgb(r, "r"), canvas_h=spread_h
    )
    n_tint = 20
    for i in range(1, n_tint + 1):
        t = ease(i / n_tint)
        blend = np.clip(
            gray_spread.astype(np.float32) * (1 - t) + tint_spread.astype(np.float32) * t, 0, 255
        ).astype(np.uint8)
        add(blend, 100 if i < n_tint else 2200, "3. Tint each plate with its filter color")

    # ---- Steps 4 & 5: G and R slide onto blue at the same speed ----
    # Real-time overlap: each plate writes into its R/G/B plane at its current
    # Y; wherever rectangles overlap, you see true channel addition (not a snap).
    g_data = np.roll(np.roll(g, gy, 0), gx, 1)
    r_data = np.roll(np.roll(r, ry, 0), rx, 1)

    dist_g = y_g1 - y_b1
    dist_r = y_r1 - y_b1
    speed = max(1.0, dist_g / 22.0)
    frames_total = int(np.ceil(dist_r / speed)) + 1

    def render_planes(yb, yg, yr):
        """Compose R/G/B planes at plate positions — overlaps add in real time."""
        top = min(yb, yg, yr)
        bot = max(yb, yg, yr) + ch_h
        hgt = bot - top
        planes = np.zeros((hgt, ch_w, 3), dtype=np.float32)

        def write(plane, data, y_pos):
            y0 = y_pos - top
            planes[y0 : y0 + ch_h, :, plane] = data

        write(2, b, yb)
        write(1, g_data, yg)
        write(0, r_data, yr)
        return to_u8(np.clip(planes, 0, 1)), top

    green_landed_beat = False
    for i in range(frames_total + 1):
        traveled = i * speed
        yg = int(round(max(y_b1, y_g1 - traveled)))
        yr = int(round(max(y_b1, y_r1 - traveled)))

        rgb, top = render_planes(y_b1, yg, yr)
        canvas = make_canvas(page_w, spread_h)
        paste(canvas, rgb, x0, top)

        g_here = yg <= y_b1
        r_here = yr <= y_b1
        if not g_here:
            caption = "4. Slide green and red onto blue"
            hold = 90
        elif not r_here:
            caption = "4. Green overlapping blue"
            hold = 90
            if not green_landed_beat and g_here:
                hold = 450
                green_landed_beat = True
        else:
            caption = "5. Red overlapping blue + green"
            hold = 90 if i < frames_total else 1400

        add(canvas, hold, caption)

    # White-balanced full stack — end hold via repeated frames (many players
    # ignore a single long delay on the last frame before looping).
    rgb_f = np.stack([r_data, g_data, b], axis=-1)
    means = rgb_f.mean(axis=(0, 1))
    mult = means.mean() / np.maximum(means, 1e-6)
    rgb_balanced = to_u8(np.clip(rgb_f * mult, 0, 1))

    stacked_base = make_canvas(page_w, spread_h)
    paste(stacked_base, rgb_balanced, x0, y_b1)
    FINAL_HOLD_MS = 4000
    TICK_MS = 100
    ticks = FINAL_HOLD_MS // TICK_MS
    for i in range(ticks):
        # Tiny per-frame difference so encoders don't coalesce into one
        # long-delay frame (browsers often skip that before looping).
        tick = stacked_base.copy()
        tick[0, i % tick.shape[1]] = (tick[0, i % tick.shape[1]].astype(np.int16) + (1 if i % 2 == 0 else -1)).clip(0, 255).astype(np.uint8)
        add(tick, TICK_MS, "6. Colorized self_portrait")

    # Normalize frame sizes
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
