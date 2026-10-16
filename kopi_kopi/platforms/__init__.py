"""Picks the backend for the current OS.

Each backend provides the same few things, so app.py never needs to know the OS:
  start_listener(handle)  hook the mouse; handle(event, x, y) -> True to swallow it
  click(shift=False)      left click at the pointer, ignored by our own hook
  prepare_cursors()       draw the cursors ahead of time
  set_cursor(look)        show the cursor for a look ("armed", "selecting", "copied") or None
  cursor_off()            restore the normal cursor
  clipboard_seq()         a number that changes whenever the clipboard changes
  MODIFIER                the copy/paste key (Ctrl on Windows/Linux, Cmd on macOS)
"""

import sys


def load():
    if sys.platform == "win32":
        from . import windows
        return windows
    raise SystemExit(
        f"kopi-kopi doesn't support {sys.platform} yet (Windows first, macOS and Linux next)."
    )
