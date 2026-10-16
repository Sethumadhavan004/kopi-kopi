"""Runs app.py end to end against a fake OS, so the glue is tested without Windows."""

import contextlib
import sys
import threading
import time
import types

from kopi_kopi import app, platforms


class FakeOS:
    MODIFIER = "ctrl"

    def __init__(self, script, selection):
        self.script = script        # list of (event, x, y) to feed the hook
        self.selection = selection  # is text selected when Ctrl+C arrives?
        self.seq = 0                # the clipboard change counter
        self.cursors = []
        self.sent = []

    def start_listener(self, handle, debug=False):
        for event, x, y in self.script:
            handle(event, x, y)
            time.sleep(0.4)  # let the worker finish this step's actions
        return types.SimpleNamespace(is_alive=lambda: False, join=lambda *a: None)

    def prepare_cursors(self):
        pass

    def set_cursor(self, look):
        self.cursors.append(look)

    def cursor_off(self):
        pass

    def clipboard_seq(self):
        return self.seq

    def click(self, shift=False):
        self.sent.append("shift+click" if shift else "click")

    def key(self, k):
        self.sent.append(f"ctrl+{k}")
        if k == "c" and self.selection:
            self.seq += 1


def run_with(monkeypatch, fake):
    keyboard = types.SimpleNamespace(Controller=lambda: types.SimpleNamespace(
        pressed=lambda *_: contextlib.nullcontext(), tap=fake.key))
    monkeypatch.setitem(sys.modules, "pynput", types.SimpleNamespace(keyboard=keyboard))
    monkeypatch.setattr(platforms, "load", lambda: fake)
    import importlib.metadata
    monkeypatch.setattr(importlib.metadata, "version", lambda _: "test")
    t = threading.Thread(target=app.run)
    t.start()
    t.join(10)


DRAG_THEN_PASTE = [
    ("trigger_down", 0, 0), ("trigger_up", 0, 0),
    ("left_down", 10, 10), ("left_up", 200, 10),
    ("trigger_down", 50, 50), ("trigger_up", 50, 50),
]


def test_drag_copies_then_paste(monkeypatch):
    fake = FakeOS(DRAG_THEN_PASTE, selection=True)
    run_with(monkeypatch, fake)
    assert fake.sent == ["ctrl+c", "click", "ctrl+v"]
    assert fake.cursors == ["armed", "copied", None]


def test_copying_nothing_never_pastes_the_old_clipboard(monkeypatch):
    fake = FakeOS(DRAG_THEN_PASTE[:4], selection=False)
    run_with(monkeypatch, fake)
    assert fake.sent == ["ctrl+c"]                         # tried to copy, nothing changed
    assert fake.cursors == ["armed", "copied", "armed"]    # back to "pick a start point"


def test_tap_tap_uses_shift_click(monkeypatch):
    script = [("trigger_down", 0, 0), ("trigger_up", 0, 0),
              ("left_down", 5, 5), ("left_up", 5, 5),
              ("left_down", 300, 900), ("left_up", 300, 900)]
    fake = FakeOS(script, selection=True)
    run_with(monkeypatch, fake)
    assert fake.sent == ["shift+click", "ctrl+c"]
    assert fake.cursors == ["armed", "start", "copied"]
