import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {kf} from '../theme';
import {Hue, tintOf, useTheme} from '../themes';
import {WIPE} from '../constants';

/**
 * The Sun-disc transition. Before `at`, a disc grows from (x, y) until it covers the frame;
 * after `at`, a hole opens from the same point and reveals the next scene.
 */
export const Wipe: React.FC<{at: number; x: number; y: number; hue: Hue}> = ({at, x, y, hue}) => {
  const f = useCurrentFrame();
  const T = useTheme();
  const {width, height} = useVideoConfig();
  const t = f - at;
  if (t < -WIPE.cover || t > WIPE.reveal) return null;
  // far enough to cover the furthest corner from the origin
  const R = Math.hypot(Math.max(x, width - x), Math.max(y, height - y)) + 20;
  const color = T.wipeTint ? tintOf(T, hue) : T[hue];
  if (t < 0) {
    const r = kf(t, [-WIPE.cover, 0], [0, R]);
    return (
      <AbsoluteFill aria-hidden>
        <div style={{position: 'absolute', left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: '50%', background: color}} />
      </AbsoluteFill>
    );
  }
  const hole = kf(t, [0, WIPE.reveal], [0, R]);
  const mask = `radial-gradient(circle at ${x}px ${y}px, transparent ${hole}px, black ${hole + 1}px)`;
  return <AbsoluteFill aria-hidden style={{background: color, WebkitMaskImage: mask, maskImage: mask}} />;
};
