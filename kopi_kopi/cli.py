"""Command line entry point: `kopi-kopi [--debug] [--reset-cursor] [--version]`."""

import argparse

from . import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="kopi-kopi",
        description="Copy and paste with taps. Three-finger tap (or middle click) to start.",
    )
    parser.add_argument("--debug", action="store_true", help="print every click kopi-kopi sees")
    parser.add_argument("--reset-cursor", action="store_true",
                        help="restore the normal cursor and exit (if it ever gets stuck)")
    parser.add_argument("--version", action="version", version=f"kopi-kopi {__version__}")
    args = parser.parse_args(argv)

    if args.reset_cursor:
        from . import platforms
        platforms.load().cursor_off()
        return

    from .app import run
    run(debug=args.debug)
