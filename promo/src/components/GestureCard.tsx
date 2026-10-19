import {FONT, kf, pop, soft} from '../theme';
import {useTheme} from '../themes';
import {GESTURE} from '../constants';

// The input, shown on its own: a trackpad with three fingertip pads, "or", and a mouse.
// Drawn at full size (about 650 x 300); the demo shows it small with a CSS scale.
export const CARD_W = 652;
export const CARD_H = 296;

// index, middle, ring: a gentle arc, the middle one a little higher, each turned a few degrees
const PADS = [
  {x: 128, y: 126, rot: -9},
  {x: 180, y: 108, rot: 0},
  {x: 232, y: 124, rot: 8},
];

// A mouse silhouette in a 120 x 190 box: rounded body, the split between the buttons, a pill wheel.
const BODY = 'M60 4 C 97 4, 116 30, 116 72 L 116 128 C 116 165, 92 186, 60 186 C 28 186, 4 165, 4 128 L 4 72 C 4 30, 23 4, 60 4 Z';
const BUTTONS = 'M4 76 C 30 84, 90 84, 116 76';

/**
 * `t` is frames since the press started (negative = not yet).
 * The pads come down with the spring curve, lift with the soft curve; a ripple spreads under them;
 * `wheelDelay` frames later the mouse wheel fills with `color` and pulses once.
 */
export const GestureCard: React.FC<{t: number; color: string; wheelDelay: number}> = ({t, color, wheelDelay}) => {
  const T = useTheme();
  const {down, up} = GESTURE;
  const pressing = t < down;
  const y = pressing ? kf(t, [0, down], [-10, 0], pop) : kf(t, [down, up], [0, -10], soft);
  const s = pressing ? kf(t, [0, down], [1.04, 0.96], pop) : kf(t, [down, up], [0.96, 1.04], soft);

  const rt = t - 3; // the ripple starts as the pads touch
  const ripR = kf(rt, [0, 22], [40, 190]);
  const ripA = rt < 0 ? 0 : kf(rt, [0, 3, 22], [0, 1, 0]);

  const wt = t - wheelDelay;
  const wheelFill = kf(wt, [0, 4], [0, 1]);
  const wheelPulse = kf(wt, [0, 5, 12], [1, 1.3, 1]);

  return (
    <div
      aria-hidden
      style={{
        width: CARD_W,
        height: CARD_H,
        boxSizing: 'border-box',
        padding: 28,
        display: 'flex',
        alignItems: 'center',
        gap: 36,
        background: T.surface,
        border: `2px solid ${T.line}`,
        borderRadius: 32,
        boxShadow: T.shadowWindow,
      }}
    >
      {/* trackpad */}
      <div
        style={{
          position: 'relative',
          width: 360,
          height: 240,
          flex: 'none',
          borderRadius: 24,
          border: `2px solid ${T.line}`,
          background: T.surface,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: 180 - ripR,
            top: 118 - ripR * 0.62,
            width: 2 * ripR,
            height: 2 * ripR * 0.62,
            borderRadius: '50%',
            border: `5px solid ${color}`,
            opacity: ripA,
          }}
        />
        {PADS.map((p, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: p.x - 22,
              top: p.y - 28,
              width: 44,
              height: 56,
              borderRadius: '50%',
              background: T.pad.fill,
              boxShadow: T.pad.shadow,
              transform: `translateY(${y}px) rotate(${p.rot}deg) scale(${s})`,
            }}
          />
        ))}
      </div>

      <div style={{fontFamily: FONT.mono, fontSize: 30, letterSpacing: '0.12em', textTransform: 'uppercase', color: T.ink3}}>or</div>

      {/* mouse */}
      <svg width={120} height={190} viewBox="0 0 120 190" style={{flex: 'none', overflow: 'visible'}}>
        <path d={BODY} fill={T.surface} stroke={T.ink2} strokeWidth={2.4} />
        <path d={BUTTONS} fill="none" stroke={T.ink2} strokeWidth={2.4} />
        <line x1="60" y1="4" x2="60" y2="80" stroke={T.ink2} strokeWidth={2.4} />
        <g transform={`translate(60 40) scale(${wheelPulse}) translate(-60 -40)`}>
          <rect x="52" y="22" width="16" height="36" rx="8" fill={T.surface} stroke={T.ink2} strokeWidth={2.4} />
          <rect
            x="52"
            y="22"
            width="16"
            height="36"
            rx="8"
            fill={color}
            stroke={T.ink2}
            strokeWidth={2.4}
            opacity={wheelFill}
            style={{filter: T.dark ? `drop-shadow(0 0 8px ${color})` : undefined}}
          />
        </g>
      </svg>
    </div>
  );
};
