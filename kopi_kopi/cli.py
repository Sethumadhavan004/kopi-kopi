"""Command line entry point: `kopi-kopi [--debug] [--reset-cursor] [--version]`."""

import argparse

from . import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="kopi-kopi",
        description="Copy and paste with taps. Three-finger tap (or wheel click) to start.",
    )
    parser.add_argument("--debug", action="store_true", help="print every click kopi-kopi sees")
    parser.add_argument("--reset-cursor", action="store_true",
                        help="restore the normal cursor and exit (if it ever gets stuck)")
    parser.add_argument("--self-test", action="store_true",
                        help="check this machine can run kopi-kopi, then exit")
    parser.add_argument("--version", action="version", version=f"kopi-kopi {__version__}")
    args = parser.parse_args(argv)

    if args.self_test:
        from . import platforms
        print(f"kopi-kopi {__version__} self-test ok: {platforms.load().self_test()}")
        return

    if args.reset_cursor:
        from . import platforms
        platforms.load().cursor_off()
        return

    from .app import run
    run(debug=args.debug)
