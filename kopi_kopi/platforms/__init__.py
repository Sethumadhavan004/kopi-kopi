"""Picks the backend for the current OS.

Each backend provides the same few things, so app.py never needs to know the OS:
  start_listener(handle)  hook the mouse; handle(event, x, y) -> True to swallow it
  cursor_on() / cursor_off()
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
