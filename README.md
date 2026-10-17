# kopi-kopi

**Copy and paste with taps.** Three-finger tap, tap where it starts, tap where it ends.
Three-finger tap again, and it's pasted.

![kopi-kopi cursors: yellow star = ready, pink heartbeat = selecting, green = copied](docs/cursors.gif)

## Why I built this

I copy a lot. Terminal logs into Claude Code, error messages, long pieces of documents.

My hand would be on the trackpad, but every copy pulled me back to the keyboard.
Ctrl+C, Ctrl+V, back to the trackpad, again and again.
And dragging across a long log on a trackpad is its own pain. The page scrolls away,
the selection slips, and I start over.

I wanted something simple. Tap where it starts, tap where it ends, tap to paste.
I couldn't find a tool that did just that, so I built one.

I'm not someone who writes every line of code from memory. What I have is the picture of
what I want and why. Claude has given me the ability to turn that picture into something that
actually works, and kopi-kopi is one of those: a small problem from my own day,
built in conversation with Claude Code, and tested on my own laptop until it felt right.

It's free and open source. It's small, it's useful, and since it touches your mouse and
clipboard, you should be able to read every line of it.

## How it works

```
three-finger tap   →  the cursor turns into a small galaxy
tap the start      →  scroll as far as you like  →  tap the end    copied
   …or just drag over the text                                    copied
three-finger tap   →  pasted where your pointer is
```

A revolving star tells you where you are:

| Star | Meaning |
|---|---|
| yellow, calm spin | ready: tap a start point, or drag |
| pink, spin **and heartbeat** | selecting: you're dragging, or the start point is placed |
| green, calm spin | copied: three-finger tap to paste |

- **Changed your mind?** Three-finger tap before copying cancels.
- **Tapped on nothing?** If nothing got copied, the star goes back to yellow and your old clipboard is never pasted by mistake.
- **Win+V still works.** kopi-kopi uses the normal clipboard, so Windows clipboard history keeps everything.

## Get started (Windows, 2 minutes)

**1. Make three-finger tap a middle click.**
Settings → Bluetooth & devices → Touchpad → Three-finger gestures → Taps → **Middle mouse button**.
Using a mouse? Clicking the scroll wheel already works, so skip this.

**2. Run kopi-kopi.**
Download `kopi-kopi.exe` from [Releases](https://github.com/sethumadhavan004/kopi-kopi/releases) and double-click it.
A small window opens. Minimise it and leave it running. Close it to quit.

> Windows may say *"Windows protected your PC"*. That's because the app isn't code-signed
> (signing costs money every year). Click **More info → Run anyway**, or run it from source below.

Prefer Python? (3.9 or newer)

```
pip install git+https://github.com/sethumadhavan004/kopi-kopi
kopi-kopi
```

**3. (Optional) Start it with Windows.**
Press Win+R, type `shell:startup`, and put a shortcut to `kopi-kopi.exe` in that folder.

## Is it safe?

- **It never reads what you copy.** To know whether a copy worked, it only looks at a counter
  Windows keeps of how many times the clipboard has changed. The contents are never touched.
- **No internet, no tracking, no data stored.** The only files it writes are its cursor images, in your temp folder.
- **It sees your clicks**, because that's how it works, and forgets them right away.
- **It's about 800 lines of Python, comments included.** You can read all of it, starting with [the architecture guide](docs/ARCHITECTURE.md).

## Troubleshooting

| Problem | Fix |
|---|---|
| Nothing happens on three-finger tap | Check step 1, then run `kopi-kopi --debug` to see every click it receives. |
| The galaxy cursor stays after quitting | Run `kopi-kopi --reset-cursor` (or `kopi-kopi.exe --reset-cursor`). |
| The first start is slow | It draws its animated cursors once (a few seconds) and caches them. Later starts are instant. |

## Under the hood

A small state machine decides what each tap means. A Windows mouse hook feeds it clicks, and
a worker thread sends the Ctrl+C and Ctrl+V. The cursors are drawn in code, with my
HIKARI design system's colours for the star, and played by
Windows itself, so there's no lag.

The [architecture guide](docs/ARCHITECTURE.md) walks through every piece, in the order to read them.

## Roadmap

- **v1.1:** macOS and Linux
- **v1.2:** a tray icon, and start-with-Windows as a setting
- **v2:** my own clipboard history, opened with a double three-finger tap

Ideas and bug reports are welcome in [Issues](https://github.com/sethumadhavan004/kopi-kopi/issues).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: `pip install -e ".[dev]"`, then `python -m pytest`.

## License

[MIT](LICENSE). Use it, change it, share it.

---

Made by Sethumadhavan N, with [Claude Code](https://claude.com/claude-code).
