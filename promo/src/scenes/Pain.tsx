import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COPY, PAIN} from '../constants';
import {enter, kf} from '../theme';
import {useTheme} from '../themes';
import {Rect, layout, rowY, textX, visibleRows} from '../layout';
import {Terminal} from '../components/Terminal';
import {Cursor} from '../components/Cursor';
import {Caption} from '../components/Text';
import {SHAPES, Shapes} from '../components/Shapes';

const START_ROW = 2;

/** Where the cursor tip is at frame f: drag to the edge, tremble there, then slip away. */
export const painCursor = (f: number, t: Rect) => {
  const rows = visibleRows(t);
  const x0 = textX(t) + 6;
  const dragY = kf(f, [PAIN.press, PAIN.reachEdge], [rowY(t, START_ROW), rowY(t, rows - 1) + 14]);
  const tremble = f > PAIN.reachEdge && f < PAIN.slip ? 1 : 0;
  const slip = kf(f, [PAIN.slip, PAIN.slip + 8], [0, 1]);
  return {
    x: kf(f, [PAIN.press, PAIN.reachEdge], [x0, x0 + 300]) + tremble * Math.sin(f * 1.9) * 6 + slip * 120,
    y: dragY + tremble * Math.sin(f * 2.7) * 5 - slip * 150,
    dragY,
  };
};

// 0-4 s: dragging a selection across a long log, and losing it.
export const Pain: React.FC = () => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width, height} = useVideoConfig();
  const L = layout(width, height);
  const t = L.painTerm;

  // auto-scroll once the drag reaches the bottom edge, getting faster
  const scroll = kf(f, [PAIN.reachEdge, PAIN.slip], [0, PAIN.scrollLines], (x) => x * x);
  const {x, y, dragY} = painCursor(f, t);
  const slipped = f >= PAIN.slip;
  const cursorLine = scroll + (dragY - rowY(t, 0)) / (rowY(t, 1) - rowY(t, 0));
  const a = T.dragSelect.alpha;
  const flicker = f >= PAIN.slip && f < PAIN.slip + 6 ? (f % 2 ? a * 0.25 : a) : slipped ? 0 : a;

  return (
    <AbsoluteFill>
      <Shapes items={SHAPES.pain} />
      <Terminal
        rect={t}
        scroll={scroll}
        title={COPY.terminalTitle}
        opacity={enter(f, 0, 10)}
        dy={(1 - enter(f, 0, 16)) * 30}
        selection={
          f >= PAIN.press
            ? {from: START_ROW, to: Math.floor(cursorLine), color: T.dragSelect.color, alpha: flicker}
            : undefined
        }
      />
      <Cursor x={x} y={y} look="plain" opacity={enter(f, 2, 8)} />
      <Caption text={COPY.pain} at={PAIN.caption} y={L.painCaptionY} width={width} size={58} />
    </AbsoluteFill>
  );
};
