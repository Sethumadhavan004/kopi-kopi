# Changelog

All notable changes to kopi-kopi. The format follows [Keep a Changelog](https://keepachangelog.com),
and versions follow [Semantic Versioning](https://semver.org).

## [1.0.0] - 2026-10-19

The first release, for Windows. Install with `pip install kopi-kopi`, or download the Windows app.

### Added
- Three-finger tap on a trackpad, or wheel click on a mouse, turns kopi-kopi on; tap the start and end, or drag, to copy;
  the same tap or click again pastes where the pointer is.
- Long selections across pages: the end tap is replayed as Shift+Click.
- Copies are verified with the clipboard change counter; an empty copy goes back to "ready"
  and never pastes old clipboard content.
- Skips Ctrl+C when the app already copied a drag by itself (Claude Code, some terminals).
- Animated galaxy cursors with a revolving star: yellow (ready), pink with a heartbeat (selecting),
  green (copied). Star colours from the HIKARI design system. Played by Windows, so no lag.
- `kopi-kopi --debug` to print every click, `--reset-cursor` to restore the normal cursor,
  `--self-test` to check a machine can run it, `--version`.
- The normal cursor comes back when the window is closed.
- Tests for the state machine, the app (against a fake OS) and the cursor files; CI on Windows and Linux;
  a release workflow that tests the built app, then publishes it to GitHub Releases and PyPI.
