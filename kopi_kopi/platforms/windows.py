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

# Our own synthetic clicks carry this tag, so the hook can recognise and ignore them.
# (Windows' "injected" flag isn't enough: touchpad drivers inject events too,
# including the middle click made by a three-finger tap.)
KOPI_TAG = 0x4B4F5049  # "KOPI" in ASCII

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


def start_listener(handle, debug=False):
    """Install the mouse hook. `handle(event, x, y)` returns True to swallow the event.

    Windows calls the filter on its own thread *before* the event reaches any app,
    and removes hooks that are slow, so `handle` must return quickly.
    """
    listener = None

    def win32_event_filter(msg, data):
        event = EVENTS.get(msg)
        if event is None or data.dwExtraInfo == KOPI_TAG:
            return True  # not ours to judge (moves, scrolls, our own synthetic clicks)
        if debug:
            print(f"  raw {event:<12} flags={data.flags:#x} extra={data.dwExtraInfo}")
        if handle(event, data.pt.x, data.pt.y):
            listener.suppress_event()  # raises internally; the app never sees this event
        return True

    listener = mouse.Listener(win32_event_filter=win32_event_filter)
    listener.start()
    return listener


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class _INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_SHIFT = 0x10


def _mouse(flags):
    return _INPUT(type=INPUT_MOUSE, mi=_MOUSEINPUT(dwFlags=flags, dwExtraInfo=KOPI_TAG))


def _key(vk, up=False):
    return _INPUT(type=INPUT_KEYBOARD,
                  ki=_KEYBDINPUT(wVk=vk, dwFlags=KEYEVENTF_KEYUP if up else 0, dwExtraInfo=KOPI_TAG))


def click(shift=False):
    """Left click at the pointer, optionally with Shift held, as one atomic batch."""
    inputs = [_mouse(MOUSEEVENTF_LEFTDOWN), _mouse(MOUSEEVENTF_LEFTUP)]
    if shift:
        inputs = [_key(VK_SHIFT)] + inputs + [_key(VK_SHIFT, up=True)]
    batch = (_INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), batch, ctypes.sizeof(_INPUT))


def _cursor_size():
    return round((user32.GetSystemMetrics(SM_CXCURSOR) or 32) * config.CURSOR_SCALE)


def _cursor_file(look, name, art, hotspot, size):
    pixels, hs = render(art, hotspot, config.KOPI_BLUE, config.OUTLINE, size,
                        badge=None if look == "armed" else look)
    path = os.path.join(tempfile.gettempdir(), f"kopi-kopi-{look}-{name}-{size}.cur")
    with open(path, "wb") as f:
        f.write(to_cur_bytes(pixels, hs))
    return path


_files = {}  # (look, size) -> (arrow .cur path, I-beam .cur path)


def prepare_cursors():
    """Draw every cursor up front (about a second), so the first tap isn't laggy."""
    size = _cursor_size()
    for look in ("armed", "start", "copied"):
        if (look, size) not in _files:
            _files[look, size] = (
                _cursor_file(look, "arrow", ARROW, ARROW_HOTSPOT, size),
                _cursor_file(look, "ibeam", IBEAM, IBEAM_HOTSPOT, size),
            )


def set_cursor(look):
    """Show the kopi-kopi cursor for `look` ("armed", "start", "copied"), or None for normal."""
    if look is None:
        cursor_off()
        return
    prepare_cursors()
    arrow, ibeam = _files[look, _cursor_size()]
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
