import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {COPY, SETUP} from '../constants';
import {FONT, kf, pop} from '../theme';
import {Theme, useTheme} from '../themes';
import {Pill, PopHeadline} from '../components/Text';
import {SHAPES, Shapes} from '../components/Shapes';

// Small drawings for each card.
const Icon: React.FC<{i: number; size: number; T: Theme}> = ({i, size, T}) => {
  const f = useCurrentFrame();
  if (i === 0)
    return (
      <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden>
        <rect x="8" y="18" width="84" height="64" rx="12" fill="none" stroke={T.ink2} strokeWidth="4" />
        {[30, 50, 70].map((cx) => (
          <circle key={cx} cx={cx} cy={50} r="7" fill={T.yellow} stroke={T.dark ? 'none' : T.ink2} strokeWidth="2" />
        ))}
      </svg>
    );
  if (i === 1)
    return (
      <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden>
        <path d="M50 14 V62 M30 44 L50 64 L70 44" fill="none" stroke={T.dark ? T.pink : T.ink2} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M18 70 V84 H82 V70" fill="none" stroke={T.ink2} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  const k = String(f % 48).padStart(2, '0');
  return <Img src={staticFile(`cursor-frames/copied-arrow/${k}.png`)} style={{width: size, height: size}} />;
};

/** Text with "→" drawn as a small arrow, and each word kept whole (kopi-kopi never breaks at its hyphen). */
const Words: React.FC<{text: string; color: string}> = ({text, color}) => (
  <>
    {text.split(' ').map((w, k) => [
      k ? ' ' : null, // the space sits between spans, so lines can break there
      <span key={k} style={{whiteSpace: 'nowrap'}}>
        {w === '→' ? (
          <svg width="0.9em" height="0.6em" viewBox="0 0 30 20" style={{verticalAlign: 'middle'}} aria-label="to">
            <path d="M2 10 H26 M18 3 L26 10 L18 17" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : (
          w
        )}
      </span>,
    ])}
  </>
);

// 19-23.5 s: three setup cards pop in, tilted and lifted, then settle flat.
export const Setup: React.FC = () => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width} = useVideoConfig();
  const wide = width > 1080;
  const accents = [T.yellow, T.pink, T.green];

  return (
    <AbsoluteFill>
      <Shapes items={SHAPES.setup} />
      <AbsoluteFill style={{padding: 80, alignItems: 'center'}}>
        <PopHeadline text={COPY.setupTitle} at={SETUP.title} size={88} style={{marginTop: wide ? 20 : 0}} />
        <div
          style={{
            marginTop: wide ? 56 : 40,
            display: 'flex',
            flexDirection: wide ? 'row' : 'column',
            gap: wide ? 40 : 26,
            width: '100%',
          }}
        >
          {COPY.setup.map((card, i) => {
            const at = SETUP.firstCard + i * SETUP.gap;
            const land = at + 12;
            const s = kf(f, [at, land], [0.85, 1], pop);
            const o = kf(f, [at, at + 4], [0, 1]);
            const lift = 1 - kf(f, [land, land + SETUP.settle], [0, 1]); // 1 = lifted, 0 = flat
            return (
              <div
                key={i}
                style={{
                  flex: wide ? '1 1 0' : 'none',
                  minWidth: 0, // let flex items shrink below their text's width
                  position: 'relative',
                  transform: `scale(${s}) rotate(${-0.6 * lift}deg)`,
                  opacity: o,
                }}
              >
                {/* the lift shadow fades as the card settles */}
                <div style={{position: 'absolute', inset: 0, borderRadius: 32, boxShadow: T.shadowLift, opacity: lift}} />
                <div
                  style={{
                    position: 'relative',
                    height: '100%',
                    boxSizing: 'border-box',
                    display: 'flex',
                    flexDirection: wide ? 'column' : 'row',
                    alignItems: wide ? 'flex-start' : 'center',
                    gap: wide ? 26 : 28,
                    padding: wide ? '36px 36px 150px' : '26px 30px',
                    background: T.surface,
                    border: `2px solid ${T.line}`,
                    borderRadius: 32,
                    minHeight: wide ? 520 : 0,
                  }}
                >
                  <div
                    style={{
                      width: 88,
                      height: 88,
                      flex: 'none',
                      borderRadius: 44,
                      background: accents[i],
                      color: T.onPastel,
                      fontFamily: FONT.head,
                      fontSize: 46,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {i + 1}
                  </div>
                  <div style={{flex: 1, minWidth: 0}}>
                    {'main' in card && card.main && (
                      <div style={{fontFamily: FONT.body, fontWeight: 700, fontSize: 48, color: T.ink, lineHeight: 1.15}}>
                        <Words text={card.main} color={T.ink} />
                      </div>
                    )}
                    {'pill' in card && card.pill && <Pill text={card.pill} size={wide ? 34 : 38} />}
                    {card.sub && (
                      <div style={{marginTop: 10, fontFamily: FONT.body, fontWeight: 500, fontSize: 44, color: T.ink3, lineHeight: 1.15}}>
                        <Words text={card.sub} color={T.ink3} />
                      </div>
                    )}
                  </div>
                  <div style={{flex: 'none', position: wide ? 'absolute' : 'static', right: 36, bottom: 30}}>
                    <Icon i={i} size={wide ? 110 : 84} T={T} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
