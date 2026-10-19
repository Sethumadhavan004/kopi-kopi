import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {useTheme} from '../themes';

/** A calm star field: small dots that breathe slowly. Ankoku only. */
export const Stars: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useTheme();
  const {width, height} = useVideoConfig();
  if (!T.stars) return null;
  return (
    <AbsoluteFill aria-hidden>
      {Array.from({length: 70}, (_, i) => {
        const r = 1 + random(`r${i}`) * 1.6;
        const base = 0.12 + random(`a${i}`) * 0.3;
        const twinkle = 0.5 + 0.5 * Math.sin(frame / 22 + random(`p${i}`) * 6.28);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: random(`x${i}`) * width,
              top: random(`y${i}`) * height,
              width: 2 * r,
              height: 2 * r,
              borderRadius: r,
              background: i % 9 === 0 ? T.pink : T.ink,
              opacity: base * (0.55 + 0.45 * twinkle),
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
