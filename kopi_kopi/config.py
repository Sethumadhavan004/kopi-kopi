"""Settings you might want to tweak. Everything else reads from here."""

# Cursor colour while kopi-kopi is ON (R, G, B).
# A deeper take on Claude Code's blue, so it stands out on any background.
# (87, 105, 247) is closer to the original but reads lighter.
KOPI_BLUE = (52, 78, 240)

# kopi-kopi cursor size relative to your normal cursor. Bigger = easier to notice.
CURSOR_SCALE = 1.5

# Outline between the blue and the dark edge, so it stays visible on any background.
OUTLINE = (255, 255, 255)

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
