"""Draws the kopi-kopi cursors and packs them into .cur files.

Shapes are polygons and circles on a 32x32 design grid. Each pixel's colour comes
from its *signed distance* to a shape (negative = inside), which gives us
outlines of any thickness and smooth (anti-aliased) edges at any size.

Layers, from the outside in:  dark edge  ->  white outline  ->  kopi blue.
The dark edge keeps the cursor visible on light backgrounds, the white on dark ones.

No OS code here, so the art can be previewed and tested anywhere.
"""

import math
import struct

# Classic arrow, tip at the top-left.
ARROW = [(1, 1), (1, 21), (6, 16.5), (9.5, 24.5), (13, 23), (9.5, 15), (16, 15)]
ARROW_HOTSPOT = (1, 1)

# Text cursor (I-beam), shifted left to leave room for the badge.
IBEAM = [(5, 4), (19, 4), (19, 8.5), (14.5, 8.5), (14.5, 23.5), (19, 23.5), (19, 28),
         (5, 28), (5, 23.5), (9.5, 23.5), (9.5, 8.5), (5, 8.5)]
IBEAM_HOTSPOT = (12, 16)

# Badges in the bottom-right corner, telling you which step you're on.
BADGE_CENTER, BADGE_RADIUS = (25, 25), 6.5
CHECK = [(21.8, 25.2), (24.2, 27.6), (28.4, 22.6)]  # the ✓ inside the "copied" badge

OUTLINE_W = 1.2   # white outline thickness, in design-grid pixels
EDGE_W = 1.0      # dark outer edge thickness
EDGE_COLOR = (20, 20, 30)
EDGE_ALPHA = 0.7


def _segment_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _polygon_sdf(p, poly):
    """Distance to the polygon's edge; negative when p is inside."""
    d = min(_segment_dist(p, poly[i - 1], poly[i]) for i in range(len(poly)))
    inside = False
    x, y = p
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return -d if inside else d


def _circle_sdf(p, center, r):
    return math.hypot(p[0] - center[0], p[1] - center[1]) - r


def _polyline_dist(p, pts):
    return min(_segment_dist(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def _cover(d, px):
    """How much of a pixel (0..1) lies inside, given the distance in grid units.

    `px` is the size of one output pixel in grid units; the 1-pixel ramp is the anti-aliasing.
    """
    return max(0.0, min(1.0, 0.5 - d / px))


def _over(dst, color, alpha):
    """Paint `color` with `alpha` on top of dst (straight RGBA, 0..1 floats)."""
    if alpha <= 0:
        return dst
    r, g, b, a = dst
    out_a = alpha + a * (1 - alpha)
    mix = lambda c_new, c_old: (c_new * alpha + c_old * a * (1 - alpha)) / out_a
    return (mix(color[0], r), mix(color[1], g), mix(color[2], b), out_a)


def _layers(pixel, d, px, fill, outline, edge):
    """Dark edge, then white outline, then blue fill, for one shape."""
    pixel = _over(pixel, edge, EDGE_ALPHA * _cover(d - EDGE_W, px))
    pixel = _over(pixel, outline, _cover(d, px))
    return _over(pixel, fill, _cover(d + OUTLINE_W, px))


def render(shape, hotspot, fill, outline, size=32, badge=None):
    """Return (pixels, hotspot): a size x size grid of 0..255 RGBA tuples.

    shape: ARROW or IBEAM.  badge: None, "start" (a ring) or "copied" (a tick).
    """
    px = 32 / size  # one output pixel, measured in design-grid units
    fill = tuple(c / 255 for c in fill)
    outline = tuple(c / 255 for c in outline)
    edge = tuple(c / 255 for c in EDGE_COLOR)
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            p = ((x + 0.5) * px, (y + 0.5) * px)
            pixel = (0.0, 0.0, 0.0, 0.0)
            pixel = _layers(pixel, _polygon_sdf(p, shape), px, fill, outline, edge)
            if badge:
                d = _circle_sdf(p, BADGE_CENTER, BADGE_RADIUS)
                pixel = _layers(pixel, d, px, fill, outline, edge)
                if badge == "start":  # punch a white hole: a ring means "waiting for the end"
                    pixel = _over(pixel, outline, _cover(d + 3.4, px))
                else:                 # a white tick means "copied, ready to paste"
                    pixel = _over(pixel, outline, _cover(_polyline_dist(p, CHECK) - 1.1, px))
            row.append(tuple(round(c * 255) for c in pixel))
        pixels.append(row)
    hx = min(size - 1, int(hotspot[0] / px))
    hy = min(size - 1, int(hotspot[1] / px))
    return pixels, (hx, hy)


def to_cur_bytes(pixels, hotspot):
    """Pack an RGBA grid into the Windows .cur file format (32-bit, with alpha)."""
    size = len(pixels)
    # Colour data: BGRA, rows stored bottom-up (a BMP quirk).
    xor = b"".join(bytes((b, g, r, a)) for row in reversed(pixels) for (r, g, b, a) in row)
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
