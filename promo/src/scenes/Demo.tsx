import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COPY, DEMO as D, GESTURE} from '../constants';
import {FONT, Look, enter, expoOut, kf, pop, starColor} from '../theme';
import {useTheme} from '../themes';
import {TERM, layout, rowY, textX} from '../layout';
import {LOG, lineText} from '../logs';
import {Terminal} from '../components/Terminal';
import {Cursor} from '../components/Cursor';
import {Ripple} from '../components/Taps';
import {CARD_H, CARD_W, GestureCard} from '../components/GestureCard';
import {Caption} from '../components/Text';
import {SHAPES, Shapes} from '../components/Shapes';

type P = {x: number; y: number};

/** The four points the cursor visits, from the layout. */
export const demoPoints = (width: number, height: number) => {
  const {term: t, input: inp, wide} = layout(width, height);
  const endText = lineText(LOG[D.scrollLines + D.endRow]);
  return {
    rest: {x: t.x + t.w * 0.62, y: t.y + t.h * 0.42},
    start: {x: textX(t) + 4, y: rowY(t, D.startRow)},
    end: {x: textX(t) + endText.length * TERM.charW, y: rowY(t, D.endRow)},
    // below the pasted line and its chip, so nothing covers what was pasted
    target: {x: inp.x + inp.w * (wide ? 0.5 : 0.66), y: inp.y + inp.h * 0.84},
  };
};

/** Where the cursor tip is at frame f. */
export const demoCursor = (f: number, width: number, height: number): P => {
  const {rest, start, end, target} = demoPoints(width, height);
  const seg = (a: P, b: P, [s, e]: number[]) => ({x: kf(f, [s, e], [a.x, b.x]), y: kf(f, [s, e], [a.y, b.y])});
  return f < D.moveToStart[1] ? seg(rest, start, D.moveToStart) : f < D.moveToEnd[1] ? seg(start, end, D.moveToEnd) : seg(end, target, D.moveToInput);
};

