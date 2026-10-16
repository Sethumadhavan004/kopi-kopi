"""Draws the blue cursors from ASCII art and packs them into .cur files.

  'O' = outline colour, '#' = fill colour (kopi blue), '.' = transparent.

No OS code here, so the art can be previewed and tested anywhere.
"""

import struct

ARROW = [
    "O...........",
    "OO..........",
    "O#O.........",
    "O##O........",
    "O###O.......",
    "O####O......",
    "O#####O.....",
    "O######O....",
    "O#######O...",
    "O########O..",
    "O#########O.",
    "O######OOOOO",
    "O###O##O....",
    "O##OO##O....",
    "O#O..O##O...",
    "OO...O##O...",
    "O.....O##O..",
    "......O##O..",
    ".......OO...",
]
ARROW_HOTSPOT = (0, 0)  # the tip

IBEAM = [
    "OOOO.OOOO",
    "O###O###O",
    "OOOO#OOOO",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "...O#O...",
    "OOOO#OOOO",
    "O###O###O",
    "OOOO.OOOO",
]
IBEAM_HOTSPOT = (4, 8)  # middle of the stem


def render(art, hotspot, fill, outline, size=32):
    """Return (pixels, hotspot) where pixels is a size x size grid of RGBA tuples.

    The art is drawn for a 32 px cursor and scaled (nearest neighbour) to `size`,
    so it matches the system cursor size on high-DPI screens.
    """
    scale = size / 32
    colors = {"O": outline + (255,), "#": fill + (255,)}
    clear = (0, 0, 0, 0)
    # Centre narrow art (the I-beam) horizontally; keep the arrow at the top-left.
    ox = 0 if art is ARROW else (32 - len(art[0])) // 2
    oy = 0 if art is ARROW else (32 - len(art)) // 2
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            ax, ay = int(x / scale) - ox, int(y / scale) - oy
            ch = art[ay][ax] if 0 <= ay < len(art) and 0 <= ax < len(art[ay]) else "."
            row.append(colors.get(ch, clear))
        pixels.append(row)
    hx = min(size - 1, int((hotspot[0] + ox + 0.5) * scale))
    hy = min(size - 1, int((hotspot[1] + oy + 0.5) * scale))
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
