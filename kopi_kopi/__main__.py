"""Entry point: `python -m kopi_kopi`, with `--debug` to print every click,
or `--reset-cursor` to restore the normal cursor."""

import sys

if "--reset-cursor" in sys.argv:
    # Escape hatch if kopi-kopi was killed while the cursor was blue.
    from . import platforms
    platforms.load().cursor_off()
else:
    from .app import run
    run(debug="--debug" in sys.argv)
