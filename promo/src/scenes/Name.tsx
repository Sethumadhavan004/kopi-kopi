import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COPY, NAME, SCENES} from '../constants';
import {FONT, enter, kf} from '../theme';
import {useTheme} from '../themes';
import {PopHeadline} from '../components/Text';
import {INFINITY, SHAPES, Shapes} from '../components/Shapes';

// 4-7 s: the name, letter by letter, over a red infinity that draws itself.
export const Name: React.FC = () => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width} = useVideoConfig();
  const wide = width > 1080;
  const tag = enter(f, NAME.tagline, 16);
  const fade = 1 - enter(f, SCENES.name.dur - 8, 8);
  // pathLength=1 lets the dash maths work in 0..1 instead of real path length
  const drawn = kf(f, NAME.infinity, [0, 1]);
  const infW = wide ? 1100 : 900;
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: fade}}>
      <Shapes items={SHAPES.name} />
      {T.dark && (
        <div
          style={{
            position: 'absolute',
            width: 900,
            height: 900,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${T.cursor.glow} 0%, transparent 60%)`,
            opacity: enter(f, 0, 30),
          }}
        />
      )}
      {/* the one red moment on this screen */}
      <svg aria-hidden width={infW} height={infW / 2} viewBox="0 0 120 60" style={{position: 'absolute', overflow: 'visible'}}>
        <path
          d={INFINITY}
          fill="none"
          stroke={T.red}
          strokeWidth={1.6}
          strokeLinecap="round"
          strokeLinejoin="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - drawn}
          opacity={T.dark ? 0.85 : 0.9}
        />
      </svg>
      <PopHeadline text={COPY.name} at={NAME.title} size={wide ? 170 : 132} />
      <div
        style={{
          position: 'absolute',
          top: `calc(50% + ${wide ? 190 : 160}px)`,
          fontFamily: FONT.body,
          fontWeight: 700,
          fontSize: 56,
          color: T.ink2,
          opacity: tag,
          transform: `translateY(${(1 - tag) * 20}px)`,
        }}
      >
        {COPY.tagline}
      </div>
    </AbsoluteFill>
  );
};
