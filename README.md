# kopi-kopi

Copy and paste with taps instead of keyboard shortcuts.
Made for copying long terminal logs into Claude Code without wrestling with your trackpad.

```
three-finger tap  →  cursor turns blue
tap start         →  scroll as far as you like  →  tap end      (copied)
   …or just drag over the text                                  (copied)
three-finger tap  →  pasted where your pointer is, cursor back to normal
```

Three-finger tap again before copying cancels.
Everything goes through the normal clipboard, so **Win+V** clipboard history keeps working.

## Setup (Windows)

1. **Make three-finger tap a middle click:**
   Settings → Bluetooth & devices → Touchpad → Three-finger gestures → Taps → **Middle mouse button**.
   (On a mouse, the wheel click already is one.)
2. Install and run (Python 3.9+):
   ```
   pip install -r requirements.txt
   python -m kopi_kopi
   ```
3. Quit with Ctrl+C in that window. If the cursor ever stays blue: `python -m kopi_kopi --reset-cursor`.

macOS and Linux: coming next. The core logic is already OS-independent.

## How it works

| File | Job |
|---|---|
| `kopi_kopi/core.py` | The state machine: OFF → ARMED → HAS_START → COPIED → OFF. Pure logic, unit tested. |
| `kopi_kopi/platforms/windows.py` | Low-level mouse hook, blue system cursor, clipboard change counter. |
| `kopi_kopi/app.py` | Glue: hook thread decides instantly, worker thread does the slow work. |
| `kopi_kopi/cursor_art.py` | Draws the blue cursor from ASCII art and writes a `.cur` file. |
| `kopi_kopi/config.py` | Colour, drag threshold and a few other knobs. |

Ideas behind it:

- **Selecting long ranges uses Shift+Click**, which almost every app supports: click the start, Shift+Click the end.
  kopi-kopi lets your start tap through untouched, then *swallows* your end tap and replays it with Shift held.
- **The trigger is always swallowed**, so apps never see a stray middle click.
- **Drags aren't touched at all.** The app selects as usual, and kopi-kopi copies when you let go.
  If the app already copied on its own (Claude Code does), kopi-kopi skips Ctrl+C, because in a terminal
  Ctrl+C with nothing selected means "stop the program".
- **Our own synthetic clicks are ignored** by the hook (Windows marks them as "injected"), so kopi-kopi never reacts to itself.

## Tests

```
pip install pytest
python -m pytest
```

## Roadmap

- v0.2: macOS and Linux backends, "Copied!" toast, tray icon, start with Windows
- v1.x: double three-finger tap opens a kopi-kopi clipboard history
