"""Generate image-pyramid demo GIF for self_portrait."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TIF = ROOT / "uncolorized" / "self_portrait.tif"
OUT_GIF = ROOT / "pyramid_self_portrait.gif"

FULL_W = 200
GAP = 14
COL_GAP = 22
PAD = 24
BANNER = 34
BG = (245, 248, 252)


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


def resize_gray(a, width):
    img = Image.fromarray(to_u8(a), mode="L")
    h = max(1, int(round(img.height * (width / img.width))))
    return np.asarray(img.resize((width, h), Image.Resampling.LANCZOS)).astype(np.float32) / 255.0


def make_canvas(w, h, bg=BG):
    return np.full((h, w, 3), bg, dtype=np.uint8)


def paste(canvas, rgb, x, y):
    ch, cw = rgb.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.shape[1], x + cw), min(canvas.shape[0], y + ch)
    if x1 <= x0 or y1 <= y0:
        return
    sx0, sy0 = x0 - x, y0 - y
    canvas[y0:y1, x0:x1] = rgb[sy0 : sy0 + (y1 - y0), sx0 : sx0 + (x1 - x0)]


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


def white_balance(rgb_f):
    means = rgb_f.mean(axis=(0, 1))
    mult = means.mean() / np.maximum(means, 1e-6)
    return to_u8(np.clip(rgb_f * mult, 0, 1))


class ScaleStack:
    """One matryoshka column: B/G/R plates that can consolidate."""

    def __init__(self, b, g, r, gx, gy, rx, ry, label, x):
        self.b = b
        self.g = g
        self.r = r
        self.g_data = np.roll(np.roll(g, gy, 0), gx, 1)
        self.r_data = np.roll(np.roll(r, ry, 0), rx, 1)
        self.label = label
        self.x = x
        self.h, self.w = b.shape
        self.y_b = None  # set after layout
        self.y_g_spread = None
        self.y_r_spread = None
        self.consolidated = False
        self.yg = None
        self.yr = None

    def spread_height(self):
        return 3 * self.h + 2 * GAP

    def set_bottom(self, bottom_y):
        """Bottom-align the spread stack so dolls stand on one baseline."""
        spread_h = self.spread_height()
        top = bottom_y - spread_h
        self.y_b = top
        self.y_g_spread = top + self.h + GAP
        self.y_r_spread = top + 2 * (self.h + GAP)
        self.yg = self.y_g_spread
        self.yr = self.y_r_spread

    def render_planes(self, yg, yr):
        top = min(self.y_b, yg, yr)
        bot = max(self.y_b, yg, yr) + self.h
        planes = np.zeros((bot - top, self.w, 3), dtype=np.float32)

        def write(plane, data, y_pos):
            y0 = y_pos - top
            planes[y0 : y0 + self.h, :, plane] = data

        write(2, self.b, self.y_b)
        write(1, self.g_data, yg)
        write(0, self.r_data, yr)
        return to_u8(np.clip(planes, 0, 1)), top

    def final_rgb(self):
        rgb_f = np.stack([self.r_data, self.g_data, self.b], axis=-1)
        return white_balance(rgb_f)

    def draw(self, canvas, yg=None, yr=None):
        if self.consolidated and yg is None and yr is None:
            paste(canvas, self.final_rgb(), self.x, self.y_b)
            return
        yg = self.yg if yg is None else yg
        yr = self.yr if yr is None else yr
        rgb, top = self.render_planes(yg, yr)
        paste(canvas, rgb, self.x, top)


def main():
    raw = Image.open(TIF)
    im_full = np.array(raw).astype(np.float32) / 65535.0

    # Working full-res strip
    strip = Image.fromarray(to_u8(im_full), mode="L")
    sh = max(1, int(round(strip.height * (FULL_W / strip.width))))
    strip = np.asarray(strip.resize((FULL_W, sh), Image.Resampling.LANCZOS)).astype(np.float32) / 255.0

    height = int(np.floor(strip.shape[0] / 3.0))
    b0 = strip[:height]
    g0 = strip[height : 2 * height]
    r0 = strip[2 * height : 3 * height]
    h = min(b0.shape[0], g0.shape[0], r0.shape[0])
    b0, g0, r0 = b0[:h].copy(), g0[:h].copy(), r0[:h].copy()

    print("aligning full...")
    gx0, gy0 = align_pyramid(g0, b0)
    rx0, ry0 = align_pyramid(r0, b0)
    print("full offsets", gx0, gy0, rx0, ry0)

    def level(scale):
        w = max(1, int(round(FULL_W * scale)))
        b = resize_gray(b0, w)
        g = resize_gray(g0, w)
        r = resize_gray(r0, w)
        # scale alignment offsets to this level
        gx = int(round(gx0 * scale))
        gy = int(round(gy0 * scale))
        rx = int(round(rx0 * scale))
        ry = int(round(ry0 * scale))
        return b, g, r, gx, gy, rx, ry

    b1, g1, r1, gx1, gy1, rx1, ry1 = level(1.0)
    b2, g2, r2, gx2, gy2, rx2, ry2 = level(0.5)
    b4, g4, r4, gx4, gy4, rx4, ry4 = level(0.25)

    # Columns left → right: full, half, quarter (matryoshka)
    x_full = PAD
    x_half = x_full + b1.shape[1] + COL_GAP
    x_quarter = x_half + b2.shape[1] + COL_GAP

    stacks = [
        ScaleStack(b1, g1, r1, gx1, gy1, rx1, ry1, "1×", x_full),
        ScaleStack(b2, g2, r2, gx2, gy2, rx2, ry2, "½×", x_half),
        ScaleStack(b4, g4, r4, gx4, gy4, rx4, ry4, "¼×", x_quarter),
    ]

    page_w = x_quarter + b4.shape[1] + PAD
    # Bottom-align all spread stacks
    max_spread = max(s.spread_height() for s in stacks)
    bottom = PAD + max_spread
    for s in stacks:
        s.set_bottom(bottom)

    page_h = bottom + PAD + BANNER

    # Labels under each column (above banner)
    def draw_labels(canvas):
        img = Image.fromarray(canvas)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except OSError:
            font = ImageFont.load_default()
        for s in stacks:
            text = s.label
            tw = draw.textlength(text, font=font) if hasattr(draw, "textlength") else 20
            draw.text((s.x + (s.w - tw) / 2, bottom + 4), text, fill=(58, 98, 138), font=font)
        return np.asarray(img)

    frames = []
    durations = []

    def add(frame, ms, caption):
        labeled = label_frame(draw_labels(frame), caption)
        frames.append(labeled)
        durations.append(ms)

    def render_all():
        canvas = make_canvas(page_w, page_h)
        for s in stacks:
            s.draw(canvas)
        return canvas

    # Intro: all three spread
    add(render_all(), 2200, "Image pyramid: 1×, ½×, and ¼× stacks")

    def consolidate(stack_index, caption_prefix):
        s = stacks[stack_index]
        dist_g = s.y_g_spread - s.y_b
        dist_r = s.y_r_spread - s.y_b
        # Faster on smaller dolls, still readable
        steps_g = max(10, int(18 * (s.w / FULL_W)))
        speed = max(1.0, dist_g / steps_g)
        total = int(np.ceil(dist_r / speed)) + 1
        green_beat = False

        for i in range(total + 1):
            traveled = i * speed
            yg = int(round(max(s.y_b, s.y_g_spread - traveled)))
            yr = int(round(max(s.y_b, s.y_r_spread - traveled)))
            s.yg, s.yr = yg, yr

            canvas = make_canvas(page_w, page_h)
            for other in stacks:
                if other is s:
                    other.draw(canvas, yg=yg, yr=yr)
                else:
                    other.draw(canvas)

            g_here = yg <= s.y_b
            r_here = yr <= s.y_b
            if not g_here:
                caption = f"{caption_prefix}: slide green & red onto blue"
                hold = 70
            elif not r_here:
                caption = f"{caption_prefix}: green overlapping blue"
                hold = 70
                if not green_beat:
                    hold = 350
                    green_beat = True
            else:
                caption = f"{caption_prefix}: stacked"
                hold = 70 if i < total else 900

            add(canvas, hold, caption)

        s.consolidated = True
        s.yg, s.yr = s.y_b, s.y_b
        # Settle on white-balanced result
        canvas = make_canvas(page_w, page_h)
        for other in stacks:
            other.draw(canvas)
        add(canvas, 700, f"{caption_prefix}: aligned result")

    # Quarter → half → full
    consolidate(2, "¼× (coarse)")
    consolidate(1, "½× (mid)")
    consolidate(0, "1× (full)")

    # Final hold via repeated slightly-unique frames
    final = render_all()
    FINAL_HOLD_MS = 4000
    TICK = 100
    for i in range(FINAL_HOLD_MS // TICK):
        tick = final.copy()
        tick[0, i % tick.shape[1]] = (
            tick[0, i % tick.shape[1]].astype(np.int16) + (1 if i % 2 == 0 else -1)
        ).clip(0, 255).astype(np.uint8)
        add(tick, TICK, "Coarse-to-fine pyramid alignment")

    max_h = max(f.shape[0] for f in frames)
    max_w = max(f.shape[1] for f in frames)
    norm = []
    for f in frames:
        canvas = np.full((max_h, max_w, 3), BG, dtype=np.uint8)
        y = (max_h - f.shape[0]) // 2
        x = (max_w - f.shape[1]) // 2
        canvas[y : y + f.shape[0], x : x + f.shape[1]] = f
        norm.append(canvas)

    print(f"writing {len(norm)} frames to {OUT_GIF}")
    pil_frames = [Image.fromarray(f) for f in norm]
    pil_frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=pil_frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )
    print("saved", OUT_GIF, "size_mb", round(OUT_GIF.stat().st_size / 1e6, 2))


if __name__ == "__main__":
    main()
