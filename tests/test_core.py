from kopi_kopi.core import Action, KopiKopi, State


def make():
    return KopiKopi(drag_threshold_px=6)


def test_left_clicks_pass_through_when_off():
    k = make()
    assert not k.left_down(10, 10).suppress
    assert not k.left_up(10, 10).suppress
    assert k.state == State.OFF


def test_trigger_turns_on_and_is_swallowed():
    k = make()
    r = k.trigger_down()
    assert r.suppress and r.actions == []
    assert k.trigger_up().suppress
    assert k.state == State.ARMED and k.look == "armed"


def test_tap_start_then_tap_end_copies_with_shift_click():
    k = make()
    k.trigger_down()
    # start tap reaches the app untouched (places the caret)
    assert not k.left_down(10, 10).suppress
    assert not k.left_up(10, 10).suppress
    assert k.state == State.HAS_START
    # end tap is swallowed and replayed as shift+click
    assert k.left_down(300, 900).suppress
    r = k.left_up(300, 900)
    assert r.suppress and r.actions == [Action.SHIFT_CLICK_COPY]
    assert k.state == State.COPIED


def test_drag_copies_without_swallowing():
    k = make()
    k.trigger_down()
    assert not k.left_down(10, 10).suppress
    r = k.left_up(200, 40)
    assert not r.suppress and r.actions == [Action.COPY_AFTER_DRAG]
    assert k.state == State.COPIED


def test_tiny_jitter_is_still_a_tap():
    k = make()
    k.trigger_down()
    k.left_down(10, 10)
    k.left_up(13, 12)
    assert k.state == State.HAS_START


def test_trigger_after_copy_pastes_and_turns_off():
    k = make()
    k.trigger_down()
    k.left_down(0, 0)
    k.left_up(100, 0)
    r = k.trigger_down()
    assert r.suppress and r.actions == [Action.PASTE]
    assert k.state == State.OFF and k.look is None


def test_clicks_after_copy_pass_through_so_you_can_focus_the_target():
    k = make()
    k.trigger_down()
    k.left_down(0, 0)
    k.left_up(100, 0)
    assert not k.left_down(5, 5).suppress
    assert not k.left_up(5, 5).suppress
    assert k.state == State.COPIED


def test_trigger_cancels_while_selecting():
    for taps in (0, 1):
        k = make()
        k.trigger_down()
        for _ in range(taps):
            k.left_down(1, 1)
            k.left_up(1, 1)
        r = k.trigger_down()
        assert r.actions == []
        assert k.state == State.OFF


def test_release_after_cancel_mid_press_is_still_swallowed():
    # Press for the end point, cancel with the trigger before releasing:
    # the release must still be swallowed so the app never sees half a click.
    k = make()
    k.trigger_down()
    k.left_down(1, 1)
    k.left_up(1, 1)
    assert k.left_down(50, 50).suppress
    k.trigger_down()
    assert k.left_up(50, 50).suppress
    assert k.state == State.OFF


def test_press_that_started_before_turning_on_is_ignored():
    k = make()
    k.left_down(1, 1)
    k.trigger_down()
    r = k.left_up(500, 500)
    assert not r.suppress and r.actions == []
    assert k.state == State.ARMED


def test_cursor_look_follows_each_step():
    k = make()
    looks = [k.look]
    k.trigger_down()
    looks.append(k.look)
    k.left_down(1, 1)
    k.left_up(1, 1)
    looks.append(k.look)
    k.left_down(90, 90)
    k.left_up(90, 90)
    looks.append(k.look)
    assert looks == [None, "armed", "selecting", "copied"]


def test_failed_copy_goes_back_to_armed_so_you_can_retry():
    k = make()
    k.trigger_down()
    k.left_down(0, 0)
    k.left_up(100, 0)
    k.copy_failed()
    assert k.state == State.ARMED
    # a fresh drag works as usual
    k.left_down(0, 0)
    k.left_up(100, 0)
    assert k.state == State.COPIED


def test_late_copy_failure_after_paste_trigger_changes_nothing():
    k = make()
    k.trigger_down()
    k.left_down(0, 0)
    k.left_up(100, 0)
    k.trigger_down()  # paste requested before the copy check finished
    k.copy_failed()
    assert k.state == State.OFF


def test_heartbeat_starts_the_moment_you_press():
    k = make()
    k.trigger_down()
    k.left_down(10, 10)
    assert k.look == "selecting"      # mid-drag (or start tap): already pulsing
    k.left_up(300, 10)
    assert k.look == "copied"         # drag finished: calm again


def test_pressing_while_off_or_copied_changes_nothing():
    k = make()
    k.left_down(1, 1)
    assert k.look is None
    k.left_up(1, 1)
    k.trigger_down()
    k.left_down(0, 0)
    k.left_up(100, 0)
    k.left_down(5, 5)                 # clicking to focus the paste target
    assert k.look == "copied"
