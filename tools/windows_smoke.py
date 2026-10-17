"""Checks the Windows layer on a real Windows machine (used by CI).

Draws every cursor, asks Windows to load each .ani file, and checks the
SendInput structure size, without changing the cursor or clicking anything.
"""

import ctypes
import sys
from ctypes import wintypes

from kopi_kopi.platforms import windows

windows.user32.DestroyCursor.argtypes = [wintypes.HANDLE]  # 64-bit handles

windows.prepare_cursors()
paths = [p for pair in windows._files.values() for p in pair]
assert len(paths) == 6, paths
for path in paths:
    handle = windows.user32.LoadCursorFromFileW(path)
    assert handle, f"Windows refused to load {path}"
    windows.user32.DestroyCursor(handle)

expected = 40 if sys.maxsize > 2**32 else 28
assert ctypes.sizeof(windows._INPUT) == expected, ctypes.sizeof(windows._INPUT)
print(f"ok: {len(paths)} animated cursors load; INPUT is {expected} bytes")
