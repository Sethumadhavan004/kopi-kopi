"""Draws the kopi-kopi cursors and packs them into Windows cursor files.

Every shape lives on a 32x32 design grid. Each pixel's colour comes from its
*signed distance* to a shape (negative = inside), which gives outlines of any
thickness and smooth, anti-aliased edges at any size.

The pointer is a little galaxy: a bright core at the hotspot fading through
electric blue to deep indigo, a neon magenta rim and a soft violet glow.
A star in the bottom-right corner revolves. Its colour (HIKARI pastels) and its
motion tell you the step:
  yellow, calm spin         ready
  pink, spin + heartbeat    selecting (dragging, or start placed)
  green, calm spin          copied, ready to paste

Animation is an .ani file: Windows itself flips the frames, so kopi-kopi does
no work per frame and your clicks are never slowed down.

No OS code here, so the art can be previewed and tested anywhere.
"""

import math
import struct

# --- shapes (design grid units) ----------------------------------------------

ARROW = [(1, 1), (1, 21), (6, 16.5), (9.5, 24.5), (13, 23), (9.5, 15), (16, 15)]
ARROW_HOTSPOT = (1, 1)

IBEAM = [(6, 4), (17, 4), (17, 7.4), (13.3, 7.4), (13.3, 24.6), (17, 24.6), (17, 28),
         (6, 28), (6, 24.6), (9.7, 24.6), (9.7, 7.4), (6, 7.4)]
IBEAM_HOTSPOT = (11.5, 16)

STAR_CENTER = (24, 24)
STAR_OUTER, STAR_INNER = 6.6, 2.0  # a 4-point sparkle: long points, thin waist
GLOW_RADIUS = 4.0                  # how far the soft halo reaches past the star

RIM_W = 1.3    # magenta rim thickness on the pointer
GLOW_W = 2.6   # violet halo outside the rim, keeps it visible on dark backgrounds
STAR_EDGE_W = 0.9

FRAMES = 48         # frames per loop (1.6 s, so the heartbeat runs at about 75 bpm)
FRAME_JIFFIES = 2   # 1 jiffy = 1/60 s, so 2 = 30 frames per second

# --- distance helpers ----------------------------------------------------------


def _segment_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _polygon_sdf(px, py, poly):
    """Distance to the polygon's edge; negative when (px, py) is inside."""
    d = min(_segment_dist(px, py, *poly[i - 1], *poly[i]) for i in range(len(poly)))
    inside = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return -d if inside else d


def _cover(d, px):
    """How much of one output pixel (0..1) is inside; `px` = pixel size in grid units.

    The 1-pixel ramp around the edge is the anti-aliasing.
    """
    v = 0.5 - d / px
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def _over(dst, rgb, a):
    """Paint colour `rgb` (0..1) with alpha `a` over `dst` (premultiplied RGBA)."""
    if a <= 0:
        return dst
    k = 1 - a
    return (rgb[0] * a + dst[0] * k, rgb[1] * a + dst[1] * k,
            rgb[2] * a + dst[2] * k, a + dst[3] * k)


def _unit(rgb):
    return tuple(c / 255 for c in rgb)

# --- drawing ------------------------------------------------------------------


def star_points(angle, scale=1.0):
    """The 4-point sparkle as a polygon, rotated by `angle` radians."""
    cx, cy = STAR_CENTER
    pts = []
    for i in range(8):
        r = (STAR_OUTER if i % 2 == 0 else STAR_INNER) * scale
        a = angle + i * math.pi / 4 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def draw_pointer(shape, hotspot, size, colors):
    """The pointer on its own: a size x size grid of premultiplied RGBA floats.

    The body colour depends on the distance from the hotspot: bright core where
    you aim, electric blue in the middle, deep indigo at the far end.
    """
    px = 32 / size
    core, body, deep = _unit(colors["core"]), _unit(colors["body"]), _unit(colors["deep"])
    rim, glow = _unit(colors["rim"]), _unit(colors["glow"])
    hx, hy = hotspot
    reach = max(math.hypot(x - hx, y - hy) for x, y in shape)
    grid = []
    for y in range(size):
        row = []
        for x in range(size):
            gx, gy = (x + 0.5) * px, (y + 0.5) * px
            d = _polygon_sdf(gx, gy, shape)
            p = (0.0, 0.0, 0.0, 0.0)
            if 0 < d < GLOW_W:  # nebula glow, fading out
                fade = 1 - d / GLOW_W
                p = _over(p, glow, 0.55 * fade * fade)
            p = _over(p, rim, _cover(d, px))
            t = min(1.0, math.hypot(gx - hx, gy - hy) / reach)
            fill = _lerp(core, body, t / 0.45) if t < 0.45 else _lerp(body, deep, (t - 0.45) / 0.55)
            p = _over(p, fill, _cover(d + RIM_W, px))
            row.append(p)
        grid.append(row)
    return grid


def _star_box(size):
    """The pixel square the star and its glow can touch, so we only redraw that."""
    px = 32 / size
    reach = STAR_OUTER * MAX_SCALE + GLOW_RADIUS + 1
    lo = max(0, int((STAR_CENTER[0] - reach) / px))
    hi = min(size, int((STAR_CENTER[0] + reach) / px) + 1)
    return lo, hi


