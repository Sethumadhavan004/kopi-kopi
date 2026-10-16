"""The brain of kopi-kopi: a small state machine with no OS code in it.

The platform layer feeds it raw mouse events and gets back two answers:
  1. should this event be swallowed (hidden from the app under the pointer)?
  2. which actions should run (change cursor, copy, paste, ...)?

Keeping it pure means it can be unit-tested on any machine, and every OS
backend (Windows today, macOS/Linux next) shares exactly the same behaviour.

    OFF --trigger--> ARMED --tap--> HAS_START --tap--> COPIED --trigger--> OFF
                       |                                  ^      (paste)
                       +-------------drag-----------------+

A trigger while ARMED or HAS_START cancels back to OFF.
If a copy turns out to have copied nothing, COPIED falls back to ARMED.
The cursor is a pure function of the state (see `look`), so it can never disagree with it.
"""

from dataclasses import dataclass, field
from enum import Enum, auto


class State(Enum):
    OFF = auto()        # normal computer, nothing intercepted
    ARMED = auto()      # blue cursor, waiting for a start tap or a drag
    HAS_START = auto()  # start point placed, waiting for the end tap
    COPIED = auto()     # text is on the clipboard, waiting for the paste trigger


class Action(Enum):
    COPY_AFTER_DRAG = auto()  # copy, unless the app already auto-copied the drag
    SHIFT_CLICK_COPY = auto() # shift+click at the pointer (extends selection), then copy
    PASTE = auto()            # (optionally click, then) paste


LOOKS = {
    State.OFF: None,
    State.ARMED: "armed",
    State.HAS_START: "start",   # ring badge: waiting for the end point
    State.COPIED: "copied",     # tick badge: ready to paste
}


@dataclass
class Result:
    suppress: bool = False
    actions: list = field(default_factory=list)


class KopiKopi:
    def __init__(self, drag_threshold_px):
        self.state = State.OFF
        self.drag_threshold_px = drag_threshold_px
        self._down_at = None          # where the current left press started
        self._left_suppressed = False # did we swallow the current left press?

    @property
    def look(self):
        """Which cursor to show: None means the normal system cursor."""
        return LOOKS[self.state]

    def copy_failed(self):
        """The clipboard didn't change: nothing was selected. Go back and let you retry."""
        if self.state == State.COPIED:
            self.state = State.ARMED

    # --- trigger (middle click / three-finger tap) -------------------------

    def trigger_down(self):
        # The trigger is always swallowed so apps never see a middle click
        # (browsers would open links in new tabs, Linux would paste, ...).
        # A press already in progress belongs to the old mode, so forget where it started.
        self._down_at = None
        if self.state == State.OFF:
            self.state = State.ARMED
            return Result(True)
        if self.state == State.COPIED:
            self.state = State.OFF
            return Result(True, [Action.PASTE])
        # ARMED or HAS_START: changed your mind, cancel.
        self.state = State.OFF
        return Result(True)

    def trigger_up(self):
        # Swallow the release too, otherwise apps get a release with no press.
        return Result(True)

    # --- left button --------------------------------------------------------

    def left_down(self, x, y):
        self._down_at = (x, y)
        # Only the END tap is swallowed: we replay it ourselves with Shift held,
        # because Shift can't be added to a click that already reached the app.
        self._left_suppressed = self.state == State.HAS_START
        return Result(self._left_suppressed)

    def left_up(self, x, y):
        # A release is swallowed exactly when its press was, so apps never
        # see half a click (that would leave a button "stuck down").
        suppressed = self._left_suppressed
        self._left_suppressed = False
        start = self._down_at
        self._down_at = None

        if self.state == State.ARMED and start is not None:
            if self._moved(start, (x, y)):
                self.state = State.COPIED
                return Result(suppressed, [Action.COPY_AFTER_DRAG])
            self.state = State.HAS_START  # plain tap went through: caret is at the start
            return Result(suppressed)

        if self.state == State.HAS_START and suppressed:
            self.state = State.COPIED
            return Result(True, [Action.SHIFT_CLICK_COPY])

        return Result(suppressed)

    def _moved(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) > self.drag_threshold_px
