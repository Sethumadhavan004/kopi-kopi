# How kopi-kopi works

A guided tour of the code, in the order that makes it easiest to understand.
Each section says which file to open and what to look for.

## The big picture

```
your finger
    │  three-finger tap = middle click, taps = left clicks
    ▼
Windows mouse hook ─────────── platforms/windows.py
    │  "left_down at (x, y)", "trigger_down", ...
    ▼
state machine ──────────────── core.py
    │  answers two questions:
    │    1. should the app under the pointer see this click?  (swallow it or not)
    │    2. what should happen?  (copy, paste, ...)
    ▼
worker thread ──────────────── app.py
       sends Shift+Click, Ctrl+C, Ctrl+V, checks the copy worked,
       and swaps the cursor
```

The files, in reading order:

| # | File | What it is |
|---|---|---|
| 1 | `kopi_kopi/core.py` | The brain: a state machine. No OS code at all. |
| 2 | `kopi_kopi/app.py` | The glue: two threads connecting the hook, the brain and the actions. |
| 3 | `kopi_kopi/platforms/windows.py` | Everything Windows-specific. |
| 4 | `kopi_kopi/cursor_art.py` | Draws the galaxy cursors and the star animation. |
| 5 | `kopi_kopi/config.py` | Colours and a few settings. |
| 6 | `kopi_kopi/cli.py` | The `kopi-kopi` command and its options. |

## 1. The state machine (`core.py`)

kopi-kopi is always in exactly one of four states:

```
         trigger               tap                    tap
  OFF ────────────▶ ARMED ───────────▶ HAS_START ───────────▶ COPIED
   ▲                  │                                        │
   │                  └──────────────── drag ─────────────────▶│
   │                                                           │
   └───────────────────────── trigger (paste) ◀────────────────┘

  A trigger in ARMED or HAS_START cancels back to OFF.
  If a copy turns out empty, COPIED falls back to ARMED.
```

Why a state machine? Each tap means something different depending on what happened before it.
Writing that as states and arrows keeps it small, readable and easy to test.

**Pure logic.** `core.py` never touches Windows. It takes events in (`trigger_down`, `left_down(x, y)`, ...)
and gives back a `Result`: swallow or not, plus a list of `Action`s. That's why `tests/test_core.py`
can test every arrow above on any computer, in milliseconds.

**The cursor follows the state.** The `look` property maps each state to a cursor
(`None` = your normal cursor). Because the cursor is *derived* from the state rather than
switched on and off separately, the two can never disagree. The one twist: holding the button
down while ARMED already counts as "selecting", so the heartbeat starts the moment a drag begins.

## 2. The glue (`app.py`)

**Two threads, on purpose.**

- The **hook thread** runs inside Windows' mouse handling. Windows waits for it before the click
  reaches any app, and it silently removes hooks that are too slow. So this thread only asks the
  state machine "swallow or not?" and queues any work. It never sleeps.
- The **worker thread** does the slow parts: waiting for an app to finish selecting, sending keys,
  checking the clipboard, swapping cursors.

They share the state machine, so a **lock** makes sure only one of them changes it at a time.

**Verifying a copy.** Windows keeps a counter that goes up every time the clipboard changes.
kopi-kopi notes it before copying and checks it after. If it didn't move, nothing was selected:
the state goes back to ARMED and the paste is skipped, so old clipboard content is never pasted
by surprise. The clipboard's *contents* are never read.

**Not sending Ctrl+C when the app already copied.** Some apps (Claude Code, some terminals) copy a
selection by themselves as soon as you finish dragging. After a drag, kopi-kopi waits a moment and
checks the counter first. If it already moved, it doesn't send Ctrl+C, because in a terminal, Ctrl+C
with nothing selected means "stop the running program".

## 3. The Windows layer (`platforms/windows.py`)

`platforms/__init__.py` lists the small set of functions every OS backend provides
(`start_listener`, `click`, `set_cursor`, `clipboard_seq`, ...). Supporting macOS or Linux
means writing one new file with the same functions; nothing else changes.

The interesting tricks, each with a comment in the code:

- **Low-level mouse hook.** Through the `pynput` library, kopi-kopi sees every click before any app does,
  and can *swallow* a click so the app never receives it.
- **Shift+Click for long selections.** Almost every app supports "click the start, Shift+Click the end".
  kopi-kopi lets your start tap through untouched, then swallows your end tap and replays it with
  Shift held. (Shift can't be added to a click that already reached the app, which is why it swallows
  first and replays.)
- **Recognising its own clicks.** The replayed clicks would reach the hook too. kopi-kopi sends them
  with Windows' `SendInput` and stamps them with a tag (`0x4B4F5049`, "KOPI" in ASCII). The hook
  ignores tagged events. (Windows' generic "injected" flag can't be used: touchpad drivers set it too,
  including on the three-finger-tap middle click. That was a real bug, found by testing.)
- **DPI awareness.** On laptops with 125% or 150% display scaling, Windows reports scaled coordinates
  to programs that don't declare themselves DPI-aware. kopi-kopi declares it, so clicks land where they should.
- **Swapping the system cursor.** `SetSystemCursor` replaces the arrow, text and hand cursors.
  `SystemParametersInfo(SPI_SETCURSORS)` puts your own cursors back. A console handler does the same
  if you close the window.

## 4. The cursor (`cursor_art.py`)

**Drawn with maths, not pixels.** Each shape (arrow, I-beam, star) is a polygon on a 32×32 grid.
For every pixel, the code computes the *signed distance* to the shape's edge: negative inside,
positive outside. One number per pixel gives you:

- the fill (distance below zero),
- outlines of any thickness (distance in a band),
- glows (fading with distance),
- smooth anti-aliased edges (blending over the last pixel),

at any size, so the cursor stays crisp on high-DPI screens.

**The galaxy.** The body colour depends on the distance from the hotspot: a bright core where you aim,
electric blue in the middle, deep indigo at the far end, with a magenta rim and a violet glow.
The star colours come from the HIKARI design system: Yuzu yellow, Sakura pink, Matcha green.

**The animation.** 48 frames at 30 fps. The star turns 90° per loop, and because it has four points,
the last frame lines up with the first. On top of the turn, `pulse()` scales it:

- `spin`: one slow breath per loop (waiting for you)
- `heartbeat`: a strong *lub*, a softer *dub*, then rest (a selection in progress)

Each beat is a smooth bump whose distance is measured *around the loop*, like a clock face
where 11:59 is next to 12:00, so there's no jump when the loop restarts.
`tests/test_cursor_art.py` checks that the frame after the last equals the first.

**Why there's no lag.** The frames are packed into an animated cursor file (`.ani`, a RIFF container
holding one `.cur` image per frame). Once Windows has it, *Windows* plays the animation.
kopi-kopi does no work per frame. The files are drawn once and cached in your temp folder,
in a folder named after a fingerprint of the art and colours, so changing either draws fresh cursors.

## 5. Tests

| Test file | What it proves | Runs on |
|---|---|---|
| `tests/test_core.py` | every state and arrow, including edge cases | any OS |
| `tests/test_app.py` | the whole app against a fake Windows (clicks, keys, clipboard counter) | any OS |
| `tests/test_cursor_art.py` | the `.ani` file structure, the seamless loop | any OS |
| `tools/windows_smoke.py` | real Windows loads every cursor; `SendInput` structures have the right size | Windows (CI) |

GitHub Actions (`.github/workflows/ci.yml`) runs all of this on Windows and Linux, with the oldest
and newest supported Python, on every push.

## A few words worth knowing

| Word | Meaning here |
|---|---|
| **hook** | a function Windows calls for every mouse event, before apps see it |
| **swallow / suppress** | tell Windows to drop an event so no app receives it |
| **state machine** | a fixed set of states plus rules for moving between them |
| **thread** | a separate line of work running at the same time as others |
| **lock** | makes threads take turns changing shared data |
| **signed distance** | how far a point is from a shape's edge; negative inside |
| **hotspot** | the exact pixel of the cursor that clicks (the arrow's tip) |
| **`.ani`** | the Windows animated cursor file format |
