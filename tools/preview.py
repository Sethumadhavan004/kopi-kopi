"""Renders the kopi-kopi cursors, to check the art or use it elsewhere.

    pip install pillow
    python tools/preview.py docs/cursors.gif             an animated preview sheet
    python tools/preview.py docs/cursors.gif --ibeam     ...including the text cursor
    python tools/preview.py --frames out/cursor-frames   every frame as a transparent PNG
                                                         (for videos and motion graphics)

Not needed to run kopi-kopi; Pillow is only used here.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image  # noqa: E402

from kopi_kopi import config  # noqa: E402
from kopi_kopi.cursor_art import (  # noqa: E402
    ARROW,
    ARROW_HOTSPOT,
    FRAME_JIFFIES,
    FRAMES,
    IBEAM,
    IBEAM_HOTSPOT,
    draw_frame,
    draw_pointer,
)

SIZE, ZOOM, CELL = 64, 2, 140
LOOKS = ["armed", "selecting", "copied"]
GROUNDS = [(0x12, 0x0A, 0x0B), (0xFF, 0xF4, 0xF0)]  # HIKARI paper: Ankoku dark, Hikari light


def to_image(grid):
    return to_rgba(grid).resize((len(grid) * ZOOM,) * 2, Image.LANCZOS)


def to_rgba(grid):
    """Premultiplied float grid -> a straight-alpha RGBA image at its own size."""
    img = Image.new("RGBA", (len(grid), len(grid)))
    img.putdata([
        (0, 0, 0, 0) if a <= 0 else
        (round(r / a * 255), round(g / a * 255), round(b / a * 255), round(a * 255))
        for row in grid for (r, g, b, a) in row
    ])
    return img


def export_frames(folder, size=128):
    """Writes <folder>/<look>-<arrow|ibeam>/NN.png: one transparent PNG per animation frame.

    Frames play at 30 fps; each folder is one seamless loop.
    """
    c = config.CURSOR_COLORS
    for name, shape, hotspot in (("arrow", ARROW, ARROW_HOTSPOT), ("ibeam", IBEAM, IBEAM_HOTSPOT)):
        base = draw_pointer(shape, hotspot, size, c)
        for look in LOOKS:
            color, motion = config.STARS[look]
            out = Path(folder) / f"{look}-{name}"
            out.mkdir(parents=True, exist_ok=True)
            for i in range(FRAMES):
                to_rgba(draw_frame(base, i, color, c["ink"], c["light"], motion)).save(out / f"{i:02}.png")
            print(f"wrote {out} ({FRAMES} frames, {size}px, 30 fps)")


def main(out, ibeam=False):
    c = config.CURSOR_COLORS
    shapes = [(ARROW, ARROW_HOTSPOT)] + ([(IBEAM, IBEAM_HOTSPOT)] if ibeam else [])
    bases = [draw_pointer(shape, hotspot, SIZE, c) for shape, hotspot in shapes]
    frames = []
    for i in range(FRAMES):
        sheet = Image.new("RGB", (CELL * len(LOOKS) * len(bases), CELL * len(GROUNDS)))
        for gi, ground in enumerate(GROUNDS):
            sheet.paste(ground, (0, gi * CELL, sheet.width, (gi + 1) * CELL))
            for li, look in enumerate(LOOKS):
                for bi, base in enumerate(bases):
                    color, motion = config.STARS[look]
                    img = to_image(draw_frame(base, i, color, c["ink"], c["light"], motion))
                    x = (li * len(bases) + bi) * CELL + (CELL - img.width) // 2
                    sheet.paste(img, (x, gi * CELL + (CELL - img.height) // 2), img)
        frames.append(sheet.quantize(64, dither=Image.Dither.NONE))  # fewer colours = smaller GIF
    frames[0].save(out, save_all=True, append_images=frames[1:], loop=0,
                   duration=round(FRAME_JIFFIES * 1000 / 60), optimize=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render the kopi-kopi cursors.")
    parser.add_argument("out", nargs="?", default="cursors.gif", help="GIF to write")
    parser.add_argument("--ibeam", action="store_true", help="include the text cursor in the GIF")
    parser.add_argument("--frames", metavar="FOLDER", help="export PNG frames instead of a GIF")
    args = parser.parse_args()
    if args.frames:
        export_frames(args.frames)
    else:
        main(args.out, args.ibeam)
