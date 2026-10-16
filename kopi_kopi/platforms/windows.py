"""Windows backend: a low-level mouse hook, system cursor swap, clipboard counter."""

import ctypes
import os
import tempfile
from ctypes import wintypes

from pynput import keyboard, mouse

from .. import config
from ..cursor_art import ARROW, ARROW_HOTSPOT, IBEAM, IBEAM_HOTSPOT, render, to_cur_bytes

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.LoadImageW.restype = wintypes.HANDLE
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                              ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.SetSystemCursor.argtypes = [wintypes.HANDLE, wintypes.DWORD]
user32.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT,
                                         ctypes.c_void_p, wintypes.UINT]

MODIFIER = keyboard.Key.ctrl

WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0201, 0x0202
WM_MBUTTONDOWN, WM_MBUTTONUP = 0x0207, 0x0208
LLMHF_INJECTED = 0x01  # set on events made by programs (including us), not by your hand

EVENTS = {
    WM_LBUTTONDOWN: "left_down",
    WM_LBUTTONUP: "left_up",
    WM_MBUTTONDOWN: "trigger_down",
    WM_MBUTTONUP: "trigger_up",
}

IMAGE_CURSOR, LR_LOADFROMFILE = 2, 0x10
OCR_NORMAL, OCR_IBEAM, OCR_HAND = 32512, 32513, 32649
SPI_SETCURSORS = 0x57
SM_CXCURSOR = 13


def _dpi_aware():
    # Without this, on a laptop with 125%/150% scaling Windows "lies" about
    # coordinates and cursor sizes, and our clicks would land in the wrong place.
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor aware
    except (AttributeError, OSError):
        ctypes.windll.user32.SetProcessDPIAware()


_dpi_aware()


def start_listener(handle):
    """Install the mouse hook. `handle(event, x, y)` returns True to swallow the event.

    Windows calls the filter on its own thread *before* the event reaches any app,
    and removes hooks that are slow, so `handle` must return quickly.
    """
    listener = None

    def win32_event_filter(msg, data):
        event = EVENTS.get(msg)
        if event is None or data.flags & LLMHF_INJECTED:
            return True  # not ours to judge (moves, scrolls, our own synthetic clicks)
        if handle(event, data.pt.x, data.pt.y):
            listener.suppress_event()  # raises internally; the app never sees this event
        return True

    listener = mouse.Listener(win32_event_filter=win32_event_filter)
    listener.start()
    return listener


def _cursor_file(name, art, hotspot, size):
    pixels, hs = render(art, hotspot, config.KOPI_BLUE, config.OUTLINE, size)
    path = os.path.join(tempfile.gettempdir(), f"kopi-kopi-{name}-{size}.cur")
    with open(path, "wb") as f:
        f.write(to_cur_bytes(pixels, hs))
    return path


_files = {}


def cursor_on():
    size = user32.GetSystemMetrics(SM_CXCURSOR) or 32
    if size not in _files:
        _files[size] = (
            _cursor_file("arrow", ARROW, ARROW_HOTSPOT, size),
            _cursor_file("ibeam", IBEAM, IBEAM_HOTSPOT, size),
        )
    arrow, ibeam = _files[size]
    # SetSystemCursor takes ownership of (and later destroys) the handle,
    # so each system cursor slot needs its own freshly loaded copy.
    for path, slot in ((arrow, OCR_NORMAL), (ibeam, OCR_IBEAM), (arrow, OCR_HAND)):
        handle = user32.LoadImageW(None, path, IMAGE_CURSOR, 0, 0, LR_LOADFROMFILE)
        if handle:
            user32.SetSystemCursor(handle, slot)


def cursor_off():
    # Reloads the user's normal cursor scheme from Windows settings.
    user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, 0)


def clipboard_seq():
    return user32.GetClipboardSequenceNumber()
