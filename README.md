# kopi-kopi

**Copy and paste with the three finger tap in your trackpad** Three finger tap, tap where it starts, tap where it ends, dragging works the same way, three finger at the destination, and its pasted there.

**Copy and paste with the middle click / wheel click in your mouse** Wheel Click, tap where it starts, tap where it ends, dragging works the same way, wheel click at the destination, and its pasted there.

![kopi-kopi cursors: yellow star = ready, pink heartbeat = selecting, green = copied](https://raw.githubusercontent.com/Sethumadhavan004/kopi-kopi/main/docs/cursors.gif)

## Why I built this

We all copy and paste a lot nowadays. And the copy-paste is by used because it is an improvement over the manual typing. But I felt, the actions that we have to do, to complete this process was something that i felt we can optimize. 

I have heard how core developers are so terminal oriented, they don't use much of the mouse / trackpad. Well I have to say sorry to them, cause this tool is fully mouse/trackpad oriented.

With actions mapped as trigger, this tool, kopi-kopi, allows one to easily go into kopi mode, select the text and paste them, without the need to touch the keyboard. The trigger, three-finger tap in the trackpad and wheel click in mouse, brings in a ease to use this feature, that I am sure will become part of one's routine.

This tool is being released as open source project, so many of them can use and get benefitted by this. No data is being collected and it is fully offline tool with no dependency.

Even though it is mainly built as a personal tool for my particular pain point, I believe many others could be benefitted through this as well.

## How it works

```
three-finger tap / wheel click   →  the cursor turns into a small galaxy
tap the start      →  scroll as far as you like  →  tap the end    copied
   …or just drag over the text                                    copied
three-finger tap / wheel click   →  pasted where your pointer is
```

A revolving star tells you where you are:

| Star | Meaning |
|---|---|
| yellow, calm spin | ready: tap a start point, or drag |
| pink, spin **and heartbeat** | selecting: you're dragging, or the start point is placed |
| green, calm spin | copied: three-finger tap or wheel click to paste |

- **Changed your mind?** Three-finger tap or wheel click before copying cancels.
- **Tapped on nothing?** If nothing got copied, the star goes back to yellow and your old clipboard is never pasted by mistake.
- **Win+V still works.** kopi-kopi uses the normal clipboard, so Windows clipboard history keeps everything.

## Get started (Windows, 2 minutes)

**1. Trackpad: make three-finger tap a middle click.**
Settings → Bluetooth & devices → Touchpad → Three-finger gestures → Taps → **Middle mouse button**.
Using a mouse? The wheel click already works, so skip this.

**2. Install and run kopi-kopi**, whichever way suits you.

**With Python** (3.9 or newer):

```
pip install kopi-kopi
kopi-kopi
```

**Or the Windows app:** download `kopi-kopi-windows.zip` from [Releases](https://github.com/Sethumadhavan004/kopi-kopi/releases),
unzip it, and double-click `kopi-kopi.exe` inside the folder.

> The app isn't code-signed yet, so Windows may say *"Windows protected your PC"*:
> click **More info → Run anyway**. If your browser blocks the download, use the Python install above.

A small window opens. Minimise it and leave it running. Close it to quit.

**3. (Optional) Start it with Windows.**
Press Win+R, type `shell:startup`, and put a shortcut to `kopi-kopi.exe` in that folder.

## Is it safe?

- **It never reads what you copy.** To know whether a copy worked, it only looks at a counter
  Windows keeps of how many times the clipboard has changed. The contents are never touched.
- **No internet, no tracking, no data stored.** The only files it writes are its cursor images, in your temp folder.
- **It sees your clicks**, because that's how it works, and forgets them right away.
- **It's about 800 lines of Python, comments included.** You can read all of it, starting with [the architecture guide](https://github.com/Sethumadhavan004/kopi-kopi/blob/main/docs/ARCHITECTURE.md).

## Troubleshooting

| Problem | Fix |
|---|---|
| Nothing happens on three-finger tap | Check step 1, then run `kopi-kopi --debug` to see every click it receives. |
| The browser blocks the download | The app isn't code-signed yet, so new versions get flagged. Install with `pip install kopi-kopi` instead. |
| Something seems off on your PC | `kopi-kopi --self-test` checks that everything kopi-kopi needs works on your machine. |
| The galaxy cursor stays after quitting | Run `kopi-kopi --reset-cursor` (or `kopi-kopi.exe --reset-cursor`). |
| The first start is slow | It draws its animated cursors once (a few seconds) and caches them. Later starts are instant. |

## Under the hood

A small state machine decides what each tap means. A Windows mouse hook feeds it clicks, and
a worker thread sends the Ctrl+C and Ctrl+V. The cursors are drawn in code, with my
HIKARI design system's colours for the star, and played by
Windows itself, so there's no lag.

The [architecture guide](https://github.com/Sethumadhavan004/kopi-kopi/blob/main/docs/ARCHITECTURE.md) walks through every piece, in the order to read them.

## Roadmap

- **v1.1:** macOS and Linux
- **v1.2:** a tray icon, and start-with-Windows as a setting
- **v2:** my own clipboard history, opened with a double three-finger tap

Ideas and bug reports are welcome in [Issues](https://github.com/Sethumadhavan004/kopi-kopi/issues).

## Contributing

See [CONTRIBUTING.md](https://github.com/Sethumadhavan004/kopi-kopi/blob/main/CONTRIBUTING.md). In short: `pip install -e ".[dev]"`, then `python -m pytest`.

## License

[MIT](https://github.com/Sethumadhavan004/kopi-kopi/blob/main/LICENSE). Use it, change it, share it.

---

Made by Sethumadhavan N, with [Claude Code](https://claude.com/claude-code).
