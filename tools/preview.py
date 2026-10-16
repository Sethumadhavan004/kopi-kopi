"""Renders the kopi-kopi cursors as an animated GIF, to check the art (or share it).

    pip install pillow
    python tools/preview.py docs/cursors.gif           (add --ibeam to include the text cursor)

Not needed to run kopi-kopi; Pillow is only used here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image  # noqa: E402

from kopi_kopi import config  # noqa: E402
from kopi_kopi.cursor_art import (  # noqa: E402
    ARROW, ARROW_HOTSPOT, FRAME_JIFFIES, FRAMES, IBEAM, IBEAM_HOTSPOT, draw_frame, draw_pointer,
)

SIZE, ZOOM, CELL = 64, 2, 140
LOOKS = ["armed", "start", "copied"]
GROUNDS = [(0x12, 0x0A, 0x0B), (0xFF, 0xF4, 0xF0)]  # HIKARI paper: Ankoku dark, Hikari light


def to_image(grid):
    img = Image.new("RGBA", (len(grid), len(grid)))
    img.putdata([
        (0, 0, 0, 0) if a <= 0 else
        (round(r / a * 255), round(g / a * 255), round(b / a * 255), round(a * 255))
        for row in grid for (r, g, b, a) in row
    ])
    return img.resize((len(grid) * ZOOM,) * 2, Image.LANCZOS)


def main(out):
    c = config.CURSOR_COLORS
    shapes = [(ARROW, ARROW_HOTSPOT)] + ([(IBEAM, IBEAM_HOTSPOT)] if "--ibeam" in sys.argv else [])
    bases = [draw_pointer(shape, hotspot, SIZE, c) for shape, hotspot in shapes]
    frames = []
    for i in range(FRAMES):
        sheet = Image.new("RGB", (CELL * len(LOOKS) * len(bases), CELL * len(GROUNDS)))
        for gi, ground in enumerate(GROUNDS):
            sheet.paste(ground, (0, gi * CELL, sheet.width, (gi + 1) * CELL))
            for li, look in enumerate(LOOKS):
                for bi, base in enumerate(bases):
                    img = to_image(draw_frame(base, i, config.STAR_COLORS[look], c["ink"], c["light"]))
                    x = (li * len(bases) + bi) * CELL + (CELL - img.width) // 2
                    sheet.paste(img, (x, gi * CELL + (CELL - img.height) // 2), img)
        frames.append(sheet.quantize(64, dither=Image.Dither.NONE))  # fewer colours = smaller GIF
    frames[0].save(out, save_all=True, append_images=frames[1:], loop=0,
                   duration=round(FRAME_JIFFIES * 1000 / 60), optimize=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else "cursors.gif")
