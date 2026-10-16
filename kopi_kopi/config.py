"""Settings you might want to tweak. Everything else reads from here."""

# Colours from the HIKARI design system (Sethumadhavan N).
HIKARI_INK = (0x2B, 0x12, 0x15)     # warm near-black
HIKARI_PINK = (0xF6, 0xB9, 0xC4)    # Sakura, "the companion"
HIKARI_YELLOW = (0xF9, 0xE7, 0x9F)  # Yuzu, "the spark"
HIKARI_GREEN = (0xBF, 0xE6, 0xCB)   # Matcha, "the calm"
WHITE = (0xFF, 0xFF, 0xFF)

# Galaxy colours for the pointer: a bright core fading to blue arms and a magenta ring.
GALAXY_CORE = (0xDC, 0xE6, 0xFF)    # white-blue, the bright centre
GALAXY_BLUE = (0x46, 0x6E, 0xFF)    # electric blue
GALAXY_INDIGO = (0x26, 0x1C, 0x7A)  # deep space
GALAXY_MAGENTA = (0xEC, 0x52, 0xD6) # the neon outer ring
GALAXY_VIOLET = (0xAA, 0x5A, 0xFF)  # the soft nebula glow

# The pointer: a galaxy gradient from tip to tail, a magenta rim and a violet glow.
CURSOR_COLORS = {
    "core": GALAXY_CORE,     # at the tip
    "body": GALAXY_BLUE,     # the middle
    "deep": GALAXY_INDIGO,   # at the tail
    "rim": GALAXY_MAGENTA,
    "glow": GALAXY_VIOLET,
    "ink": GALAXY_INDIGO,    # outline around the star, so pastels show on white pages
    "light": WHITE,          # the star's bright core
}

# The revolving star's colour and motion tell you which step you're on.
# Motion: "spin" = waiting for you, "heartbeat" = a selection is in progress.
STARS = {
    "armed": (HIKARI_YELLOW, "spin"),          # ready: tap a start point or drag
    "selecting": (HIKARI_PINK, "heartbeat"),   # dragging, or start placed: tap the end point
    "copied": (HIKARI_GREEN, "spin"),          # copied: three-finger tap to paste
}

# kopi-kopi cursor size relative to your normal cursor. Bigger = easier to notice.
CURSOR_SCALE = 1.5

# If the pointer moves more than this many pixels between press and release,
# it counts as a drag (select-by-dragging) instead of a tap (mark a point).
DRAG_THRESHOLD_PX = 6

# On paste, click at the pointer first so the text lands where you are pointing,
# not wherever the caret happened to be.
CLICK_BEFORE_PASTE = True

# After a drag, wait this long to see if the app copied the selection by itself
# (Claude Code and some terminals do). If it did, we skip sending Ctrl+C, because
# Ctrl+C with nothing selected in a terminal means "interrupt", not "copy".
AUTO_COPY_WAIT_S = 0.15
