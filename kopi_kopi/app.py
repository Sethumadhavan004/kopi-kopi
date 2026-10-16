"""Wires the pieces together: OS hook -> core state machine -> action worker.

Two threads, on purpose:
  hook thread    decides "swallow or not" instantly (the OS drops slow hooks)
  worker thread  does the slow stuff: sleeping, sending keys, swapping cursors
They talk through a queue, so the hook never waits on the worker.
"""

import atexit
import platform
import queue
import threading
import time

from . import config, platforms
from .core import Action, KopiKopi, State


def run(debug=False):
    os_ = platforms.load()  # first, so an unsupported OS gets a clear message
    from importlib.metadata import version

    from pynput import keyboard, mouse

    print(f"kopi-kopi: Python {platform.python_version()}, pynput {version('pynput')}")

    kopi = KopiKopi(config.DRAG_THRESHOLD_PX)
    jobs = queue.Queue()
    keys = keyboard.Controller()
    pointer = mouse.Controller()
    press_seq = [0]  # clipboard counter when the current press started

    def tap(key):
        with keys.pressed(os_.MODIFIER):
            keys.tap(key)

    def do(action, seq_at_press):
        if action == Action.CURSOR_ON:
            os_.cursor_on()
        elif action == Action.CURSOR_OFF:
            os_.cursor_off()
        elif action == Action.COPY_AFTER_DRAG:
            time.sleep(config.AUTO_COPY_WAIT_S)
            if os_.clipboard_seq() == seq_at_press:  # the app didn't copy it by itself
                tap("c")
        elif action == Action.SHIFT_CLICK_COPY:
            with keys.pressed(keyboard.Key.shift):
                pointer.click(mouse.Button.left)
            time.sleep(0.05)  # let the app finish selecting before we copy
            tap("c")
        elif action == Action.PASTE:
            if config.CLICK_BEFORE_PASTE:
                pointer.click(mouse.Button.left)
                time.sleep(0.05)
            tap("v")

    def worker():
        while True:
            action, seq = jobs.get()
            try:
                do(action, seq)
            except Exception as e:  # one failed action shouldn't kill the tool
                print(f"kopi-kopi: {action.name} failed: {e}")

    def handle(event, x, y):
        # Runs on the hook thread: keep it fast, no sleeping, no I/O.
        if event == "left_down" and kopi.state != State.OFF:
            press_seq[0] = os_.clipboard_seq()
        if event in ("left_down", "left_up"):
            result = getattr(kopi, event)(x, y)
        else:
            result = getattr(kopi, event)()
        for action in result.actions:
            jobs.put((action, press_seq[0]))
        if debug:
            names = [a.name for a in result.actions]
            print(f"  {event:<12} ({x},{y})  -> {kopi.state.name:<9} swallow={result.suppress} {names}")
        return result.suppress

    atexit.register(os_.cursor_off)  # never leave the user stuck with a blue cursor
    threading.Thread(target=worker, daemon=True).start()
    listener = os_.start_listener(handle)
    print("kopi-kopi is running. Three-finger tap (or middle click) to start. Ctrl+C here to quit.")
    try:
        while listener.is_alive():
            listener.join(0.5)  # short waits so Ctrl+C can get through on Windows
        # The listener thread ended on its own: join() re-raises whatever killed it,
        # so the error is shown instead of the program quietly exiting.
        listener.join()
        print("kopi-kopi: the mouse listener stopped unexpectedly.")
    except KeyboardInterrupt:
        pass
