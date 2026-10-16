"""Entry point: `python -m kopi_kopi` (or `python -m kopi_kopi --reset-cursor`)."""

import sys

if "--reset-cursor" in sys.argv:
    # Escape hatch if kopi-kopi was killed while the cursor was blue.
    from . import platforms
    platforms.load().cursor_off()
else:
    from .app import run
    run()