MAX_SCALE = 1.2  # the star's size at the peak of a heartbeat


def _beat(t, at, width):
    """A smooth bump centred at `at`, measured around the loop so it wraps cleanly."""
    d = abs(t - at)
    d = min(d, 1 - d)  # distance on a circle: 0.95 is close to 0.05
    return math.exp(-(d / width) ** 2)


def pulse(t, motion):
    """How "big" the star is at loop position t (0..1): returns 0..1.

    spin:       a slow, gentle breath
    heartbeat:  lub (strong) - dub (softer) - rest, like a heart
    """
    if motion == "heartbeat":
        return min(1.0, _beat(t, 0.12, 0.06) + 0.65 * _beat(t, 0.32, 0.06))
    return 0.5 - 0.5 * math.cos(2 * math.pi * t)


def draw_frame(base, frame, color, ink, light, motion="spin"):
    """One animation frame: the pointer plus the star at step `frame` of the loop."""
    size = len(base)
    px = 32 / size
    t = frame / FRAMES                     # 0..1 around the loop
    angle = t * math.pi / 2                # a quarter turn per loop: seamless for 4 points
    breathe = pulse(t, motion)
    grow = (MAX_SCALE - 0.92) if motion == "heartbeat" else 0.12
    star = star_points(angle, scale=0.92 + grow * breathe)
    color, ink, light = _unit(color), _unit(ink), _unit(light)
    glow_alpha = 0.25 + 0.35 * breathe
    cx, cy = STAR_CENTER

    grid = [row[:] for row in base]
    lo, hi = _star_box(size)
    for y in range(lo, hi):
        for x in range(lo, hi):
            gx, gy = (x + 0.5) * px, (y + 0.5) * px
            d = _polygon_sdf(gx, gy, star)
            p = grid[y][x]
            if d > 0:  # soft halo outside the star, fading with distance
                fade = max(0.0, 1 - d / GLOW_RADIUS)
                p = _over(p, color, glow_alpha * fade * fade)
            p = _over(p, ink, _cover(d - STAR_EDGE_W, px))
            p = _over(p, color, _cover(d, px))
            # a bright core, like light caught in the middle of the star
            core = math.hypot(gx - cx, gy - cy) - (0.9 + 0.5 * breathe)
            p = _over(p, light, 0.85 * _cover(core, px))
            grid[y][x] = p
    return grid


def hotspot_px(hotspot, size):
    px = 32 / size
    return min(size - 1, int(hotspot[0] / px)), min(size - 1, int(hotspot[1] / px))

# --- file formats ---------------------------------------------------------------


def to_cur_bytes(grid, hotspot):
    """Pack a premultiplied RGBA float grid into a .cur file (32-bit with alpha)."""
    size = len(grid)

    def bgra(p):
        r, g, b, a = p
        if a <= 0:
            return b"\0\0\0\0"
        # .cur wants straight (not premultiplied) alpha
        return bytes((round(b / a * 255), round(g / a * 255), round(r / a * 255), round(a * 255)))

    # Colour data: BGRA, rows stored bottom-up (a BMP quirk).
    xor = b"".join(bgra(p) for row in reversed(grid) for p in row)
    # AND mask: 1 bit per pixel, rows padded to 4 bytes. All zero, because alpha does the work.
    and_mask = bytes(((size + 31) // 32) * 4 * size)
    header = struct.pack(
        "<IiiHHIIiiII",
        40, size, size * 2,  # height is doubled: XOR image + AND mask
        1, 32, 0, len(xor) + len(and_mask), 0, 0, 0, 0,
    )
    image = header + xor + and_mask
    icondir = struct.pack("<HHH", 0, 2, 1)  # type 2 = cursor, 1 image
    entry = struct.pack(
        "<BBBBHHII",
        size % 256, size % 256, 0, 0,
        hotspot[0], hotspot[1],  # for cursors these two fields are the hotspot
        len(image), 6 + 16,
    )
    return icondir + entry + image


def _chunk(tag, data):
    pad = b"\0" if len(data) % 2 else b""
    return tag + struct.pack("<I", len(data)) + data + pad


def to_ani_bytes(frames, hotspot, jiffies=FRAME_JIFFIES):
    """Pack frames into an animated cursor (.ani): a RIFF file holding one .cur per frame."""
    n = len(frames)
    # anih header: size, frames, steps, (w, h, bits, planes: unused), rate, flags (1 = frames are .cur data)
    anih = struct.pack("<9I", 36, n, n, 0, 0, 0, 0, jiffies, 1)
    icons = b"".join(_chunk(b"icon", to_cur_bytes(f, hotspot)) for f in frames)
    body = b"ACON" + _chunk(b"anih", anih) + _chunk(b"LIST", b"fram" + icons)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def build_ani(shape, hotspot, size, colors, star_color, motion="spin"):
    """Everything above in one call: draw the pointer, animate the star, pack an .ani."""
    base = draw_pointer(shape, hotspot, size, colors)
    frames = [draw_frame(base, i, star_color, colors["ink"], colors["light"], motion)
              for i in range(FRAMES)]
    return to_ani_bytes(frames, hotspot_px(hotspot, size))
