"""Draws the app icon (the galaxy arrow with its yellow star) as a multi-size .ico.

    pip install pillow
    python packaging/make_icon.py packaging/kopi-kopi.ico
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image  # noqa: E402

from kopi_kopi import config  # noqa: E402
from kopi_kopi.cursor_art import ARROW, ARROW_HOTSPOT, draw_frame, draw_pointer  # noqa: E402

SIZE = 256


def main(out):
    c = config.CURSOR_COLORS
    color, motion = config.STARS["armed"]
    grid = draw_frame(draw_pointer(ARROW, ARROW_HOTSPOT, SIZE, c), 0, color, c["ink"], c["light"], motion)
    img = Image.new("RGBA", (SIZE, SIZE))
    img.putdata([
        (0, 0, 0, 0) if a <= 0 else
        (round(r / a * 255), round(g / a * 255), round(b / a * 255), round(a * 255))
        for row in grid for (r, g, b, a) in row
    ])
    # The cursor sits in the corner of its canvas; crop to the drawing and centre it.
    art = img.crop(img.getbbox())
    side = round(max(art.size) * 1.06)
    icon = Image.new("RGBA", (side, side))
    icon.paste(art, ((side - art.width) // 2, (side - art.height) // 2))
    icon = icon.resize((SIZE, SIZE), Image.LANCZOS)
    icon.save(out, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "kopi-kopi.ico")
