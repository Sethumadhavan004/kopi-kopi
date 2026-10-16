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

    from pynput import keyboard

    print(f"kopi-kopi: Python {platform.python_version()}, pynput {version('pynput')}")

    kopi = KopiKopi(config.DRAG_THRESHOLD_PX)
    lock = threading.Lock()  # the hook thread and the worker both touch `kopi`
    jobs = queue.Queue()     # functions for the worker to run, in order
    keys = keyboard.Controller()
    press_seq = [0]          # clipboard counter when the current press started
    shown = [None]           # which cursor look is on screen
    copy_ok = [True]         # did the last copy put something new on the clipboard?

    def sync_cursor():
        # Call with `lock` held. Queues a cursor change only when the look changes.
        look = kopi.look
        if look != shown[0]:
            shown[0] = look
            jobs.put(lambda: os_.set_cursor(look))

    def tap(key):
        with keys.pressed(os_.MODIFIER):
            keys.tap(key)

    def copy(seq_before, send_ctrl_c=True):
        if send_ctrl_c:
            tap("c")
            time.sleep(0.15)  # give the app a moment to fill the clipboard
        copy_ok[0] = os_.clipboard_seq() != seq_before
        if not copy_ok[0]:
            # Nothing was selected, so the clipboard still holds the old stuff
            # (maybe a screenshot!). Don't paste that; go back and let you retry.
            print("kopi-kopi: nothing got copied, tap the start point again.")
            with lock:
                kopi.copy_failed()
                sync_cursor()

    def do(action, seq_at_press):
        if action == Action.COPY_AFTER_DRAG:
            time.sleep(config.AUTO_COPY_WAIT_S)
            # If the app already copied the drag by itself (Claude Code does), don't
            # send Ctrl+C: in a terminal with nothing selected it means "stop".
            copy(seq_at_press, send_ctrl_c=os_.clipboard_seq() == seq_at_press)
        elif action == Action.SHIFT_CLICK_COPY:
            before = os_.clipboard_seq()
            os_.click(shift=True)
            time.sleep(0.05)  # let the app finish selecting before we copy
            copy(before)
        elif action == Action.PASTE:
            if not copy_ok[0]:
                return
            if config.CLICK_BEFORE_PASTE:
                os_.click()
                time.sleep(0.05)
            tap("v")

    def worker():
        while True:
            job = jobs.get()
            try:
                job()
            except Exception as e:  # one failed action shouldn't kill the tool
                print(f"kopi-kopi: {e!r}")

    def handle(event, x, y):
        # Runs on the hook thread: keep it fast, no sleeping, no I/O.
        with lock:
            if event == "left_down" and kopi.state != State.OFF:
                press_seq[0] = os_.clipboard_seq()
            if event in ("left_down", "left_up"):
                result = getattr(kopi, event)(x, y)
            else:
                result = getattr(kopi, event)()
            for action in result.actions:
                jobs.put(lambda a=action, seq=press_seq[0]: do(a, seq))
            sync_cursor()
        if debug:
            names = [a.name for a in result.actions]
            print(f"  {event:<12} ({x},{y})  -> {kopi.state.name:<9} swallow={result.suppress} {names}")
        return result.suppress

    atexit.register(os_.cursor_off)  # never leave the user stuck with a blue cursor
    threading.Thread(target=worker, daemon=True).start()

    def prepare():
        started = time.time()
        os_.prepare_cursors()
        if time.time() - started > 1:
            print("kopi-kopi: cursors drawn and cached, next start is instant.")

    jobs.put(prepare)
    listener = os_.start_listener(handle, debug)
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
