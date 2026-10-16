import struct

from kopi_kopi import config
from kopi_kopi.cursor_art import (
    ARROW, ARROW_HOTSPOT, FRAME_JIFFIES, FRAMES, build_ani, draw_frame, draw_pointer,
)

C = config.CURSOR_COLORS


def chunks(data):
    """Walk RIFF chunks: yields (tag, payload)."""
    i = 0
    while i < len(data):
        tag, n = data[i:i + 4], struct.unpack("<I", data[i + 4:i + 8])[0]
        yield tag, data[i + 8:i + 8 + n]
        i += 8 + n + (n % 2)


def test_ani_file_structure():
    data = build_ani(ARROW, ARROW_HOTSPOT, 32, C, *config.STARS["armed"])
    assert data[:4] == b"RIFF" and data[8:12] == b"ACON"
    assert struct.unpack("<I", data[4:8])[0] == len(data) - 8
    found = dict(chunks(data[12:]))
    anih = struct.unpack("<9I", found[b"anih"])
    assert anih[0] == 36 and anih[1] == FRAMES and anih[7] == FRAME_JIFFIES and anih[8] == 1
    fram = found[b"LIST"]
    assert fram[:4] == b"fram"
    icons = [payload for tag, payload in chunks(fram[4:]) if tag == b"icon"]
    assert len(icons) == FRAMES
    for icon in icons:
        reserved, kind, count = struct.unpack("<HHH", icon[:6])
        hotspot = struct.unpack("<HH", icon[10:14])
        assert (reserved, kind, count) == (0, 2, 1)  # one cursor image
        assert hotspot == (1, 1)                     # the arrow's tip


def test_animation_loops_without_a_jump():
    base = draw_pointer(ARROW, ARROW_HOTSPOT, 32, C)
    for color, motion in config.STARS.values():
        first = draw_frame(base, 0, color, C["ink"], C["light"], motion)
        after_last = draw_frame(base, FRAMES, color, C["ink"], C["light"], motion)
        worst = max(abs(a - b) for r1, r2 in zip(first, after_last)
                    for p1, p2 in zip(r1, r2) for a, b in zip(p1, p2))
        assert worst < 1e-6, motion


def test_star_only_touches_its_corner():
    # The pointer itself must look identical in every frame; only the star moves.
    base = draw_pointer(ARROW, ARROW_HOTSPOT, 32, C)
    color, motion = config.STARS["selecting"]
    frame = draw_frame(base, 7, color, C["ink"], C["light"], motion)
    assert frame[2][2] == base[2][2]  # near the tip
