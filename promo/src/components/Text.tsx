import {useCurrentFrame} from 'remotion';
import {FONT, enter, popScale} from '../theme';
import {useTheme} from '../themes';

/** A headline whose letters pop in one by one, 45 ms apart. */
export const PopHeadline: React.FC<{text: string; at: number; size: number; color?: string; style?: React.CSSProperties}> = ({
  text,
  at,
  size,
  color,
  style,
}) => {
  const frame = useCurrentFrame();
  const T = useTheme();
  const step = (45 / 1000) * 30; // 45 ms in frames
  return (
    <div style={{fontFamily: FONT.head, fontSize: size, color: color ?? T.ink, lineHeight: 1.15, textAlign: 'center', ...style}}>
      {text.split(' ').map((word, w, words) => {
        const offset = words.slice(0, w).join(' ').length + (w ? 1 : 0);
        return (
          <span key={w} style={{display: 'inline-block', whiteSpace: 'nowrap', marginRight: w < words.length - 1 ? '0.32em' : 0}}>
            {word.split('').map((ch, i) => (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  transform: `scale(${popScale(frame, at + (offset + i) * step)})`,
                  transformOrigin: '50% 70%',
                }}
              >
                {ch}
              </span>
            ))}
          </span>
        );
      })}
    </div>
  );
};

/** A centred caption that rises softly into place. */
export const Caption: React.FC<{
  text: string;
  at: number;
  until?: number;
  y: number;
  width: number;
  dot?: string;
  size?: number;
}> = ({text, at, until = Infinity, y, width, dot, size = 54}) => {
  const frame = useCurrentFrame();
  const T = useTheme();
  const inP = enter(frame, at, 14);
  const outP = Number.isFinite(until) ? enter(frame, until, 8) : 0;
  const p = inP * (1 - outP);
  if (p <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 80,
        width: width - 160,
        top: y,
        transform: `translateY(calc(-50% + ${(1 - inP) * 24 - outP * 16}px))`,
        opacity: p,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 22,
        fontFamily: FONT.body,
        fontWeight: 700,
        fontSize: size,
        lineHeight: 1.2,
        color: T.ink,
        textAlign: 'center',
        textWrap: 'balance',
      }}
    >
      {dot && (
        <div
          style={{
            width: 24,
            height: 24,
            flex: 'none',
            borderRadius: 12,
            background: dot,
            boxShadow: T.dark ? `0 0 18px ${dot}` : `0 0 0 2px ${T.ink}22`,
          }}
        />
      )}
      <div>{text}</div>
    </div>
  );
};

/** A mono pill, e.g. `pip install kopi-kopi`. */
export const Pill: React.FC<{text: string; size?: number; style?: React.CSSProperties}> = ({text, size = 40, style}) => {
  const T = useTheme();
  return (
    <div
      style={{
        display: 'inline-block',
        fontFamily: FONT.mono,
        fontWeight: 500,
        fontSize: size,
        color: T.ink,
        background: T.pinkTint,
        border: `2px solid ${T.line}`,
        borderRadius: 999,
        padding: `${size * 0.22}px ${size * 0.7}px`,
        whiteSpace: 'nowrap',
        ...style,
      }}
    >
      {text}
    </div>
  );
};