// 7-19 s: one continuous shot of kopi-kopi doing the job.
export const Demo: React.FC = () => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width, height} = useVideoConfig();
  const L = layout(width, height);
  const t = L.term;
  const inp = L.input;
  const {rest, start, end, target} = demoPoints(width, height);

  const startLine = D.startRow; // log line tapped first (scroll is 0 then)
  const endLine = D.scrollLines + D.endRow;
  const lines = endLine - startLine + 1;

  const pos = demoCursor(f, width, height);
  const look: Look =
    f >= D.pasted ? 'plain' : f >= D.copied ? 'copied' : f >= D.tapStart ? 'selecting' : f >= D.armed ? 'armed' : 'plain';

  // --- the log ---
  const scroll = kf(f, D.scroll, [0, D.scrollLines]);
  const sweep = kf(f, [D.tapEnd, D.tapEnd + 10], [0, 1]);

  // --- the camera: a gentle push toward each tap, easing back between steps ---
  const taps: [number, P][] = [
    [D.trigger1, rest],
    [D.tapStart, start],
    [D.tapEnd, end],
    [D.trigger2, target],
  ];
  const {push} = D;
  const bumps = taps.map(([at, p]) => ({p, k: kf(f, [at, at + push.in, at + push.in + push.hold, at + push.in + push.hold + push.out], [0, 1, 1, 0])}));
  const active = bumps.reduce((a, b) => (b.k > a.k ? b : a));
  const camScale = 1 + (push.scale - 1) * active.k;

  // --- the paste: a small squish, and the chip counting up ---
  const squish = kf(f, [D.pasted, D.pasted + 4], [0.95, 1], pop);
  const pasteIn = enter(f, D.pasted, 4);
  const count = Math.round(kf(f, [D.pasted + 4, D.pasted + 4 + D.countUp], [0, lines - 1], expoOut));
  const chipIn = count > 0 ? 1 : 0; // the chip appears at its first non-zero value

  // --- the input lives in a small gesture card, bottom-left; only the effect happens at the cursor ---
  const corner = (at: number, landed: number) => {
    const sIn = enter(f, at - GESTURE.slideIn - 2, GESTURE.slideIn);
    const sOut = enter(f, landed + GESTURE.outAfter, GESTURE.slideIn);
    return (1 - sIn) + sOut; // 0 = in place, 1 = off to the left
  };
  const cornerOff = Math.min(corner(D.trigger1, D.armed), corner(D.trigger2, D.pasted));
  const cardT = f < (D.trigger1 + D.trigger2) / 2 ? f - D.trigger1 : f - D.trigger2;
  const cardColor = f < (D.trigger1 + D.trigger2) / 2 ? T.yellow : T.green;
  const cs = GESTURE.cornerScale;

  const inT = enter(f, 0, 16);
  const inputIn = enter(f, D.moveToInput[0] - 14, 18);

  const stepAt = [D.trigger1, D.tapStart, D.tapEnd, D.trigger2];
  const stepDot = [T.yellow, T.pink, T.green, T.ink];

  return (
    <AbsoluteFill>
      <Shapes items={SHAPES.demo} />
      <AbsoluteFill style={{transform: `scale(${camScale})`, transformOrigin: `${active.p.x}px ${active.p.y}px`}}>
        <Terminal
          rect={t}
          scroll={scroll}
          title={COPY.terminalTitle}
          opacity={inT}
          dy={(1 - inT) * 30}
          caret={{line: startLine, color: T.pink, alpha: f >= D.tapStart && f < D.tapEnd + 6 ? 0.5 + 0.5 * Math.sin(f / 3) ** 2 : 0}}
          selection={{
            from: startLine,
            to: startLine + (endLine - startLine) * sweep,
            color: T.greenTint,
            alpha: sweep,
            text: T.greenText,
          }}
          rangeMark={{
            from: startLine,
            to: f >= D.tapEnd ? endLine : startLine,
            color: f >= D.tapEnd ? T.green : T.pink,
            alpha: f >= D.tapStart ? 1 : 0,
          }}
        />

        {/* the Claude Code input box; its red border after the paste is this screen's one red moment */}
        <div
          style={{
            position: 'absolute',
            left: inp.x,
            top: inp.y + (1 - inputIn) * 30,
            width: inp.w,
            height: inp.h,
            opacity: inputIn,
            background: T.surface,
            border: `2px solid ${f >= D.pasted ? T.red : T.line}`,
            borderRadius: 24,
            padding: '22px 28px',
            boxSizing: 'border-box',
            boxShadow: f >= D.pasted ? `0 0 36px ${T.red}33` : T.shadowWindow,
          }}
        >
          <div style={{fontFamily: FONT.mono, fontSize: 20, letterSpacing: '0.12em', textTransform: 'uppercase', color: T.ink3}}>
            {COPY.inputLabel}
          </div>
          <div style={{display: 'flex', gap: 16, marginTop: 14, fontFamily: FONT.mono, fontSize: 26, color: T.ink, alignItems: 'flex-start'}}>
            <span style={{color: T.ink3}}>&gt;</span>
            {f < D.pasted ? (
              <span style={{width: 12, height: 32, background: T.ink, opacity: Math.floor(f / 15) % 2 ? 0 : 0.8}} />
            ) : (
              <div style={{opacity: pasteIn, transform: `scale(${squish})`, transformOrigin: '0 50%', minWidth: 0}}>
                <div style={{whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: inp.w - 110, color: T.ink2}}>
                  {lineText(LOG[startLine])}
                </div>
                <div
                  style={{
                    opacity: chipIn,
                    display: 'inline-block',
                    marginTop: 10,
                    padding: '4px 16px',
                    borderRadius: 999,
                    background: T.green,
                    color: T.onPastel,
                    fontSize: 26,
                    fontWeight: 500,
                  }}
                >
                  +{count} lines
                </div>
              </div>
            )}
          </div>
        </div>

        <Ripple x={rest.x} y={rest.y} at={D.trigger1 + 3} color={starColor(T, 'armed')} />
        <Ripple x={start.x} y={start.y} at={D.tapStart} color={starColor(T, 'selecting')} />
        <Ripple x={end.x} y={end.y} at={D.tapEnd} color={starColor(T, 'copied')} />
        <Ripple x={target.x} y={target.y} at={D.trigger2 + 3} color={starColor(T, 'copied')} />

        <Cursor x={pos.x} y={pos.y} look={look} opacity={enter(f, 4, 10)} />
      </AbsoluteFill>

      {cornerOff < 1 && (
        <div
          style={{
            position: 'absolute',
            left: L.corner.x - cornerOff * (CARD_W * cs + L.corner.x + 20),
            top: L.corner.y,
            width: CARD_W * cs,
            height: CARD_H * cs,
          }}
        >
          <div style={{transform: `scale(${cs})`, transformOrigin: '0 0'}}>
            <GestureCard t={cardT} color={cardColor} wheelDelay={GESTURE.cornerWheelDelay} />
          </div>
        </div>
      )}

      {COPY.steps.map((s, i) => (
        <Caption key={i} text={s} at={stepAt[i]} until={stepAt[i + 1] ?? Infinity} y={L.captionY} width={width} dot={stepDot[i]} />
      ))}
    </AbsoluteFill>
  );
};
